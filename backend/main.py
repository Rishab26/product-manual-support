# main.py
from fastapi import FastAPI, UploadFile, File, Form
from typing import List
from pydantic import BaseModel
from agent import process_media, structure_as_markdown
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ManualRequest(BaseModel):
    topic: str


class ManualResponse(BaseModel):
    manual_markdown: str
    manual_html: str
    image_urls: list[str]


@app.post("/generate-manual")
async def generate_manual(
        topic: str = Form(...),
        files: List[UploadFile] = File(None),
        generate_images: bool = Form(True)
):
    if files is None:
        files = []

    # Generate manual
    manual_text, manual_with_markers, image_urls = await process_media(
        files, topic, generate_images
    )
    breakpoint()
    # Convert to markdown
    markdown = await structure_as_markdown(manual_text, image_urls)
    breakpoint()
    # Save markdown to temp file
    file_id = str(uuid.uuid4())
    md_path = f"/temp_uploads/manual_{file_id}.md"

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(markdown)
    breakpoint()
    return FileResponse(
        md_path,
        media_type="text/markdown",
        filename="manual.md"
    )



@app.get("/health")
async def health():
    return {"status": "ok"}

# Serve static files
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# Mount the static directory (frontend build)
# We assume the frontend build is copied to a 'static' directory in the container
if os.path.exists("static"):
    app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")

    @app.get("/")
    async def serve_root():
        return FileResponse("static/index.html")

    @app.get("/{full_path:path}")
    async def catch_all(full_path: str):
        # Check if file exists in static root (e.g. favicon.ico)
        if os.path.isfile(f"static/{full_path}"):
             return FileResponse(f"static/{full_path}")
        # Otherwise return index.html for SPA routing
        return FileResponse("static/index.html")
