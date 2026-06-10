from google.adk.agents import Agent, SequentialAgent
from agents.detector.agent import detector_agent
from agents.translator.agent import translator_agent
from agents.cleaner.agent import cleaner_agent
from agents.colorizer.agent import colorizer_agent
from agents.quality.agent import quality_agent

# Sequential pipeline for a single manga page
page_pipeline = SequentialAgent(
    name="page_translation_pipeline",
    description="Processes a single manga page through detect → translate → clean → colorize → quality",
    sub_agents=[
        detector_agent,
        translator_agent,
        cleaner_agent,
        colorizer_agent,
        quality_agent,
    ],
)

# Root orchestrator handles multi-page chapters
root_agent = Agent(
    model="gemini-2.0-flash",
    name="mangaflow_orchestrator",
    description=(
        "MangaFlow: AI-powered manga translation and colorization. "
        "Orchestrates five specialized agents (Detector, Translator, Cleaner, "
        "Colorizer, Quality Checker) to translate manga from Japanese to English."
    ),
    instruction="""You are MangaFlow, an AI manga translation system.

When a user gives you a manga translation task:
1. Identify the manga pages to process
2. For each page, delegate to the page_translation_pipeline which runs:
   a. Detector → find all text regions
   b. Translator → translate JP→EN with glossary/memory consistency
   c. Cleaner → remove JP text, add EN text
   d. Colorizer → colorize if requested
   e. Quality → assess output quality
3. Provide a final summary with:
   - Pages processed
   - Quality scores
   - Output file locations
   - Glossary additions made
   - Any issues flagged""",
    sub_agents=[page_pipeline],
)
