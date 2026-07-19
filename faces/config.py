from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from faces.paths import RECOGNITION_CONFIG_PATH, ensure_face_recognition_dir

DEFAULT_SETTINGS: dict[str, Any] = {
    "deepface_version": "0.0.100",
    "detector_backend": "yolov8n",
    "model_name": "Facenet512",
    "distance_metric": "cosine",
    "distance_threshold": 0.4,
    "align_recognition": True,
    "find_detector_backend": "skip",
    "enforce_detection_on_crop": False,
    "min_face_side_px": 40,
    "require_eyes": False,
    "crop_pad_ratio": 0.15,
    "second_best_margin": None,
}


def load_recognition_config(
    path: Path = RECOGNITION_CONFIG_PATH,
) -> dict[str, Any]:
    if not path.is_file():
        return deepcopy(DEFAULT_SETTINGS)
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError(f"Recognition config must be an object: {path}")
    if "distance_threshold" in data:
        settings = deepcopy(DEFAULT_SETTINGS)
        settings.update(data)
        return settings
    if "ongoing" in data and isinstance(data["ongoing"], dict):
        settings = deepcopy(DEFAULT_SETTINGS)
        settings.update(data["ongoing"])
        return settings
    settings = deepcopy(DEFAULT_SETTINGS)
    settings.update(data)
    return settings


def save_recognition_config(
    config: dict[str, Any], path: Path = RECOGNITION_CONFIG_PATH
) -> None:
    ensure_face_recognition_dir()
    with path.open("w", encoding="utf-8") as file:
        json.dump(config, file, ensure_ascii=False, indent=2)
        file.write("\n")


def read_local_version(path: Path | None = None) -> int:
    from faces.paths import VERSION_PATH

    version_path = path or VERSION_PATH
    if not version_path.is_file():
        return 0
    text = version_path.read_text(encoding="utf-8").strip()
    if not text:
        return 0
    return int(text.split()[0])


def write_local_version(version: int, path: Path | None = None) -> None:
    from faces.paths import VERSION_PATH

    version_path = path or VERSION_PATH
    version_path.parent.mkdir(parents=True, exist_ok=True)
    version_path.write_text(f"{int(version)}\n", encoding="utf-8")
