"""Cleaner agent tools — removes original text and typesets English.

Primary:  OpenAI gpt-image-1 (requires billing)
Fallback: PIL-based text replacement (always works, no API cost)
"""
import base64
import os
import textwrap
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from core.config import Config


# ── PIL fallback ──────────────────────────────────────────────────────────────

def _get_font(size: int = 24):
    """Try to load a bold system font; fall back to PIL default."""
    font_candidates = [
        "arialbd.ttf", "Arial_Bold.ttf",          # Windows
        "DejaVuSans-Bold.ttf",                      # Linux
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",  # macOS
    ]
    for name in font_candidates:
        try:
            return ImageFont.truetype(name, size)
        except (IOError, OSError):
            pass
    return ImageFont.load_default()


def _pil_clean_and_typeset(
    img: Image.Image,
    regions: list,
) -> Image.Image:
    """
    PIL-based fallback: draws white boxes over bubble areas and renders
    English text. Uses x/y percent positions from detection.
    """
    draw = ImageDraw.Draw(img)
    w, h = img.size

    for r in regions:
        if not r.get("translation_en"):
            continue

        pos = r.get("position", {"x": 50, "y": 50})
        cx = int(pos.get("x", 50) / 100 * w)
        cy = int(pos.get("y", 50) / 100 * h)

        # Estimate bubble radius based on text length
        text = r["translation_en"]
        font_size = max(16, min(28, int(w / 20)))
        font = _get_font(font_size)

        wrapped = textwrap.fill(text, width=16)
        lines   = wrapped.split("\n")
        line_h  = font_size + 4
        tw      = max(len(l) for l in lines) * (font_size // 2)
        bh      = len(lines) * line_h

        pad = 14
        x0, y0 = cx - tw // 2 - pad, cy - bh // 2 - pad
        x1, y1 = cx + tw // 2 + pad, cy + bh // 2 + pad

        # White bubble + thin border
        draw.ellipse([x0, y0, x1, y1], fill="white", outline="#cccccc", width=2)

        # Draw text lines centred
        y_text = cy - bh // 2
        for line in lines:
            draw.text((cx, y_text), line, fill="black", font=font, anchor="mm")
            y_text += line_h

    return img


# ── main function ─────────────────────────────────────────────────────────────

def clean_and_typeset_page(
    image_base64: str,
    regions_with_translations: list,
) -> dict:
    """
    Removes original text and adds English translations.

    Tries gpt-image-1 first; if that fails (billing/quota), falls back to PIL.

    Args:
        image_base64: Base64-encoded manga panel
        regions_with_translations: List of dicts with region_id, original_jp,
                                   translation_en, position, font_style
    Returns:
        Dict with edited_image_base64 or error info
    """
    # ── try OpenAI gpt-image-1 ──
    try:
        from core.config import get_image_client
        client = get_image_client()
        if client:
            instructions = "\n".join(
                f"- Around ({r.get('position',{}).get('x',50)}%, "
                f"{r.get('position',{}).get('y',50)}%): "
                f"Replace '{r.get('original_jp','')}' with '{r.get('translation_en','')}'"
                for r in regions_with_translations
                if r.get("translation_en")
            )
            prompt = (
                "Edit this manga panel:\n"
                "1. Remove ALL Japanese/foreign text from every speech bubble, thought bubble, "
                "narration box, and sound effect\n"
                "2. Fill emptied bubble areas with white; restore background art for SFX\n"
                f"3. Add these English translations:\n{instructions}\n\n"
                "Keep ALL line art, panel borders, and character drawings exactly as they are.\n"
                "Use bold, uppercase comic-book style font. Center text in each bubble."
            )

            img_src = Image.open(BytesIO(base64.b64decode(image_base64))).convert("RGBA")
            buf = BytesIO()
            img_src.save(buf, format="PNG")
            buf.seek(0)

            response = client.images.edit(
                model="gpt-image-1",
                image=("panel.png", buf, "image/png"),
                prompt=prompt,
            )

            if response.data and response.data[0].b64_json:
                b64 = response.data[0].b64_json
                out = Image.open(BytesIO(base64.b64decode(b64)))
                return {
                    "status": "success",
                    "edited_image_base64": b64,
                    "width": out.width,
                    "height": out.height,
                    "method": "gpt-image-1",
                }
    except Exception:
        pass  # fall through to PIL

    # ── PIL fallback ──
    img = Image.open(BytesIO(base64.b64decode(image_base64))).convert("RGB")
    img = _pil_clean_and_typeset(img, regions_with_translations)

    buf = BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()

    return {
        "status": "success",
        "edited_image_base64": b64,
        "width": img.width,
        "height": img.height,
        "method": "pil-fallback",
    }


def save_output_page(
    image_base64: str,
    manga_title: str,
    chapter: int,
    page: int,
    suffix: str = "translated",
) -> dict:
    """Saves a processed manga page to the output directory."""
    img = Image.open(BytesIO(base64.b64decode(image_base64)))
    out_dir = os.path.join(Config.OUTPUT_DIR, manga_title, f"chapter_{chapter:03d}")
    os.makedirs(out_dir, exist_ok=True)
    filename = f"page_{page:03d}_{suffix}.png"
    filepath = os.path.join(out_dir, filename)
    img.save(filepath)
    return {"status": "saved", "file_path": filepath, "filename": filename}
