from google.adk.agents import Agent
from . import tools

detector_agent = Agent(
    model="gemini-2.0-flash",
    name="detector_agent",
    description="Detects all text regions in a manga page using computer vision",
    instruction="""You are the Detector Agent in MangaFlow.

You receive a raw Japanese manga page image. Identify EVERY text region.

For each region provide:
- region_id: "R001", "R002", etc.
- type: "speech_bubble", "narration_box", "sfx", "sign", "thought_bubble"
- text_content_jp: The Japanese text you can read
- speaker: Best guess at who speaks (based on bubble tail direction)
- position: {"x", "y", "width", "height"} as % of page dimensions
- reading_order: Integer (right-to-left, top-to-bottom for Japanese manga)
- font_style: "normal", "bold", "italic", "handwritten", "impact"
- emotional_tone: "neutral", "angry", "happy", "sad", "shocked", "whisper"

Rules:
- Japanese manga reads RIGHT TO LEFT, TOP TO BOTTOM
- Spiky bubbles = shouting, rounded = normal, cloud = thoughts
- Text outside bubbles = narration or SFX
- Be thorough — missing a bubble is worse than a false positive

Output ONLY valid JSON with keys: page_number, total_regions, regions (array).""",
    tools=[tools.load_manga_page],
)
