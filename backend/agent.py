import os
from dotenv import load_dotenv
from pydantic_ai import Agent, BinaryContent
from pydantic_ai.models.gemini import GeminiModel
from fastapi import UploadFile
from google import genai
import base64
import json

load_dotenv()

model = GeminiModel("gemini-3-pro-preview")
genai_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Agent 1: Extract manual from topic + media
manual_agent = Agent(
    model,
    system_prompt="""
You are an expert technical writer. 
Given the topic and uploaded media (images, videos, PDFs, etc.), create a clear, accurate, 
step-by-step usage manual.

IMPORTANT FORMATTING RULES:
- Start with a main title using # (h1)
- Break the manual into clear sections using ## (h2) headers
- Each major step or topic should be its own ## section
- Use bullet points and numbered lists where appropriate
- Keep language clear and instructional
- Add spacing between sections
- Each section should be substantial enough to warrant an accompanying illustration

Example structure:
# Product Name Manual

## Overview
Brief introduction to the product...

## Getting Started
Initial setup steps...

## Main Features
Detailed feature explanations...

## Troubleshooting
Common issues and solutions...

Return ONLY the markdown content, no code blocks.
"""
)

# Agent 2: Generate image prompts
image_prompt_agent = Agent(
    model,
    system_prompt="""
Analyze the manual text and generate image prompts for technical illustrations.
Each prompt should describe a clear, informative diagram or visual that would help explain that section.

IMPORTANT:
- Generate ONE prompt per ## section in the manual (excluding the first title section)
- Each prompt should be specific to the content of that section
- Focus on diagrams, illustrations, and visual aids
- Keep prompts clear and technical

Return ONLY a JSON array of strings with one prompt per section.
Example: ["Diagram showing product overview and main components", "Step-by-step assembly illustration", "Detailed view of control panel features"]
"""
)


async def generate_images(manual_text: str) -> list[str]:
    """Generate images based on manual sections and return as base64 data URLs"""

    # Count the number of ## sections (excluding the first # title)
    sections = [line for line in manual_text.split('\n') if line.startswith('## ')]
    num_images = len(sections)

    if num_images == 0:
        return []

    print(f"Generating {num_images} images for {num_images} sections...")

    # Get image prompts
    result = await image_prompt_agent.run(f"Generate {num_images} image prompts for this manual:\n\n{manual_text}")

    try:
        prompts = json.loads(result.output)
        # Ensure we have the right number of prompts
        while len(prompts) < num_images:
            prompts.append(f"Technical illustration for section {len(prompts) + 1}")
        prompts = prompts[:num_images]
    except:
        prompts = [f"Technical illustration for section {i + 1}" for i in range(num_images)]

    # Generate images
    images_base64 = []
    for i, prompt in enumerate(prompts):
        try:
            print(f"Generating image {i + 1}/{num_images}: {prompt}")
            response = genai_client.models.generate_content(
                model="gemini-3-pro-image-preview",
                contents=[prompt],
            )

            for part in response.parts:
                if part.inline_data is not None:
                    img_bytes = part.inline_data.data
                    img_str = base64.b64encode(img_bytes).decode()
                    data_url = f"data:image/png;base64,{img_str}"
                    images_base64.append(data_url)
                    print(f"Image {i + 1} generated successfully")
                    break
            else:
                images_base64.append(None)
                print(f"No image generated for prompt {i + 1}")

        except Exception as e:
            print(f"Error generating image {i + 1}: {e}")
            images_base64.append(None)

    return images_base64


async def process_media(files: list[UploadFile], prompt: str):
    """Run Gemini on uploaded media + topic and produce manual text."""
    media_content = []

    for file in files:
        await file.seek(0)
        data = await file.read()
        media_content.append(BinaryContent(
            data=data,
            media_type=file.content_type
        ))

    print("Running manual agent...")
    result = await manual_agent.run([prompt, *media_content])
    manual_text = result.output

    return manual_text


async def create_manual_with_images(manual_text: str, images: list[str]) -> str:
    """Insert image markdown into the manual at appropriate section breaks"""

    lines = manual_text.split('\n')
    result_lines = []
    image_index = 0

    for i, line in enumerate(lines):
        result_lines.append(line)

        # After each ## header (but not the first # title), insert an image if available
        if line.startswith('## ') and image_index < len(images):
            if images[image_index]:
                # Add the image markdown after the section header
                result_lines.append('')
                result_lines.append(f'![Section illustration {image_index + 1}]({images[image_index]})')
                result_lines.append('')
            image_index += 1

    return '\n'.join(result_lines)
