"""Build res/face_recognition/person_frequencies.json from album people counts."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from faces.frequency import build_person_frequencies_file
from faces.matcher import FaceMatcher


def main() -> int:
    stats = build_person_frequencies_file()
    print(f"Wrote {stats['path']}")
    print(f"last_n={stats['last_n']} rows_used={stats['rows_used']}")
    print(f"people_counted={stats['people_counted']}")
    print(f"total_occurrences={stats['total_occurrences']}")
    print(f"max_count={stats['max_count']} min_positive={stats['min_positive']}")
    matcher = FaceMatcher()
    print("name | count | weight | threshold")
    for row in matcher.frequency_debug_rows():
        print(f"{row['name']} | {row['count']} | {row['weight']} | {row['threshold']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
