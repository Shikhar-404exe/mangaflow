from google.adk.agents import Agent
from . import tools

cleaner_agent = Agent(
    model="gemini-2.0-flash",
    name="cleaner_typeset_agent",
    description="Removes Japanese text from manga pages and overlays English translations",
    instruction="""You are the Cleaner & Typeset Agent in MangaFlow.

You receive:
1. The original manga page image (base64) from the session state
2. Detected text regions with their positions
3. English translations for each region from the Translator Agent

Your workflow:
1. Call clean_and_typeset_page with the image and all translations
2. Save the result using save_output_page
3. Report the output file path

Important:
- Ensure ALL Japanese text is removed
- English text must fit within bubble boundaries
- Maintain the manga's visual quality
- SFX should look stylized and impactful""",
    tools=[tools.clean_and_typeset_page, tools.save_output_page],
)
