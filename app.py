"""MangaFlow FastAPI app — upload panel → stream progress → return result."""
import asyncio
import json
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pipeline import run_pipeline

app = FastAPI(title="MangaFlow", docs_url=None, redoc_url=None)

# Serve static files (HTML/CSS/JS assets)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def index():
    with open("static/index.html", encoding="utf-8") as f:
        return f.read()


@app.get("/health")
async def health():
    return {"status": "ok", "service": "mangaflow"}


@app.post("/api/process")
async def process_panel(
    file: UploadFile = File(...),
    translate: str = Form(default="true"),
    colorize: str = Form(default="true"),
    manga_title: str = Form(default="Unknown"),
):
    """
    Accept a manga panel image, run the full pipeline, stream SSE progress events.
    Final event: {"step": "done", "image_b64": "...", "translations": [...]}
    """
    image_bytes = await file.read()
    do_translate = translate.lower() == "true"
    do_colorize = colorize.lower() == "true"

    # Queue bridges the sync generator thread → async SSE stream
    queue: asyncio.Queue = asyncio.Queue()
    loop = asyncio.get_event_loop()

    def run_sync():
        try:
            for event in run_pipeline(image_bytes, do_translate, do_colorize, manga_title):
                asyncio.run_coroutine_threadsafe(queue.put(event), loop)
        except Exception as exc:
            asyncio.run_coroutine_threadsafe(
                queue.put({"step": "error", "msg": str(exc)}), loop
            )
        finally:
            asyncio.run_coroutine_threadsafe(queue.put(None), loop)  # sentinel

    async def stream():
        loop.run_in_executor(None, run_sync)
        while True:
            event = await queue.get()
            if event is None:
                break
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")
