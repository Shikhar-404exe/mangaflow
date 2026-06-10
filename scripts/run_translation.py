"""
Main entry point for MangaFlow.

Usage:
  python scripts/run_translation.py --folder path/to/manga/pages
  python scripts/run_translation.py --folder path/to/manga/pages --title "My Manga" --chapter 1
  python scripts/run_translation.py --folder path/to/manga/pages --no-colorize
"""
import argparse
import asyncio
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types
from agents.root_agent.agent import root_agent
from core.config import Config

IMAGE_EXTS = ("*.png", "*.jpg", "*.jpeg", "*.webp")


def collect_pages(folder: str) -> list:
    pages = []
    for ext in IMAGE_EXTS:
        pages.extend(glob.glob(os.path.join(folder, ext)))
    return sorted(pages)


async def run_translation(folder: str, title: str, chapter: int, colorize: bool) -> None:
    print("=" * 60)
    print("📖 MangaFlow — AI Manga Translation & Colorization")
    print("=" * 60)
    print(f"📂 Manga folder : {folder}")
    print(f"📚 Title        : {title}")
    print(f"📖 Chapter      : {chapter}")
    print(f"🎨 Colorize     : {'yes' if colorize else 'no'}")
    print(f"🔗 Elastic      : {Config.ES_URL}")
    print("=" * 60)

    pages = collect_pages(folder)
    if not pages:
        print(f"❌ No images found in '{folder}'. Supported: PNG, JPG, JPEG, WEBP.")
        return

    print(f"📄 Found {len(pages)} page(s) to process:")
    for p in pages:
        print(f"   - {os.path.basename(p)}")

    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="mangaflow",
        user_id="translator_01",
    )

    runner = Runner(
        agent=root_agent,
        app_name="mangaflow",
        session_service=session_service,
    )

    page_list = "\n".join(f"- {p}" for p in pages)
    colorize_instruction = (
        "4. Colorize the cleaned page using character color references from Elastic\n"
        if colorize
        else "4. Skip colorization (user did not request it)\n"
    )

    full_prompt = (
        f"Translate {title} Chapter {chapter} from Japanese to English.\n\n"
        f"Pages to process:\n{page_list}\n\n"
        "For every page, run the full pipeline in order:\n"
        "1. Detect all text regions (speech bubbles, narration boxes, SFX, signs)\n"
        "2. Translate JP→EN — check the Elastic 'manga-glossary' and 'translation-memory' indices first\n"
        "3. Clean Japanese text from the page and typeset the English translations\n"
        f"{colorize_instruction}"
        "5. Run quality check and score the output\n\n"
        f"Use manga title '{title}' and chapter {chapter} for all Elastic indexing.\n"
        "Save all output pages to the output directory."
    )

    user_message = genai_types.Content(
        role="user",
        parts=[genai_types.Part(text=full_prompt)],
    )

    print("\n🚀 Starting translation...\n")

    async for event in runner.run_async(
        user_id="translator_01",
        session_id=session.id,
        new_message=user_message,
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(f"[{event.author}] {part.text}")

    print("\n" + "=" * 60)
    print("✅ Translation complete!")
    print(f"📁 Output saved to: {os.path.join(Config.OUTPUT_DIR, title, f'chapter_{chapter:03d}')}")
    print("=" * 60)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="MangaFlow — translate and optionally colorize a manga chapter"
    )
    parser.add_argument(
        "--folder", required=True,
        help="Path to the folder containing raw manga page images (JPG/PNG/WEBP)"
    )
    parser.add_argument(
        "--title", default="Unknown Manga",
        help="Manga series title used for Elastic indexing (default: 'Unknown Manga')"
    )
    parser.add_argument(
        "--chapter", type=int, default=1,
        help="Chapter number (default: 1)"
    )
    parser.add_argument(
        "--no-colorize", dest="colorize", action="store_false",
        help="Skip colorization step"
    )
    parser.set_defaults(colorize=True)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(run_translation(
        folder=args.folder,
        title=args.title,
        chapter=args.chapter,
        colorize=args.colorize,
    ))
