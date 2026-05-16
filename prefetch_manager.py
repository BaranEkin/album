import threading
import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Sequence

from PyQt5.QtCore import QObject, QRunnable, QThreadPool, pyqtSignal

from ops import file_ops
from logger import log


_AWAIT_TIMEOUT_SECONDS = 15.0


@dataclass
class PrefetchResult:
    key: str
    q_image: object
    generation: int
    used_cloud: bool
    skipped: bool


class _ManagerSignals(QObject):
    completed = pyqtSignal(object)


class _PrefetchRunnable(QRunnable):
    def __init__(self, manager: "PrefetchManager", media_key: str, generation: int):
        super().__init__()
        self._manager = manager
        self._media_key = media_key
        self._generation = generation

    def run(self):
        if self._generation != self._manager.generation:
            self._manager._finalize(
                PrefetchResult(self._media_key, None, self._generation, False, True)
            )
            return

        is_local = file_ops.check_file_exists(
            self._manager.media_loader.media_dir, self._media_key
        )
        needs_cloud = not is_local

        if needs_cloud and not self._manager.should_attempt_cloud():
            self._manager._finalize(
                PrefetchResult(self._media_key, None, self._generation, False, True)
            )
            return

        try:
            q_image = self._manager.media_loader._load_image_uncached(self._media_key)
        except Exception as e:
            log(
                "PrefetchManager._PrefetchRunnable.run",
                f"Prefetch failed for '{self._media_key}': {e}",
                level="warning",
            )
            q_image = None

        self._manager._finalize(
            PrefetchResult(
                self._media_key, q_image, self._generation, needs_cloud, False
            )
        )


