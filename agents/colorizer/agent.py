from google.adk.agents import Agent
from . import tools

colorizer_agent = Agent(
    model="gemini-2.0-flash",
    name="colorizer_agent",
    description="Colorizes B&W manga pages using character color references from Elastic",
    instruction="""You are the Colorizer Agent in MangaFlow.

You receive a translated black-and-white manga page and optional color references.

Steps:
1. Search Elastic "color-references" index for character color info for this manga
2. Build a color_description string from the results (hair, eyes, outfit, etc.)
3. Call colorize_manga_page with the B&W page image and color descriptions
4. Save the colored output using save_output_page from your context

If no color references exist in Elastic, use sensible defaults based on the
scene content and common anime color conventions (e.g., protagonist typically
has dark hair, bright eyes).""",
    tools=[tools.colorize_manga_page],
)
