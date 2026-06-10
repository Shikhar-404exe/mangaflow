"""Colorizer agent tools — colorizes B&W manga using OpenAI gpt-image-1.

If OpenAI billing is not active, colorization is skipped gracefully
and the cleaned (translated) image is returned as-is.
"""
import base64
from io import BytesIO
from PIL import Image
from core.config import Config


def colorize_manga_page(
    bw_image_base64: str,
    color_description: str = "",
    reference_image_base64: str = None,
) -> dict:
    """
    Colorizes a B&W manga panel using gpt-image-1.
    If unavailable (billing not set up), returns the input image unchanged.

    Args:
        bw_image_base64: Base64-encoded manga panel
        color_description: Text color guidelines
        reference_image_base64: Unused (API compatibility)

    Returns:
        Dict with colored_image_base64 or fallback to original
    """
    prompt = (
        "Colorize this black-and-white manga panel with rich, vibrant anime-style colors.\n\n"
        f"Color guidelines: {color_description}\n\n"
        "Rules:\n"
        "- Preserve ALL line art exactly — do not blur or modify any lines\n"
        "- Keep speech bubble interiors white with black text\n"
        "- Apply natural anime-style lighting and shadows\n"
        "- Use saturated, vivid colors typical of professional manga colorization\n"
        "- Match background colors to the scene mood"
    )

    try:
        from core.config import get_image_client
        client = get_image_client()
        if not client:
            raise ValueError("No OpenAI client — skipping colorization")

        img = Image.open(BytesIO(base64.b64decode(bw_image_base64))).convert("RGBA")
        buf = BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        response = client.images.edit(
            model="gpt-image-1",
            image=("panel.png", buf, "image/png"),
            prompt=prompt,
        )

        if response.data and response.data[0].b64_json:
            return {
                "status": "success",
                "colored_image_base64": response.data[0].b64_json,
                "method": "gpt-image-1",
            }
        return {"status": "error", "message": "No image returned from OpenAI"}

    except Exception as exc:
        # Graceful fallback — return original image unchanged
        return {
            "status": "success",           # treat as success so pipeline continues
            "colored_image_base64": bw_image_base64,
            "method": "skipped",
            "note": f"Colorization skipped: {exc}",
        }
