from PIL import Image

from faces.paths import DEFAULT_CROP_PAD_RATIO


def crop_face(
    image: Image.Image,
    box: tuple[int, int, int, int],
    pad_ratio: float = DEFAULT_CROP_PAD_RATIO,
) -> Image.Image:
    x, y, w, h = box
    pad_x = int(w * pad_ratio)
    pad_y = int(h * pad_ratio)
    left = max(0, x - pad_x)
    top = max(0, y - pad_y)
    right = min(image.width, x + w + pad_x)
    bottom = min(image.height, y + h + pad_y)
    if right <= left or bottom <= top:
        raise ValueError(f"Invalid crop bounds for box {box} on {image.size}")
    return image.crop((left, top, right, bottom))
