from PIL import Image, ImageDraw, ImageFont
import numpy as np
from deepface.modules.detection import detect_faces
import platform


def draw_identifications(image: Image, detections_with_names) -> Image:
    """Draw bounding boxes labeled with names for identified faces on an image.

    Args:
        image (PIL.Image): The image to annotate.
        detections_with_names (list): List of detections with names, each formatted as
                                      [x, y, width, height, name, method].

    Returns:
        PIL.Image: The annotated image with labeled bounding boxes.

    Raises:
        Exception: If an error occurs during the drawing process, returns the original image.
    """

    original_image = image

    try:
        # Calculate box thickness and font size based on the image size
        box_thickness = 2 + int((image.size[0] + image.size[1]) / 1000)
        font_size = 8 + int(5 * (image.size[0] + image.size[1]) / 1000)

        # Choose font based on operating system
        current_os = platform.system()

        if current_os == "Windows":
            font = ImageFont.truetype("arial.ttf", size=font_size)
        else:  # Linux (Fedora)
            # font = ImageFont.load_default(size=font_size)
            font = ImageFont.truetype(
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                size=font_size,
            )

        # Create a draw object from PIL
        image = image.convert("RGBA")
        draw = ImageDraw.Draw(image, "RGBA")

        detections_with_names = preprocess_detections(detections_with_names)
        # First pass: Draw all boxes
        text_elements = []
        for box in detections_with_names:
            x, y, w, h, name, _ = box

            # Define top-left and bottom-right corners of the rectangle
            top_left = (x, y)
            bottom_right = (x + w, y + h)

            # Set color based on whether a name is provided
            box_color = (255, 255, 255) if name == "" else (0, 200, 0)

            # Draw the rectangle (box) for the face
            draw.rectangle(
                [top_left, bottom_right], outline=box_color, width=box_thickness
            )

            # Skip if no name to display
            if not name:
                continue

            # Prepare the name label to be displayed
            surname_index = name.rfind(" ")
            name = (
                name[:surname_index] + "\n" + name[surname_index + 1 :]
                if surname_index != -1
                else name
            )

            # Calculate the text's default position above the box
            text_x, text_y = x + 0.5 * font_size, y - 2.5 * font_size

            # Get the bounding box of the text for background purposes
            text_bbox = draw.textbbox((text_x, text_y), name, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]

            # Make the background 10% wider and 30% taller than the text
            padding_x = int(0.1 * text_width)
            padding_y = int(0.3 * text_height)
            background_width = text_width + 2 * padding_x

            image_width = image.size[0]

            # If text goes above the image, move it below the box
            if text_y < 0:
                text_y = y + h + 0.5 * font_size

            # If text goes to the right of the image, move it to the left
            if text_x + background_width > image_width:
                text_x = x - background_width - 0.5 * font_size

            # Store text element for second pass
            text_elements.append(
                {
                    "text": name,
                    "position": (text_x, text_y),
                    "width": text_width,
                    "height": text_height,
                    "padding_x": padding_x,
                    "padding_y": padding_y,
                }
            )

        # Second pass: Draw all text elements
        for text_item in text_elements:
            # Draw the background rectangle behind the text
            draw.rectangle(
                [
                    (
                        text_item["position"][0] - text_item["padding_x"],
                        text_item["position"][1] - text_item["padding_y"],
                    ),
                    (
                        text_item["position"][0]
                        + text_item["width"]
                        + text_item["padding_x"],
                        text_item["position"][1]
                        + text_item["height"]
                        + text_item["padding_y"],
                    ),
                ],
                fill=(0, 0, 0, 128),  # 50% black background
            )

            # Draw the text on top of the background rectangle
            draw.text(
                text_item["position"],
                text_item["text"],
                font=font,
                fill=(255, 255, 255),
            )

        return image

    except Exception:
        return original_image


def detect_people(image: Image):
    """Detect and return bounding boxes for faces in an image using the YOLOv8 backend.

    Args:
        image (PIL.Image): The image in which to detect faces.

    Returns:
        list: A list of bounding boxes for detected faces, each formatted as
              [x, y, width, height, ""(placeholder for name), "auto"], sorted by the x-coordinate.

    Raises:
        Exception: If an error occurs during detection, an empty list is returned.
    """

    try:
        image = np.array(image)
        detection_results = detect_faces(
            detector_backend="yolov8", img=image, align=False, expand_percentage=0
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

    # Remove manually added detections with no name
    detections_with_names = [
        det
        for det in detections_with_names
        if not (det[4] == "" and det[5] == "manual")
    ]

    # Sort detections on x
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
    detections = [
        list(map(int, det_str.split("-"))) for det_str in detections_str.split(",")
    ]

    assert len(names) == len(detections)

    for i, det in enumerate(detections):
        det.extend([names[i], "auto"])

    return detections
