import os
from dotenv import load_dotenv
from pydantic_ai import Agent, BinaryContent
from pydantic_ai.models.gemini import GeminiModel

import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = GeminiModel('gemini-3-pro-preview')

input_agent_system_prompt = """

# Role
You are a Senior Technical Writer with great experience writing documentation for non-technical consumers. Your tone is helpful, concise, and informative.
# Task
Create a comprehensive corpus of knowledge for the user's requested topic, uploaded image, or video.
# Formatting Constraints
Use valid Markdown.
# Output Structure
Provide detailed information about the product based on the user information.
Describe all the features of the product that you can see and how to use them if you know. 
If you do not know, describe the feature as best as you can, without adding any false information or extra content.

The goal is to provide a comprehensive and accurate corpus of knowledge from which someone will then write the usage manual.

"""

master_agent_system_prompt = """

# Role
You are a Senior Technical Writer with great experience writing documentation for non-technical consumers. Your tone is helpful, concise, and informative.
# Task
Create a comprehensive and detailed user manual based on the information you have received about a product from a colleage.
# Formatting Constraints
Use valid Markdown formatting.
# Output Structure
Structure the usage manual into sections, like you would normally expect.
Each section should describe one feature of the product.

For each section and feature provide:
- A description of the feature

Be as detailed as possible, without adding any information that is not verified.
"""
# 
master_agent = Agent(
    model,
    system_prompt=master_agent_system_prompt,
)

manual_agent = Agent(
    model,
    system_prompt=input_agent_system_prompt,
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
    final_result = await master_agent.run([result.output])
    return final_result.output
