"""Seeds Elasticsearch with pre-built glossary, translation memory, and color references for demo."""
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from elasticsearch import Elasticsearch
from core.config import Config

es = Elasticsearch(Config.ES_URL, api_key=Config.ES_API_KEY)

# --- GLOSSARY ---
GLOSSARY = [
    {"term_jp": "太郎", "term_en": "Taro", "manga_title": "Dragon Spirit",
     "category": "character_name", "notes": "Main protagonist"},
    {"term_jp": "桜", "term_en": "Sakura", "manga_title": "Dragon Spirit",
     "category": "character_name", "notes": "Female lead, healer class"},
    {"term_jp": "竜の息吹", "term_en": "Dragon's Breath", "manga_title": "Dragon Spirit",
     "category": "attack_name", "notes": "Taro's signature move"},
    {"term_jp": "暗黒の森", "term_en": "The Dark Forest", "manga_title": "Dragon Spirit",
     "category": "place_name", "notes": "Setting of chapters 10-15"},
    {"term_jp": "魔王", "term_en": "Demon Lord", "manga_title": "Dragon Spirit",
     "category": "character_name", "notes": "Main antagonist — do NOT translate as 'Devil King'"},
    {"term_jp": "精霊石", "term_en": "Spirit Stone", "manga_title": "Dragon Spirit",
     "category": "item", "notes": "Key item, 7 total must be collected"},
    {"term_jp": "師匠", "term_en": "Master Ryuken", "manga_title": "Dragon Spirit",
     "category": "character_name", "notes": "Taro's martial arts teacher"},
    {"term_jp": "覚醒", "term_en": "Awakening", "manga_title": "Dragon Spirit",
     "category": "title", "notes": "Used as chapter title for transformation arcs"},
]

# --- TRANSLATION MEMORY ---
TRANSLATIONS = [
    {"original_jp": "おはよう、太郎くん！", "translation_en": "Good morning, Taro-kun!",
     "manga_title": "Dragon Spirit", "chapter": 1, "page": 3,
     "speaker": "Sakura", "confidence": 0.95, "verified": True},
    {"original_jp": "竜の息吹！", "translation_en": "Dragon's Breath!",
     "manga_title": "Dragon Spirit", "chapter": 5, "page": 12,
     "speaker": "Taro", "confidence": 1.0, "verified": True},
    {"original_jp": "まだまだだな", "translation_en": "You've still got a long way to go.",
     "manga_title": "Dragon Spirit", "chapter": 2, "page": 8,
     "speaker": "Master Ryuken", "confidence": 0.90, "verified": True},
    {"original_jp": "仲間を守る！それが俺の使命だ！",
     "translation_en": "Protecting my friends! That is my mission!",
     "manga_title": "Dragon Spirit", "chapter": 10, "page": 22,
     "speaker": "Taro", "confidence": 0.92, "verified": True},
    {"original_jp": "この精霊石の力を…",
     "translation_en": "The power of this Spirit Stone...",
     "manga_title": "Dragon Spirit", "chapter": 15, "page": 5,
     "speaker": "Sakura", "confidence": 0.88, "verified": True},
]

# --- COLOR REFERENCES ---
COLORS = [
    {"manga_title": "Dragon Spirit", "character_name": "Taro",
     "colors": {"hair": "spiky black", "eyes": "bright blue", "skin": "light tan",
                "outfit": "red jacket with gold trim, white shirt, dark blue pants",
                "accessories": "gold pendant necklace (Spirit Stone)"},
     "notes": "Main character — always vibrant, heroic color palette"},
    {"manga_title": "Dragon Spirit", "character_name": "Sakura",
     "colors": {"hair": "long, light pink", "eyes": "emerald green", "skin": "pale/fair",
                "outfit": "white and lavender priestess robes with cherry blossom embroidery",
                "accessories": "wooden staff with crystal tip"},
     "notes": "Healer — soft, pastel color palette"},
]


def seed_index(index: str, entries: list, label: str) -> None:
    for entry in entries:
        entry["created_at"] = datetime.now().isoformat()
        es.index(index=index, document=entry)
        print(f"  {label}: {list(entry.values())[0]}")


if __name__ == "__main__":
    print("🌱 Seeding Elasticsearch demo data...")
    seed_index("manga-glossary", GLOSSARY, "📖 Glossary")
    seed_index("translation-memory", TRANSLATIONS, "🌐 Memory")
    seed_index("color-references", COLORS, "🎨 Color")
    print("\n✅ All demo data seeded!")
