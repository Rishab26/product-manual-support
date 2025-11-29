import os
from dotenv import load_dotenv
from pydantic_ai import Agent, BinaryContent
from pydantic_ai.models.gemini import GeminiModel

import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = GeminiModel('gemini-3-pro-preview')

manual_agent = Agent(
    model,
    system_prompt='You are an expert technical writer. Create a clear, step-by-step usage manual for the requested topic. Use markdown formatting. If media is provided, analyze it to understand the product.',
)

from fastapi import UploadFile

async def process_media(files: list[UploadFile], prompt: str):
    media_content = []
    for file in files:
        print(f"Processing {file.filename}...")
        # Reset file pointer to beginning just in case
        await file.seek(0)
        
        content = await file.read()
        
        media_content.append(BinaryContent(
            data=content,
            media_type=file.content_type
        ))
        print(f"Processed {file.filename} ({len(content)} bytes)")

    # Run agent with files and prompt
    print("Running agent with media...")
    result = await manual_agent.run([prompt, *media_content])
    return result.output
