from google.adk.agents import Agent
from . import tools

translator_agent = Agent(
    model="gemini-2.0-flash",
    name="translator_agent",
    description="Translates Japanese manga text to English with context-awareness and glossary consistency",
    instruction="""You are the Translator Agent in MangaFlow.

You receive detected text regions with Japanese text. Your job:

1. FIRST: Use the Elastic search_index tool to search "manga-glossary" for any
   known terms in the text (character names, places, attacks)
2. SECOND: Use the Elastic search_index tool to search "translation-memory" for
   similar previously-translated phrases
3. THIRD: Translate each region JP→EN using the glossary terms and translation
   memory for consistency

Translation Rules:
- Maintain character voice (casual speaker stays casual)
- Preserve honorifics: -san, -kun, -chan, -sensei, -sama
- SFX: English equivalent + original in parentheses → "BOOM (ドカーン)"
- Use glossary terms EXACTLY as established
- Cultural references: add brief TL note if needed
- Match emotional tone

For each region, call create_translation_entry to create the entry.
Also call create_glossary_entry for any new character names, places, or special
terms you encounter for the first time.

Output all translations as valid JSON.""",
    tools=[tools.create_translation_entry, tools.create_glossary_entry],
)
