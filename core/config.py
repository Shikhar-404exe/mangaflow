import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
    ES_URL = os.getenv("ES_URL")
    ES_API_KEY = os.getenv("ES_API_KEY")

    _base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    OUTPUT_DIR = os.path.join(_base, "output")
    DEMO_DIR = os.path.join(_base, "demo")
