from datetime import datetime


def create_translation_entry(
    region_id: str,
    original_jp: str,
    translation_en: str,
    manga_title: str,
    chapter: int,
    page: int,
    speaker: str = "unknown",
    confidence: float = 0.9,
    translator_notes: str = "",
    glossary_terms_used: list = None,
) -> dict:
    """
    Creates a translation entry ready for indexing into Elasticsearch translation memory.

    Args:
        region_id: Unique region ID matching the detector output
        original_jp: Original Japanese text
        translation_en: English translation
        manga_title: Title of the manga series
        chapter: Chapter number
        page: Page number
        speaker: Character speaking this line
        confidence: Translation confidence score (0-1)
        translator_notes: Optional notes for human editors
        glossary_terms_used: List of glossary terms applied

    Returns:
        Translation entry dict ready for ES indexing
    """
    return {
        "entry_id": f"TM-{manga_title[:10]}-C{chapter:03d}-P{page:02d}-{region_id}",
        "region_id": region_id,
        "original_jp": original_jp,
        "translation_en": translation_en,
        "manga_title": manga_title,
        "chapter": chapter,
        "page": page,
        "speaker": speaker,
        "confidence": confidence,
        "translator_notes": translator_notes,
        "glossary_terms_used": glossary_terms_used or [],
        "verified": False,
        "created_at": datetime.now().isoformat(),
    }


def create_glossary_entry(
    term_jp: str,
    term_en: str,
    manga_title: str,
    category: str,
    notes: str = "",
) -> dict:
    """
    Creates a new glossary entry for consistent terminology.

    Args:
        term_jp: Japanese term
        term_en: Established English translation
        manga_title: Which manga this term belongs to
        category: One of: character_name, place_name, attack_name, item, title, organization
        notes: Additional context

    Returns:
        Glossary entry dict ready for ES indexing
    """
    return {
        "term_jp": term_jp,
        "term_en": term_en,
        "manga_title": manga_title,
        "category": category,
        "notes": notes,
        "created_at": datetime.now().isoformat(),
    }
