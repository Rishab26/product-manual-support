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
