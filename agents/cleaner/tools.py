import base64
import os
from io import BytesIO
from PIL import Image
from google import genai
from core.config import Config


def clean_and_typeset_page(
    image_base64: str,
    regions_with_translations: list,
) -> dict:
    """
    Uses Gemini's image editing to remove Japanese text and add English translations.

    Args:
        image_base64: Base64-encoded original manga page
        regions_with_translations: List of dicts with region_id, original_jp,
                                   translation_en, position, font_style

    Returns:
        Dict with the cleaned and typeset image as base64, or error info
    """
    input_image = Image.open(BytesIO(base64.b64decode(image_base64)))

    instructions = "\n".join(
        f"- Region at ({r.get('position', {}).get('x', 0)}%, "
        f"{r.get('position', {}).get('y', 0)}%): "
        f"Replace '{r['original_jp']}' with '{r['translation_en']}'"
        for r in regions_with_translations
    )

    prompt = (
        "Edit this manga page:\n"
        "1. Remove ALL Japanese text from every speech bubble, thought bubble, "
        "narration box, and SFX\n"
        "2. Fill emptied bubble areas with white; restore background art for SFX\n"
        f"3. Add these English translations at their respective locations:\n{instructions}\n\n"
        "Keep all line art, panel borders, and character drawings exactly as they are.\n"
        "Use a clean, readable manga font style for the English text.\n"
        "Center text within each speech bubble."
    )

    client = genai.Client(api_key=Config.GEMINI_API_KEY)
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp-image-generation",
        contents=[input_image, prompt],
    )

    for part in response.parts:
        if part.inline_data is not None:
            edited = part.as_image()
            buffer = BytesIO()
            edited.save(buffer, format="PNG")
            return {
                "status": "success",
                "edited_image_base64": base64.b64encode(buffer.getvalue()).decode("utf-8"),
                "width": edited.width,
                "height": edited.height,
            }

    return {"status": "error", "message": "No image returned from Gemini"}


def save_output_page(
    image_base64: str,
    manga_title: str,
    chapter: int,
    page: int,
    suffix: str = "translated",
) -> dict:
    """
    Saves a processed manga page to the output directory.

    Args:
        image_base64: Base64-encoded image to save
        manga_title: Manga series name
        chapter: Chapter number
        page: Page number
        suffix: Label suffix for the filename (e.g. "translated", "colored")

    Returns:
        Dict with saved file path and filename
    """
    img = Image.open(BytesIO(base64.b64decode(image_base64)))
    output_dir = os.path.join(Config.OUTPUT_DIR, manga_title, f"chapter_{chapter:03d}")
    os.makedirs(output_dir, exist_ok=True)
    filename = f"page_{page:03d}_{suffix}.png"
    filepath = os.path.join(output_dir, filename)
    img.save(filepath)
    return {"status": "saved", "file_path": filepath, "filename": filename}
