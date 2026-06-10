"""One-click Elasticsearch setup: creates indices and seeds demo data."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from elastic_setup.create_indices import create_all_indices
from scripts.seed_demo_data import seed_index, GLOSSARY, TRANSLATIONS, COLORS


if __name__ == "__main__":
    print("🔧 Setting up Elasticsearch...")
    create_all_indices()
    print("\n🌱 Seeding demo data...")
    seed_index("manga-glossary", GLOSSARY, "📖 Glossary")
    seed_index("translation-memory", TRANSLATIONS, "🌐 Memory")
    seed_index("color-references", COLORS, "🎨 Color")
    print("\n✅ Elasticsearch setup complete!")
