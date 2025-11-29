from fastapi import FastAPI, UploadFile, File, Form
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from agent import process_media, generate_images

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/generate-manual")
async def generate_manual(
    topic: str = Form(...),
    files: List[UploadFile] = File(None),
    generate_images_bool: bool = Form(True)
):
    if files is None:
        files = []

    # Generate manual text
    manual_text = await process_media(files, topic)

    # Generate images if requested
    images = []
    if generate_images_bool:
        images = await generate_images(manual_text)

    return {
        "markdown": manual_text,
        "images": images  # Array of base64 data URLs
    }


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
