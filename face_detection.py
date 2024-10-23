from PIL import Image, ImageDraw, ImageFont
import numpy as np
from deepface.modules.detection import detect_faces


def draw_identifications(image: Image, detections_with_names) -> Image:

        original_image = image

        try:
            # Calculate box thickness and font size based on the image size
            box_thickness = 2 + int((image.size[0] + image.size[1]) / 1000)
            font_size = 10 + int(6 * (image.size[0] + image.size[1]) / 1000)

            # Use Arial font for Turkish letters (or any font available in the system)
            font = ImageFont.truetype("arial.ttf", size=font_size)

            # Create a draw object from PIL
            draw = ImageDraw.Draw(image, "RGBA")

            detections_with_names = preprocess_detections(detections_with_names)
            # Loop through each detection
            for box in detections_with_names:
                x, y, w, h, name, _ = box

                # Define top-left and bottom-right corners of the rectangle
                top_left = (x, y)
                bottom_right = (x + w, y + h)
                
                # Set color based on whether a name is provided
                box_color = (255, 255, 255) if name == "" else (0, 200, 0)
                
                # Draw the rectangle (box) for the face
                draw.rectangle([top_left, bottom_right], outline=box_color, width=box_thickness)

                # Prepare the name label to be displayed
                surname_index = name.rfind(" ")
                name = name[:surname_index] + '\n' + name[surname_index + 1:] if surname_index != -1 else name

                # Calculate the text's default position above the box
                text_x, text_y = x + 0.5 * font_size, y - 2.5 * font_size  

                # Get the bounding box of the text for background purposes
                text_bbox = draw.textbbox((text_x, text_y), name, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]

                # Make the background 10% wider and 20% taller than the text
                padding_x = int(0.1 * text_width)
                padding_y = int(0.3 * text_height)
                background_width = text_width + 2 * padding_x

                image_width = image.size[0]

                # If text goes above the image, move it below the box
                if text_y < 0:
                    text_y = y + h + 2.5 * font_size 
                
                # If text goes to the right of the image, move it to the left
                if text_x + background_width > image_width:
                    text_x = x - background_width - 0.5 * font_size

                # 75% black text background
                background_color = (0, 0, 0, 192)

                # Draw the background rectangle behind the text
                draw.rectangle(
                    [(text_x - padding_x, text_y - padding_y), (text_x + text_width + padding_x, text_y + text_height + padding_y)],
                    fill=background_color
                )

                # Draw the text on top of the background rectangle
                text_color = (255, 255, 255)
                draw.text((text_x, text_y), name, font=font, fill=text_color)

            return image

        except Exception as e:
            print(f"Error in draw_identifications: {e}")
            return original_image


def detect_people(image: Image):
        
        try:
            image = np.array(image)
            detection_results = detect_faces(detector_backend="yolov8", img=image, align=False, expand_percentage=0)

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
    # Remove manually added detections with no name
    detections_with_names = [det for det in detections_with_names if not (det[4] == "" and det[5] == "manual")]
    
    # Sort detections on x
    detections_with_names = sorted(detections_with_names, key=lambda x: x[0])
    return detections_with_names

