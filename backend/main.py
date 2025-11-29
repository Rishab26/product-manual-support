from fastapi import FastAPI, UploadFile, File, Form
from typing import List
from pydantic import BaseModel
from agent import manual_agent, process_media
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ManualRequest(BaseModel):
    topic: str

@app.post("/generate-manual")
async def generate_manual(
    topic: str = Form(...),
    files: List[UploadFile] = File(None)
):
    if files is None: files = []
    # Pass UploadFile objects directly to process_media
    manual_text = await process_media(files, topic)
    return {"manual": manual_text}

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

# Mount the generated images directory
if os.path.exists("generated_images"):
    app.mount("/images", StaticFiles(directory="generated_images"), name="images")
elif not os.path.exists("generated_images"):
    # Create the directory if it doesn't exist
    os.makedirs("generated_images", exist_ok=True)
    app.mount("/images", StaticFiles(directory="generated_images"), name="images")

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
