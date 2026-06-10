"""Tests for the Translator agent tools."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.translator.tools import create_translation_entry, create_glossary_entry


def test_create_translation_entry_fields():
    entry = create_translation_entry(
        region_id="R001",
        original_jp="おはよう",
        translation_en="Good morning",
        manga_title="Dragon Spirit",
        chapter=1,
        page=1,
    )
    assert entry["original_jp"] == "おはよう"
    assert entry["translation_en"] == "Good morning"
    assert entry["verified"] is False
    assert "entry_id" in entry
    assert "created_at" in entry


def test_create_glossary_entry_fields():
    entry = create_glossary_entry(
        term_jp="太郎",
        term_en="Taro",
        manga_title="Dragon Spirit",
        category="character_name",
    )
    assert entry["term_jp"] == "太郎"
    assert entry["term_en"] == "Taro"
    assert entry["category"] == "character_name"
    assert "created_at" in entry
