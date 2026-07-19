from __future__ import annotations

import tempfile
from pathlib import Path

from botocore.exceptions import ClientError

from config.config import Config
from faces.config import read_local_version, write_local_version
from faces.paths import (
    FACE_RECOGNITION_DIR,
    S3_FACE_RECOGNITION_PREFIX,
    ensure_face_recognition_dir,
)
from logger import log
from ops import cloud_ops


def _parse_version(text: str) -> int:
    text = text.strip()
    if not text:
        return 0
    return int(text.split()[0])


def fetch_remote_version() -> int | None:
    """Return S3 VERSION as int, or None if missing/unreachable."""
    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = Path(tmp.name)
        try:
            ok = cloud_ops.download_from_s3_bucket(
                f"{S3_FACE_RECOGNITION_PREFIX}VERSION", str(tmp_path)
            )
            if not ok:
                return None
            return _parse_version(tmp_path.read_text(encoding="utf-8"))
        finally:
            tmp_path.unlink(missing_ok=True)
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code", "")
        if code in {"NoSuchKey", "404", "NotFound"}:
            log(
                "faces.sync",
                "No remote face_recognition/VERSION on S3 yet.",
                level="info",
            )
            return None
        log("faces.sync", f"Failed to read remote VERSION: {exc}", level="warning")
        return None
    except Exception as exc:
        log("faces.sync", f"Failed to read remote VERSION: {exc}", level="warning")
        return None


def _list_remote_keys() -> list[str]:
    from ops.cloud_ops import s3

    keys: list[str] = []
    token = None
    while True:
        kwargs = {
            "Bucket": Config.S3_BUCKET_NAME,
            "Prefix": S3_FACE_RECOGNITION_PREFIX,
        }
        if token:
            kwargs["ContinuationToken"] = token
        response = s3.list_objects_v2(**kwargs)
        for item in response.get("Contents") or []:
            key = item["Key"]
            if key.endswith("/"):
                continue
            keys.append(key)
        if not response.get("IsTruncated"):
            break
        token = response.get("NextContinuationToken")
    return keys


def download_gallery_from_s3() -> bool:
    """Overwrite local res/face_recognition/ from S3. Returns True on success."""
    ensure_face_recognition_dir()
    try:
        keys = _list_remote_keys()
    except Exception as exc:
        log("faces.sync", f"Failed listing S3 gallery: {exc}", level="warning")
        return False
    if not keys:
        log("faces.sync", "Remote face_recognition/ is empty.", level="warning")
        return False

    prefix_len = len(S3_FACE_RECOGNITION_PREFIX)
    for key in keys:
        relative = key[prefix_len:]
        if not relative:
            continue
        dest = FACE_RECOGNITION_DIR.joinpath(*relative.split("/"))
        dest.parent.mkdir(parents=True, exist_ok=True)
        ok = cloud_ops.download_from_s3_bucket(key, str(dest))
        if not ok:
            log("faces.sync", f"Failed downloading {key}", level="warning")
            return False
    log(
        "faces.sync",
        f"Downloaded {len(keys)} face_recognition objects from S3.",
        level="info",
    )
    return True


def sync_face_recognition_gallery() -> bool:
    """
    If S3 VERSION is higher than local, download and overwrite local gallery.

    Returns True when local gallery was updated.
    """
    remote = fetch_remote_version()
    if remote is None:
        return False
    local = read_local_version()
    if remote <= local:
        log(
            "faces.sync",
            f"face_recognition up to date (local={local}, remote={remote})",
            level="info",
        )
        return False
    log(
        "faces.sync",
        f"Updating face_recognition local={local} -> remote={remote}",
        level="info",
    )
    if not download_gallery_from_s3():
        return False
    if read_local_version() != remote:
        write_local_version(remote)
    return True
