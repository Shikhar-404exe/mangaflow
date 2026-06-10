from pydantic import BaseModel
from typing import Optional


class TextRegion(BaseModel):
    region_id: str
    type: str
    text_content_jp: str
    speaker: Optional[str] = None
    position: dict
    reading_order: int
    font_style: str = "normal"
    emotional_tone: str = "neutral"


class TranslationEntry(BaseModel):
    region_id: str
    original_jp: str
    translation_en: str
    manga_title: str
    chapter: int
    page: int
    speaker: str = "unknown"
    confidence: float = 0.9
    translator_notes: str = ""
    glossary_terms_used: list = []
    verified: bool = False


class QualityReport(BaseModel):
    report_id: str
    manga_title: str
    chapter: int
    page: int
    scores: dict
    issues: list = []
    notes: str = ""
    status: str
