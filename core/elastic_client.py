from elasticsearch import Elasticsearch
from core.config import Config

_client: Elasticsearch | None = None


def get_client() -> Elasticsearch:
    global _client
    if _client is None:
        _client = Elasticsearch(Config.ES_URL, api_key=Config.ES_API_KEY)
    return _client
