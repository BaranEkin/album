import json
import re
from pathlib import Path
from typing import Any

_WINDOWS_FORBIDDEN = '<>:"/\\|?*'
_MULTI_UNDERSCORE = re.compile(r"_+")
_TURKISH_ASCII = str.maketrans(
    {
        "Ç": "C",
        "Ğ": "G",
        "İ": "I",
        "Ö": "O",
        "Ş": "S",
        "Ü": "U",
        "ç": "c",
        "ğ": "g",
        "ı": "i",
        "ö": "o",
        "ş": "s",
        "ü": "u",
    }
)


def slugify_display_name(display_name: str) -> str:
    slug = display_name.strip().translate(_TURKISH_ASCII).replace(" ", "_")
    for char in _WINDOWS_FORBIDDEN:
        slug = slug.replace(char, "")
    slug = "".join(ch if ord(ch) < 128 else "_" for ch in slug)
    slug = _MULTI_UNDERSCORE.sub("_", slug)
    slug = slug.strip("._")
    if not slug:
        raise ValueError(f"Cannot slugify display name: {display_name!r}")
    return slug


def load_identity_map(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError(f"Identity map must be an object: {path}")
    return data


def save_identity_map(path: Path, identity_map: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(identity_map, file, ensure_ascii=False, indent=2)
        file.write("\n")
