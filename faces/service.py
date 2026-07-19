from __future__ import annotations

from typing import Any

from PIL import Image

from faces.config import load_recognition_config
from faces.matcher import FaceMatcher
from faces.paths import (
    FACE_RECOGNITION_DIR,
    IDENTITY_MAP_PATH,
    RECOGNITION_CONFIG_PATH,
)

_matcher: FaceMatcher | None = None
_enabled: bool | None = None


def recognition_available() -> bool:
    if not FACE_RECOGNITION_DIR.is_dir():
        return False
    if not IDENTITY_MAP_PATH.is_file():
        return False
    if not any(FACE_RECOGNITION_DIR.rglob("*.jpg")) and not any(
        FACE_RECOGNITION_DIR.rglob("*.jpeg")
    ):
        return False
    return True


def reset_matcher() -> None:
    global _matcher, _enabled
    _matcher = None
    _enabled = None


def get_matcher(*, force_reload: bool = False) -> FaceMatcher | None:
    global _matcher, _enabled
    if force_reload:
        reset_matcher()
    if _enabled is False:
        return None
    if _matcher is not None:
        return _matcher
    if not recognition_available():
        _enabled = False
        return None
    config = load_recognition_config(RECOGNITION_CONFIG_PATH)
    _matcher = FaceMatcher(
        db_path=FACE_RECOGNITION_DIR,
        identity_map_path=IDENTITY_MAP_PATH,
        config=config,
    )
    _enabled = True
    return _matcher


def is_database_ready() -> bool:
    return _matcher is not None and _matcher._db_ready


def needs_warmup() -> bool:
    if not recognition_available():
        return False
    return not is_database_ready()


def refresh_frequencies() -> bool:
    try:
        from faces.frequency import build_person_frequencies_file

        build_person_frequencies_file()
        return True
    except Exception:
        return False


def warm_recognition() -> None:
    refresh_frequencies()
    reset_matcher()
    matcher = get_matcher(force_reload=True)
    if matcher is None:
        return
    matcher.warm_database(force_refresh=False, silent=True)


def auto_name_detections(
    image: Image.Image,
    detections: list[list[Any]],
) -> list[list[Any]]:
    matcher = get_matcher()
    if matcher is None or not matcher._db_ready:
        return detections
    try:
        return matcher.suggest_names_for_detections(image, detections)
    except Exception:
        return detections
