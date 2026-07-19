from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FACE_RECOGNITION_DIR = REPO_ROOT / "res" / "face_recognition"
VERSION_PATH = FACE_RECOGNITION_DIR / "VERSION"
IDENTITY_MAP_PATH = FACE_RECOGNITION_DIR / "identity_map.json"
RECOGNITION_CONFIG_PATH = FACE_RECOGNITION_DIR / "recognition_config.json"
S3_FACE_RECOGNITION_PREFIX = "face_recognition/"

DEFAULT_CROP_PAD_RATIO = 0.15


def ensure_face_recognition_dir() -> Path:
    FACE_RECOGNITION_DIR.mkdir(parents=True, exist_ok=True)
    return FACE_RECOGNITION_DIR
