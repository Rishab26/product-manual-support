import os
from dotenv import load_dotenv
from pydantic_ai import Agent, BinaryContent, RunContext
from pydantic_ai.models.gemini import GeminiModel

import google.generativeai as genai
from google import genai as new_genai

load_dotenv()

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = GeminiModel('gemini-3-pro-preview')

genai_client = new_genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))


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
Create a comprehensive and detailed user manual based on the information you have received about a product from a colleague.
# Formatting Constraints
Use valid Markdown formatting.
IMPORTANT: Structure each feature as a level 2 heading (## Feature Name).
# Output Structure
Structure the usage manual into sections, like you would normally expect.

IMPORTANT: Select and present ONLY the 5 most relevant and important features from the input.
Prioritize the features that are most essential for users to understand and use the product effectively.

The first section should be an introduction/overview without a feature-specific focus.
Then present the 5 most relevant features as separate sections.

For each feature section provide:
1. A level 2 heading (## Feature Name)
2. A description of the feature with detailed text
3. A schematic showing the feature in a simple line only sketch (use the generate_image tool)

CRITICAL: You MUST use the generate_image tool for EVERY feature section (not the intro) to create a schematic.
Each feature section MUST have both text description AND an image.

Example structure:
## Introduction
Overview of the product...

## Feature Name
Detailed description of the feature...
- How it works
- How to use it
![schematic](/images/...)

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
    if not prompt and media_content:
        prompt = "Create a manual based on the provided media."
    
    result = await manual_agent.run([prompt, *media_content])
    final_result = await master_agent.run([result.output])
    return final_result.output

@master_agent.tool
async def generate_image(context: RunContext, prompt: str):
    """
    Use this tool to generate sketches of a product feature.

    Keep the sketches simple like in an IKEA catalogue.
    
    Returns a markdown image reference that can be embedded in the manual.
    """
    import uuid
    import base64
    from pathlib import Path
    
    # Create directory for generated images if it doesn't exist
    images_dir = Path("generated_images")
    images_dir.mkdir(exist_ok=True)
    
    # Generate the image
    response = genai_client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=[prompt],
    )
    
    # Extract image data from response
    # The response should contain image data in the candidates
    if response.candidates and len(response.candidates) > 0:
        candidate = response.candidates[0]
        if candidate.content and candidate.content.parts:
            for part in candidate.content.parts:
                # Check if this part contains image data
                if hasattr(part, 'inline_data') and part.inline_data:
                    # Generate unique filename
                    image_id = str(uuid.uuid4())
                    
                    # Determine file extension from mime type
                    mime_type = part.inline_data.mime_type
                    ext = mime_type.split('/')[-1] if '/' in mime_type else 'png'
                    filename = f"{image_id}.{ext}"
                    filepath = images_dir / filename
                    
                    # Save the image
                    image_data = part.inline_data.data
                    with open(filepath, 'wb') as f:
                        f.write(image_data)
                    
                    # Return markdown image reference
                    return f"![Generated schematic for: {prompt}](/images/{filename})"
    
    # If no image was generated, return a message
    return f"[Image generation failed for: {prompt}]"