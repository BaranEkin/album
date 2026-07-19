from PIL import Image
import numpy as np
from deepface.modules.detection import detect_faces

_device_logged = False


def get_torch_device() -> str:
    """Return ultralytics/torch device: cuda:0 when available, otherwise cpu."""
    try:
        import torch

        if torch.cuda.is_available():
            return "cuda:0"
        return "cpu"
    except Exception:
        return "cpu"


def _log_torch_device_once() -> None:
    global _device_logged
    if _device_logged:
        return
    _device_logged = True
    try:
        from logger import log

        device = get_torch_device()
        detail = device
        if device.startswith("cuda"):
            import torch

            detail = f"{device} ({torch.cuda.get_device_name(0)})"
        log("faces.detection", f"Torch device for YOLO: {detail}")
    except Exception:
        pass


def detect_people(image: Image.Image):
    """Detect and return bounding boxes for faces in an image using the YOLOv8n backend.

    Uses GPU automatically when CUDA PyTorch is installed and a GPU is present;
    otherwise runs on CPU. No GPU is required.

    Args:
        image (PIL.Image): The image in which to detect faces.

    Returns:
        list: A list of bounding boxes for detected faces, each formatted as
              [x, y, width, height, ""(placeholder for name), "auto"], sorted by the x-coordinate.

    Raises:
        Exception: If an error occurs during detection, an empty list is returned.
    """

    try:
        _log_torch_device_once()
        image_array = np.array(image)
        detection_results = detect_faces(
            detector_backend="yolov8n",
            img=image_array,
            align=False,
            expand_percentage=0,
        )

        detections = []
        for det in detection_results:
            box = det.facial_area
            if box.left_eye or box.right_eye:
                detections.append([box.x, box.y, box.w, box.h, "", "auto"])

        sorted_detections = sorted(detections, key=lambda x: x[0])

        return sorted_detections
    except Exception as e:
        print(e)
        return []


def preprocess_detections(detections_with_names):
    """Filter and sort face detections, removing unnamed manual detections.

    Args:
        detections_with_names (list): List of detections, each containing [x, y, width, height, name, method].

    Returns:
        list: Filtered and sorted detections, with unnamed manual entries removed and ordered by x-coordinate.
    """

    detections_with_names = [
        det
        for det in detections_with_names
        if not (det[4] == "" and det[5] == "manual")
    ]

    detections_with_names = sorted(detections_with_names, key=lambda x: x[0])
    return detections_with_names


def build_detections_with_names(detections_str: str, names_str: str):
    """Build a list of detections with names from string inputs of bounding boxes and names.

    Args:
        detections_str (str): A comma-separated string of detections in "x-y-w-h" format.
        names_str (str): A comma-separated string of names corresponding to each detection.

    Returns:
        list: A list of detections, each formatted as [x, y, width, height, name, "auto"].

    Raises:
        AssertionError: If the number of names does not match the number of detections.
    """

    names = names_str.split(",")
    detections: list[list[int | str]] = [
        list(map(int, det_str.split("-"))) for det_str in detections_str.split(",")
    ]

    assert len(names) == len(detections)

    for i, det in enumerate(detections):
        det.extend([names[i], "auto"])

    return detections