class PrefetchManager(QObject):
    """Keeps a small LRU of decoded QImages for media around the current index.

    Single-flight: at most one load per key is in progress at a time. If the
    main thread requests a key that is already being prefetched, it can wait
    on the existing load via ``await_pending`` instead of starting a duplicate.

    Cache state is guarded by ``_lock`` (a plain ``threading.Lock``) so both the
    GUI thread and worker threads can mutate it safely. UI-side effects (the
    cloud-status callback, debug messages) are dispatched back to the main
    thread via a queued Qt signal so they only ever run on the GUI thread.
    """

    def __init__(
        self,
        media_loader,
        on_cloud_status_change: Optional[Callable[[bool], None]] = None,
        lookahead: int = 10,
        lookbehind: int = 10,
        workers: int = 4,
        failure_threshold: int = 3,
        backoff_seconds: float = 30.0,
        parent: Optional[QObject] = None,
    ):
        super().__init__(parent)
        self.media_loader = media_loader
        self._on_cloud_status_change = on_cloud_status_change
        self._lookahead = lookahead
        self._lookbehind = lookbehind
        self._capacity = lookahead + lookbehind + 1
        self._failure_threshold = failure_threshold
        self._backoff_seconds = backoff_seconds

        self._pool = QThreadPool()
        self._pool.setMaxThreadCount(workers)

        self._signals = _ManagerSignals()
        self._signals.completed.connect(self._on_completed_ui)

        self._lock = threading.Lock()
        self._media_data: Sequence = ()
        self._cache: "OrderedDict[str, object]" = OrderedDict()
        self._pending: Dict[str, threading.Event] = {}
        self.generation: int = 0

        self._cloud_failure_count: int = 0
        self._cloud_backoff_until: float = 0.0
        self._cloud_reported_off: bool = False

    def set_media_list(self, media_data: Sequence) -> None:
        """Invalidate state and adopt a new ordered media list. Wakes any
        waiters so they can fall through cleanly."""
        with self._lock:
            self.generation += 1
            self._media_data = media_data
            self._cache.clear()
            old_pending = self._pending
            self._pending = {}
        for event in old_pending.values():
            event.set()

    def set_current_index(
        self,
        index: int,
        direction: str = "F",
        hint: Optional[int] = None,
    ) -> None:
        """Recompute the prefetch window around index and schedule missing items."""
        if not self._media_data:
            return

        to_schedule: List[str] = []
        with self._lock:
            gen = self.generation
            current_key = self._key_for(index)
            if current_key is not None and current_key in self._cache:
                self._cache.move_to_end(current_key)
            for idx in self._compute_window(index, direction, hint):
                key = self._key_for(idx)
                if key is None:
                    continue
                if key in self._cache:
                    self._cache.move_to_end(key)
                    continue
                if key in self._pending:
                    continue
                self._pending[key] = threading.Event()
                to_schedule.append(key)

        for key in to_schedule:
            self._pool.start(_PrefetchRunnable(self, key, gen))

    def get(self, media_key: str):
        """Return a cached QImage and bump its LRU recency, or None on miss."""
        with self._lock:
            q_image = self._cache.get(media_key)
            if q_image is not None:
                self._cache.move_to_end(media_key)
            return q_image

    def is_pending(self, media_key: str) -> bool:
        with self._lock:
            return media_key in self._pending

    def insert(self, media_key: str, q_image) -> None:
        """Publish a fully-loaded image into the cache (used by user-facing
        sync loads in MediaLoader so the current item also benefits from the
        cache)."""
        if q_image is None:
            return
        with self._lock:
            self._cache[media_key] = q_image
            self._cache.move_to_end(media_key)
            while len(self._cache) > self._capacity:
                self._cache.popitem(last=False)

    def await_pending(self, media_key: str, timeout: float = _AWAIT_TIMEOUT_SECONDS):
        """If a load for ``media_key`` is already in flight, block until it
        finishes (or ``timeout`` elapses) and return the cached image, else
        return None. Safe to call from the GUI thread; only blocks while the
        existing load is in progress."""
        with self._lock:
            q_image = self._cache.get(media_key)
            if q_image is not None:
                self._cache.move_to_end(media_key)
                return q_image
            event = self._pending.get(media_key)
        if event is None:
            return None
        if not event.wait(timeout):
            return None
        return self.get(media_key)

    def should_attempt_cloud(self) -> bool:
        return time.monotonic() >= self._cloud_backoff_until

    def _finalize(self, result: PrefetchResult) -> None:
        """Worker-thread entry point: insert into cache under lock, wake any
        waiters, then hand off UI side effects to the main thread."""
        with self._lock:
            event = self._pending.pop(result.key, None)
            stale = result.generation != self.generation
            if not stale and not result.skipped and result.q_image is not None:
                self._cache[result.key] = result.q_image
                self._cache.move_to_end(result.key)
                while len(self._cache) > self._capacity:
                    self._cache.popitem(last=False)
        if event is not None:
            event.set()
        if not stale:
            self._signals.completed.emit(result)

    def _on_completed_ui(self, result: PrefetchResult) -> None:
        if result.skipped:
            return
        if result.q_image is None:
            if result.used_cloud:
                self._record_cloud_failure()
            return
        if result.used_cloud:
            self._record_cloud_success()

    def _record_cloud_failure(self) -> None:
        self._cloud_failure_count += 1
        if self._cloud_failure_count < self._failure_threshold:
            return
        self._cloud_backoff_until = time.monotonic() + self._backoff_seconds
        self._cloud_failure_count = 0
        if self._cloud_reported_off:
            return
        self._cloud_reported_off = True
        log(
            "PrefetchManager._record_cloud_failure",
            f"Cloud prefetch disabled for {self._backoff_seconds:.0f}s after repeated failures.",
            level="warning",
        )
        if self._on_cloud_status_change is not None:
            self._on_cloud_status_change(False)

    def _record_cloud_success(self) -> None:
        self._cloud_failure_count = 0
        self._cloud_backoff_until = 0.0
        if not self._cloud_reported_off:
            return
        self._cloud_reported_off = False
        log(
            "PrefetchManager._record_cloud_success",
            "Cloud prefetch re-enabled after successful fetch.",
            level="info",
        )
        if self._on_cloud_status_change is not None:
            self._on_cloud_status_change(True)

    def _is_image(self, idx: int) -> bool:
        if idx < 0 or idx >= len(self._media_data):
            return False
        return getattr(self._media_data[idx], "type", None) == 1

    def _key_for(self, idx: int) -> Optional[str]:
        if idx < 0 or idx >= len(self._media_data):
            return None
        media = self._media_data[idx]
        return f"{media.media_uuid}{media.extension}"

    def _compute_window(
        self, center: int, direction: str, hint: Optional[int]
    ) -> List[int]:
        if direction == "B":
            ahead, behind = self._lookbehind, self._lookahead
        else:
            ahead, behind = self._lookahead, self._lookbehind

        forward: List[int] = []
        j = center + 1
        while len(forward) < ahead and j < len(self._media_data):
            if self._is_image(j):
                forward.append(j)
            j += 1

        backward: List[int] = []
        j = center - 1
        while len(backward) < behind and j >= 0:
            if self._is_image(j):
                backward.append(j)
            j -= 1

        ordered: List[int] = []
        for f, b in zip(forward, backward):
            ordered.append(f)
            ordered.append(b)
        ordered.extend(forward[len(backward) :])
        ordered.extend(backward[len(forward) :])

        if hint is not None and self._is_image(hint) and hint not in ordered:
            ordered.append(hint)

        return ordered
