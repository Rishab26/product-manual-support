from fastapi import FastAPI, UploadFile, File, Form
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from agent import process_media, generate_images, create_manual_with_images

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
        files: List[UploadFile] = File(None)
):
    if files is None:
        files = []

    # Step 1: Generate manual text from media + topic
    print(f"Generating manual for topic: {topic}")
    manual_text = await process_media(files, topic)

    # Step 2: Generate images based on the manual sections
    print("Generating images for manual sections...")
    images = await generate_images(manual_text)

    # Step 3: Insert images into the manual markdown
    final_manual = await create_manual_with_images(manual_text, images)

    return {
        "manual": final_manual
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
