def draw_box_object_detection(image_bytes, detection_response):
    import io

    from PIL import Image, ImageDraw

    # Load the image from bytes
    img = Image.open(io.BytesIO(image_bytes))
    draw = ImageDraw.Draw(img)

    # Get the image dimensions
    img_width, img_height = img.size

    # Draw rectangles around bounding boxes
    for item in detection_response.items:
        # Check for None values and skip invalid items
        if (
            item.x_min is None
            or item.y_min is None
            or item.x_max is None
            or item.y_max is None
        ):
            continue

        try:
            # Convert coordinates to float and scale if necessary
            x_min = (
                float(item.x_min) * img_width
                if isinstance(item.x_min, (str, float))
                else int(item.x_min)
            )
            y_min = (
                float(item.y_min) * img_height
                if isinstance(item.y_min, (str, float))
                else int(item.y_min)
            )
            x_max = (
                float(item.x_max) * img_width
                if isinstance(item.x_max, (str, float))
                else int(item.x_max)
            )
            y_max = (
                float(item.y_max) * img_height
                if isinstance(item.y_max, (str, float))
                else int(item.y_max)
            )
        except ValueError:
            continue

        # Ensure valid coordinates
        if x_min < 0 or y_min < 0 or x_max > img_width or y_max > img_height:
            continue

        # Ensure x_max >= x_min and y_max >= y_min
        if x_max < x_min or y_max < y_min:
            continue

        # Draw rectangle and add text
        draw.rectangle([x_min, y_min, x_max, y_max], outline="red", width=2)
        draw.text(
            (x_min, max(0, y_min - 10)),
            f"{item.label} ({item.confidence:.2f})",
            fill="red",
        )  # Add label and confidence

    # Save to memory as bytes
    output_bytes = io.BytesIO()
    img.save(output_bytes, format="JPEG")
    output_bytes.seek(0)
    return output_bytes.getvalue()


def draw_box_ocr(image_bytes, ocr_response):
    import io

    from PIL import Image, ImageDraw

    # Load the image from bytes
    img = Image.open(io.BytesIO(image_bytes))
    draw = ImageDraw.Draw(img)

    # Get the image dimensions
    img_width, img_height = img.size

    # Draw rectangles around bounding boxes
    for bbox in ocr_response.bounding_boxes:
        # Scale bounding box coordinates if they are normalized
        left = bbox.left * img_width  # Assuming normalized coordinates
        top = bbox.top * img_height
        right = (bbox.left + bbox.width) * img_width
        bottom = (bbox.top + bbox.height) * img_height

        # Ensure valid coordinates
        if left < 0 or top < 0 or right > img_width or bottom > img_height:
            continue

        # Ensure y1 >= y0 and x1 >= x0
        if top > bottom or left > right:
            continue

        # Draw rectangle and add text
        draw.rectangle([left, top, right, bottom], outline="red", width=2)
        draw.text(
            (left, max(0, top - 10)), bbox.text, fill="red"
        )  # Add text above the box

    # Save to memory as bytes
    output_bytes = io.BytesIO()
    img.save(output_bytes, format="JPEG")
    output_bytes.seek(0)
    return output_bytes.getvalue()


def encode_file(file: bytes):
    import base64

    return base64.b64encode(file).decode("utf-8")


def decode_file(file: str) -> bytes:
    import base64

    return base64.b64decode(file)


def prepare_image(file_type: str, file: bytes):

    base64_file = encode_file(file)

    return {
        "role": "user",
        "content": [
            {
                "type": "image_url",
                "image_url": {"url": f"data:{file_type};base64,{base64_file}"},
            },
        ],
    }


def prepare_audio(file_type: str, file: bytes):

    base64_file = encode_file(file)

    return {
        "role": "user",
        "content": [
            {
                "type": "input_audio",
                "input_audio": {"data": base64_file, "format": file_type.split("/")[1]},
            }
        ],
    }
