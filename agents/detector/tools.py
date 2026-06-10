import base64
from io import BytesIO
from PIL import Image


def load_manga_page(file_path: str) -> dict:
    """
    Loads a manga page image from disk and returns it as base64 for analysis.

    Args:
        file_path: Path to the manga page image file (JPG/PNG)

    Returns:
        Dict with image data, dimensions, and metadata
    """
    img = Image.open(file_path)

    max_dim = 1500
    if max(img.size) > max_dim:
        ratio = max_dim / max(img.size)
        img = img.resize((int(img.width * ratio), int(img.height * ratio)))

    buffer = BytesIO()
    img.save(buffer, format="JPEG", quality=90)
    img_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return {
        "image_base64": img_b64,
        "width": img.width,
        "height": img.height,
        "file_path": file_path,
        "format": "jpeg",
    }
