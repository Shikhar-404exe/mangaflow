from datetime import datetime


def create_quality_report(
    manga_title: str,
    chapter: int,
    page: int,
    translation_accuracy: int,
    text_completeness: int,
    visual_quality: int,
    consistency: int,
    readability: int,
    issues: list = None,
    notes: str = "",
) -> dict:
    """
    Creates a quality assessment report for a translated manga page.

    Args:
        manga_title: Manga series name
        chapter: Chapter number
        page: Page number
        translation_accuracy: 0-100 score for translation accuracy
        text_completeness: 0-100 score for completeness of region translation
        visual_quality: 0-100 score for text placement and visual output
        consistency: 0-100 score for glossary and cross-chapter consistency
        readability: 0-100 score for natural English readability
        issues: List of flagged issues (strings)
        notes: Additional reviewer notes

    Returns:
        Quality report dict
    """
    overall = (
        translation_accuracy + text_completeness + visual_quality + consistency + readability
    ) / 5

    return {
        "report_id": f"QR-{manga_title[:10]}-C{chapter:03d}-P{page:02d}",
        "manga_title": manga_title,
        "chapter": chapter,
        "page": page,
        "scores": {
            "translation_accuracy": translation_accuracy,
            "text_completeness": text_completeness,
            "visual_quality": visual_quality,
            "consistency": consistency,
            "readability": readability,
            "overall": round(overall, 1),
        },
        "issues": issues or [],
        "notes": notes,
        "status": "pass" if overall >= 70 else "needs_review",
        "created_at": datetime.now().isoformat(),
    }
