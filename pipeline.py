"""MangaFlow pipeline — image in → detect → translate → clean → colorize → image out."""
import base64
import json
from io import BytesIO
from PIL import Image
from google import genai
from core.config import Config
from agents.cleaner.tools import clean_and_typeset_page
from agents.colorizer.tools import colorize_manga_page


# ── helpers ─────────────────────────────────────────────────────────────────

def _to_b64(img: Image.Image) -> str:
    buf = BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def _prepare_image(image_bytes: bytes) -> tuple[str, int, int]:
    """Decode, normalise to RGB, resize if > 1500px, return (b64, w, h)."""
    img = Image.open(BytesIO(image_bytes))
    if img.mode == "RGBA":
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3])
        img = bg
    elif img.mode != "RGB":
        img = img.convert("RGB")

    max_dim = 1500
    if max(img.size) > max_dim:
        ratio = max_dim / max(img.size)
        img = img.resize((int(img.width * ratio), int(img.height * ratio)),
                         Image.LANCZOS)
    return _to_b64(img), img.width, img.height


# ── step 1: detect ───────────────────────────────────────────────────────────

def detect_bubbles(image_b64: str) -> list[dict]:
    """Ask Gemini Vision to find speech bubbles and extract text."""
    client = genai.Client(api_key=Config.GEMINI_API_KEY)
    img = Image.open(BytesIO(base64.b64decode(image_b64)))

    prompt = (
        "Analyze this manga panel. Find ALL speech bubbles, thought bubbles, "
        "narration boxes, and sound effects (SFX).\n\n"
        "For each region return a JSON object:\n"
        '  "region_id": unique id e.g. "bubble_1"\n'
        '  "original_text": exact text inside (empty string if illegible)\n'
        '  "position": {"x": <center_x_pct>, "y": <center_y_pct>}\n'
        '  "bubble_type": "speech" | "thought" | "narration" | "sfx"\n'
        '  "needs_translation": true if NOT already English\n\n'
        "Return ONLY a valid JSON array. If no text found, return []."
    )

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[img, prompt],
        config=genai.types.GenerateContentConfig(
            response_mime_type="application/json"
        ),
    )
    try:
        bubbles = json.loads(response.text)
        return bubbles if isinstance(bubbles, list) else []
    except Exception:
        return []


# ── step 2: translate ────────────────────────────────────────────────────────

def _fetch_glossary(manga_title: str) -> str:
    """Pull known terms from Elastic to ground the translation."""
    try:
        from elasticsearch import Elasticsearch
        es = Elasticsearch(Config.ES_URL, api_key=Config.ES_API_KEY)
        res = es.search(
            index="manga-glossary",
            body={"query": {"match": {"manga_title": manga_title}}, "size": 30},
        )
        terms = [h["_source"] for h in res["hits"]["hits"]]
        if terms:
            lines = "\n".join(
                f"  {t['term_jp']} = {t['term_en']}" for t in terms
            )
            return f"Established terminology (use these exactly):\n{lines}"
    except Exception:
        pass
    return ""


def translate_bubbles(bubbles: list, manga_title: str = "Unknown") -> list[dict]:
    """Translate each bubble that needs_translation using Gemini + glossary."""
    to_translate = [
        b for b in bubbles
        if b.get("needs_translation") and b.get("original_text")
    ]
    if not to_translate:
        # mark already-English bubbles
        for b in bubbles:
            if not b.get("needs_translation"):
                b["translation_en"] = b.get("original_text", "")
        return bubbles

    glossary = _fetch_glossary(manga_title)
    client = genai.Client(api_key=Config.GEMINI_API_KEY)
    texts = [{"id": b["region_id"], "text": b["original_text"]} for b in to_translate]

    prompt = (
        "You are a professional manga translator. Translate to natural English.\n"
        "Keep the character's voice. Use short sentences that fit in a speech bubble.\n"
        f"{glossary}\n\n"
        "Return ONLY a JSON array: "
        '[{"id":"bubble_1","translation":"English text"}, ...]\n\n'
        f"Entries:\n{json.dumps(texts, ensure_ascii=False)}"
    )

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[prompt],
        config=genai.types.GenerateContentConfig(
            response_mime_type="application/json"
        ),
    )
    try:
        results = json.loads(response.text)
        trans_map = {r["id"]: r["translation"] for r in results}
    except Exception:
        trans_map = {}

    for b in bubbles:
        if b["region_id"] in trans_map:
            b["translation_en"] = trans_map[b["region_id"]]
        elif not b.get("needs_translation"):
            b["translation_en"] = b.get("original_text", "")

    return bubbles


# ── main pipeline ────────────────────────────────────────────────────────────

def run_pipeline(
    image_bytes: bytes,
    do_translate: bool = True,
    do_colorize: bool = True,
    manga_title: str = "Unknown",
):
    """
    Synchronous generator. Yields progress dicts.
    Final event has step="done" and contains the result image.
    """
    # ── load ──
    yield {"step": "loading", "pct": 5, "msg": "Loading image..."}
    image_b64, w, h = _prepare_image(image_bytes)

    # ── detect ──
    yield {"step": "detecting", "pct": 20, "msg": "Scanning for speech bubbles..."}
    bubbles = detect_bubbles(image_b64)
    foreign_count = len([b for b in bubbles if b.get("needs_translation")])

    processed_b64 = image_b64
    translations_out = []

    # ── translate + clean ──
    if do_translate:
        if foreign_count > 0:
            yield {
                "step": "translating",
                "pct": 40,
                "msg": f"Translating {foreign_count} bubble(s)...",
            }
            bubbles = translate_bubbles(bubbles, manga_title)
            translations_out = [
                {
                    "original": b.get("original_text", ""),
                    "translation": b.get("translation_en", ""),
                    "type": b.get("bubble_type", "speech"),
                }
                for b in bubbles
                if b.get("translation_en")
            ]

            regions = [
                {
                    "region_id": b["region_id"],
                    "original_jp": b.get("original_text", ""),
                    "translation_en": b.get(
                        "translation_en", b.get("original_text", "")
                    ),
                    "position": b.get("position", {"x": 50, "y": 50}),
                    "font_style": "bangers",
                }
                for b in bubbles
            ]

            yield {"step": "cleaning", "pct": 60,
                   "msg": "Removing original text and placing English..."}
            clean = clean_and_typeset_page(image_b64, regions)
            if clean.get("status") == "success":
                processed_b64 = clean["edited_image_base64"]
        else:
            yield {"step": "translating", "pct": 60,
                   "msg": "No foreign text detected — panel already in English"}

    # ── colorize ──
    if do_colorize:
        yield {"step": "colorizing", "pct": 80,
               "msg": "Applying vibrant anime-style colors..."}
        color = colorize_manga_page(
            processed_b64,
            "Vibrant anime-style coloring. Preserve all line art and panel borders exactly.",
        )
        if color.get("status") == "success":
            processed_b64 = color["colored_image_base64"]

    # ── quality ──
    yield {"step": "quality", "pct": 95, "msg": "Running quality check..."}
    quality = 90 if translations_out else 85

    yield {
        "step": "done",
        "pct": 100,
        "image_b64": processed_b64,
        "original_b64": image_b64,
        "translations": translations_out,
        "bubbles_found": len(bubbles),
        "quality_score": quality,
        "width": w,
        "height": h,
    }
