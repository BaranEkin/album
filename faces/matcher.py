from __future__ import annotations

import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

import numpy as np
from PIL import Image
from deepface import DeepFace
from deepface.commons.logger import Logger as DeepFaceLogger

from faces.config import load_recognition_config
from faces.crops import crop_face
from faces.identity import load_identity_map
from faces.paths import FACE_RECOGNITION_DIR, IDENTITY_MAP_PATH


@contextmanager
def _quiet_deepface_info() -> Iterator[None]:
    df_logger = DeepFaceLogger()
    previous = df_logger.log_level
    df_logger.log_level = max(previous, logging.WARNING)
    try:
        yield
    finally:
        df_logger.log_level = previous


class FaceMatcher:
    def __init__(
        self,
        db_path: Path = FACE_RECOGNITION_DIR,
        identity_map_path: Path = IDENTITY_MAP_PATH,
        config: dict[str, Any] | None = None,
    ):
        self.db_path = Path(db_path)
        self.settings = config or load_recognition_config()
        self.identity_map = load_identity_map(identity_map_path)
        self._folder_by_name = {
            meta["display_name"]: folder
            for folder, meta in self.identity_map.items()
            if meta.get("display_name")
        }
        self.known_names = set(self._folder_by_name)
        self._db_ready = False

    def warm_database(self, force_refresh: bool = False, silent: bool = False) -> None:
        if self._db_ready and not force_refresh:
            return
        probe = next(self.db_path.rglob("*.jpg"), None)
        if probe is None:
            probe = next(self.db_path.rglob("*.jpeg"), None)
        if probe is None:
            raise FileNotFoundError(f"No gallery images under {self.db_path}")
        DeepFace.find(
            img_path=str(probe),
            db_path=str(self.db_path),
            model_name=self.settings["model_name"],
            distance_metric=self.settings["distance_metric"],
            enforce_detection=False,
            detector_backend=self.settings.get("find_detector_backend", "skip"),
            align=bool(self.settings.get("align_recognition", True)),
            threshold=self.settings.get("distance_threshold"),
            silent=silent,
            refresh_database=True,
        )
        self._db_ready = True

    def find_for_crop(
        self, crop_rgb: Image.Image, allowed_names: set[str]
    ) -> list[tuple[str, float, str, str]]:
        bgr = np.array(crop_rgb.convert("RGB"))[:, :, ::-1]
        with _quiet_deepface_info():
            dfs = DeepFace.find(
                img_path=bgr,
                db_path=str(self.db_path),
                model_name=self.settings["model_name"],
                distance_metric=self.settings["distance_metric"],
                enforce_detection=bool(
                    self.settings.get("enforce_detection_on_crop", False)
                ),
                detector_backend=self.settings.get("find_detector_backend", "skip"),
                align=bool(self.settings.get("align_recognition", True)),
                threshold=self.settings.get("distance_threshold"),
                silent=True,
                refresh_database=False,
            )
        if not dfs:
            return []
        dataframe = dfs[0]
        if dataframe is None or len(dataframe) == 0:
            return []

        hits: list[tuple[str, float, str, str]] = []
        for _, row in dataframe.iterrows():
            identity_path = Path(str(row["identity"]))
            identity_folder = identity_path.parent.name
            meta = self.identity_map.get(identity_folder)
            if meta is None:
                continue
            display_name = meta["display_name"]
            if display_name not in allowed_names:
                continue
            distance = float(row["distance"])
            hits.append((display_name, distance, identity_folder, str(identity_path)))
        hits.sort(key=lambda item: item[1])
        return hits

    def _select_hit(
        self, hits: list[tuple[str, float, str, str]]
    ) -> tuple[str, float, str, str] | None:
        if not hits:
            return None
        margin = self.settings.get("second_best_margin")
        if margin is None or len(hits) < 2:
            return hits[0]
        if hits[1][1] - hits[0][1] >= float(margin):
            return hits[0]
        return None

    def suggest_names_for_detections(
        self,
        image: Image.Image,
        detections: list[list],
    ) -> list[list]:
        if not detections or not self.known_names:
            return detections

        blank_indexes = [
            index for index, det in enumerate(detections) if not (det[4] or "").strip()
        ]
        if not blank_indexes:
            return detections

        pad_ratio = float(self.settings.get("crop_pad_ratio", 0.15))
        candidates: list[tuple[int, str, float]] = []
        for index in blank_indexes:
            box = (
                int(detections[index][0]),
                int(detections[index][1]),
                int(detections[index][2]),
                int(detections[index][3]),
            )
            crop = crop_face(image, box, pad_ratio=pad_ratio)
            try:
                hits = self.find_for_crop(crop, self.known_names)
            finally:
                crop.close()
            best = self._select_hit(hits)
            if best is None:
                continue
            name, distance, _folder, _matched = best
            candidates.append((index, name, distance))

        candidates.sort(key=lambda item: item[2])
        used_indexes: set[int] = set()
        used_names: set[str] = set()
        updated = [list(det) for det in detections]
        for index, name, _distance in candidates:
            if index in used_indexes or name in used_names:
                continue
            used_indexes.add(index)
            used_names.add(name)
            updated[index][4] = name
        return updated
