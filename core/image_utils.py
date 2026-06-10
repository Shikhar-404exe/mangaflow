import base64
import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont


def load_image(path: str) -> Image.Image:
    return Image.open(path)


def image_to_base64(img: Image.Image, fmt: str = "JPEG", quality: int = 90) -> str:
    buffer = BytesIO()
    img.save(buffer, format=fmt, quality=quality)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def base64_to_image(b64_str: str) -> Image.Image:
    return Image.open(BytesIO(base64.b64decode(b64_str)))


def save_image(img: Image.Image, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path, quality=95)


def overlay_text_on_image(
    img: Image.Image,
    text: str,
    position: dict,
    font_size: int = 14,
    font_style: str = "normal",
) -> Image.Image:
    """Overlay translated text onto a manga page using percentage-based positions."""
    draw = ImageDraw.Draw(img)
    x = int(img.width * position["x"] / 100)
    y = int(img.height * position["y"] / 100)
    w = int(img.width * position["width"] / 100)
    h = int(img.height * position["height"] / 100)

    font_map = {
        "bold": "arialbd.ttf",
        "impact": "arialbd.ttf",
        "italic": "ariali.ttf",
    }
    try:
        font = ImageFont.truetype(font_map.get(font_style, "arial.ttf"), font_size)
    except (OSError, IOError):
        font = ImageFont.load_default()

    words = text.split()
    lines, current = [], ""
    for word in words:
        test = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= w - 10:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)

    line_height = font_size + 4
    start_y = y + (h - len(lines) * line_height) // 2

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        line_x = x + (w - (bbox[2] - bbox[0])) // 2
        draw.text((line_x, start_y + i * line_height), line, fill="black", font=font)

    return img
