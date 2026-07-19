def parse_box(box_str: str) -> tuple[int, int, int, int]:
    parts = box_str.split("-")
    if len(parts) != 4:
        raise ValueError(f"Invalid detection box: {box_str!r}")
    x, y, w, h = (int(part) for part in parts)
    if w <= 0 or h <= 0:
        raise ValueError(f"Non-positive detection box: {box_str!r}")
    return x, y, w, h


def box_to_str(box: tuple[int, int, int, int]) -> str:
    return "-".join(str(int(value)) for value in box)


def face_side_px(box: tuple[int, int, int, int] | list) -> int:
    return min(int(box[2]), int(box[3]))


def eligible_for_recognition(
    side_px: int,
    *,
    largest_side_px: int,
    min_side_px: float | int | None,
    min_side_ratio: float | None,
) -> bool:
    if min_side_px is not None and float(min_side_px) > 0:
        if side_px < float(min_side_px):
            return False
    if min_side_ratio is not None and float(min_side_ratio) > 0 and largest_side_px > 0:
        if side_px < float(min_side_ratio) * largest_side_px:
            return False
    return True
