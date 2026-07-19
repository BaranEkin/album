from __future__ import annotations

from data.helpers import turkish_normalize

FAMILY_ALBUMS: tuple[tuple[str, str], ...] = (
    ("Baran Ekin", "a04"),
    ("Türker", "a02"),
    ("Sevda", "a03"),
    ("Özgün", "a05"),
)

ALBUM_TEK_FOTOGRAFLAR = "a07"
ALBUM_TOPLU_FOTOGRAFLAR = "a08"

MANAGED_AUTO_ALBUM_TAGS: frozenset[str] = frozenset(
    {tag for _, tag in FAMILY_ALBUMS} | {ALBUM_TEK_FOTOGRAFLAR, ALBUM_TOPLU_FOTOGRAFLAR}
)


def _split_people(people: str | None) -> list[str]:
    if not people:
        return []
    return [person.strip() for person in people.split(",") if person.strip()]


def person_matches_album_label(person: str, label: str) -> bool:
    person_norm = turkish_normalize(person)
    label_norm = turkish_normalize(label)
    if not person_norm or not label_norm:
        return False
    return person_norm == label_norm or person_norm.startswith(label_norm + " ")


def auto_album_tags_from_people(people: str | None, *, is_photo: bool) -> set[str]:
    names = _split_people(people)
    tags: set[str] = set()
    for label, tag in FAMILY_ALBUMS:
        if any(person_matches_album_label(name, label) for name in names):
            tags.add(tag)
    if is_photo:
        if len(names) == 1:
            tags.add(ALBUM_TEK_FOTOGRAFLAR)
        elif len(names) >= 2:
            tags.add(ALBUM_TOPLU_FOTOGRAFLAR)
    return tags
