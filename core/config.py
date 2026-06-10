import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # API keys — set whichever you have
    OPENAI_API_KEY     = os.getenv("OPENAI_API_KEY")       # needs billing
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")   # free tier available
    GROQ_API_KEY       = os.getenv("GROQ_API_KEY")         # free, fast, vision support

    # Elasticsearch
    ES_URL     = os.getenv("ES_URL")
    ES_API_KEY = os.getenv("ES_API_KEY")

    # Paths
    _base      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    OUTPUT_DIR = os.path.join(_base, "output")
    DEMO_DIR   = os.path.join(_base, "demo")


def get_text_client():
    """
    Returns (client, model_name) for text/vision tasks.
    Priority: Groq (free) → OpenRouter → OpenAI
    """
    from openai import OpenAI

    if Config.GROQ_API_KEY:
        return (
            OpenAI(api_key=Config.GROQ_API_KEY,
                   base_url="https://api.groq.com/openai/v1"),
            "meta-llama/llama-4-scout-17b-16e-instruct",   # Llama 4 Scout — vision + free
        )
    if Config.OPENROUTER_API_KEY:
        return (
            OpenAI(api_key=Config.OPENROUTER_API_KEY,
                   base_url="https://openrouter.ai/api/v1"),
            "openai/gpt-4o",
        )
    if Config.OPENAI_API_KEY:
        return OpenAI(api_key=Config.OPENAI_API_KEY), "gpt-4o"

    raise RuntimeError(
        "No text API key found. Set one of: GROQ_API_KEY, OPENROUTER_API_KEY, or OPENAI_API_KEY"
    )


def get_image_client():
    """
    Returns OpenAI client for gpt-image-1 image editing.
    Requires OPENAI_API_KEY with billing.
    Returns None if unavailable (PIL fallback will be used).
    """
    if not Config.OPENAI_API_KEY:
        return None
    try:
        from openai import OpenAI
        return OpenAI(api_key=Config.OPENAI_API_KEY)
    except Exception:
        return None
