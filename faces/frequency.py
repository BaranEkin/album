from __future__ import annotations

import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from faces.identity import load_identity_map
from faces.paths import (
    IDENTITY_MAP_PATH,
    PERSON_FREQUENCIES_PATH,
    ensure_face_recognition_dir,
)


def load_person_frequencies(
    path: Path = PERSON_FREQUENCIES_PATH,
) -> dict[str, int]:
    if not path.is_file():
        return {}
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    people = data.get("people") if isinstance(data, dict) else None
    if not isinstance(people, dict):
        return {}
    result: dict[str, int] = {}
    for name, count in people.items():
        if isinstance(name, str) and isinstance(count, (int, float)) and count > 0:
            result[name] = int(count)
    return result


DEFAULT_FREQUENCY_LAST_N = 5000


def save_person_frequencies(
    frequencies: dict[str, int],
    path: Path = PERSON_FREQUENCIES_PATH,
    *,
    source: str = "album_db",
    last_n: int = DEFAULT_FREQUENCY_LAST_N,
    rows_used: int | None = None,
) -> None:
    ensure_face_recognition_dir()
    payload = {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source": source,
        "last_n": last_n,
        "rows_used": rows_used,
        "people": dict(
            sorted(frequencies.items(), key=lambda item: (-item[1], item[0]))
        ),
    }
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)
        file.write("\n")


def count_person_frequencies(
    known_names: set[str],
    *,
    last_n: int = DEFAULT_FREQUENCY_LAST_N,
) -> tuple[dict[str, int], int]:
    from config.config import Config
    from data.data_manager import DataManager
    from data.orm import Media
    from sqlalchemy import select

    Config.read_config()
    counts: Counter[str] = Counter()
    data_manager = DataManager()
    with data_manager.get_session() as session:
        rows = session.execute(
            select(Media.people)
            .where(Media.status != 0)
            .where(Media.type == 1)
            .where(Media.people.isnot(None))
            .where(Media.people != "")
            .order_by(Media.date.desc(), Media.rank.desc())
            .limit(last_n)
        ).all()
    for (people,) in rows:
        for token in str(people).split(","):
            name = token.strip()
            if name in known_names:
                counts[name] += 1
    frequencies = {name: counts.get(name, 0) for name in sorted(known_names)}
    return frequencies, len(rows)


def build_person_frequencies_file(
    identity_map_path: Path = IDENTITY_MAP_PATH,
    output_path: Path = PERSON_FREQUENCIES_PATH,
    *,
    last_n: int = DEFAULT_FREQUENCY_LAST_N,
) -> dict[str, Any]:
    identity_map = load_identity_map(identity_map_path)
    known_names = {
        meta["display_name"]
        for meta in identity_map.values()
        if meta.get("display_name")
    }
    frequencies, rows_used = count_person_frequencies(known_names, last_n=last_n)
    save_person_frequencies(
        frequencies,
        output_path,
        source="album_db_photos_last_n_by_date",
        last_n=last_n,
        rows_used=rows_used,
    )
    return {
        "path": str(output_path),
        "last_n": last_n,
        "rows_used": rows_used,
        "people_counted": len(frequencies),
        "total_occurrences": sum(frequencies.values()),
        "max_count": max(frequencies.values()) if frequencies else 0,
        "min_positive": min((c for c in frequencies.values() if c > 0), default=0),
    }


def frequency_weight(count: int, max_count: int, *, gamma: float = 2.0) -> float:
    if max_count <= 0:
        return 0.5
    count = max(0, int(count))
    raw = math.log1p(count) / math.log1p(max_count)
    return float(raw ** max(gamma, 0.01))


def threshold_for_count(
    count: int,
    max_count: int,
    *,
    threshold_min: float,
    threshold_max: float,
    gamma: float = 2.0,
) -> float:
    weight = frequency_weight(count, max_count, gamma=gamma)
    return float(threshold_min + (threshold_max - threshold_min) * weight)


def gallery_known_names(
    identity_map_path: Path = IDENTITY_MAP_PATH,
) -> set[str]:
    identity_map = load_identity_map(identity_map_path)
    return {
        meta["display_name"]
        for meta in identity_map.values()
        if meta.get("display_name")
    }
