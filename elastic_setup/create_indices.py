"""Creates all Elasticsearch indices using the JSON mapping files."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from elasticsearch import Elasticsearch
from core.config import Config


INDICES = [
    "translation-memory",
    "manga-glossary",
    "manga-pages",
    "quality-scores",
    "color-references",
]


def create_all_indices() -> None:
    es = Elasticsearch(Config.ES_URL, api_key=Config.ES_API_KEY)
    mappings_dir = os.path.join(os.path.dirname(__file__), "mappings")

    for name in INDICES:
        path = os.path.join(mappings_dir, f"{name}.json")
        with open(path) as fh:
            mapping = json.load(fh)

        if es.indices.exists(index=name):
            print(f"⏭️  Exists: {name}")
        else:
            es.indices.create(index=name, body=mapping)
            print(f"✅ Created: {name}")


if __name__ == "__main__":
    create_all_indices()
