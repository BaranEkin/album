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
