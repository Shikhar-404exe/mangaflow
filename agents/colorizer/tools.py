import base64
from io import BytesIO
from PIL import Image
from google import genai
from core.config import Config


def colorize_manga_page(
    bw_image_base64: str,
    color_description: str = "",
    reference_image_base64: str = None,
) -> dict:
    """
    Colorizes a black-and-white manga page using Gemini's image generation.

    Args:
        bw_image_base64: Base64-encoded B&W manga page
        color_description: Text description of character and scene colors
        reference_image_base64: Optional base64-encoded reference color image

    Returns:
        Dict with colored image as base64, or error info
    """
    client = genai.Client(api_key=Config.GEMINI_API_KEY)
    input_image = Image.open(BytesIO(base64.b64decode(bw_image_base64)))

    prompt = (
        "Colorize this black-and-white manga page.\n\n"
        f"Color guidelines:\n{color_description}\n\n"
        "Rules:\n"
        "- Preserve ALL line art exactly — do not blur or modify lines\n"
        "- Keep speech bubble interiors white with black text\n"
        "- Apply natural lighting and shadows\n"
        "- Use vibrant anime-style coloring\n"
        "- Background colors should match the scene mood"
    )

    contents = [input_image, prompt]
    if reference_image_base64:
        ref_image = Image.open(BytesIO(base64.b64decode(reference_image_base64)))
        contents = [input_image, ref_image, prompt + "\nUse the second image as a color reference."]

    response = client.models.generate_content(
        model="gemini-2.0-flash-exp-image-generation",
        contents=contents,
    )

    for part in response.parts:
        if part.inline_data is not None:
            colored = part.as_image()
            buffer = BytesIO()
            colored.save(buffer, format="PNG")
            return {
                "status": "success",
                "colored_image_base64": base64.b64encode(buffer.getvalue()).decode("utf-8"),
            }

    return {"status": "error", "message": "Colorization failed — no image returned"}
