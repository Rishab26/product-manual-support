import os
from dotenv import load_dotenv
from pydantic_ai import Agent, BinaryContent
from pydantic_ai.models.gemini import GeminiModel
from fastapi import UploadFile
import google.generativeai as genai
from google import genai as new_genai
from google.genai import types
import json
import base64
import io

load_dotenv()

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = GeminiModel('gemini-3-pro-preview')

# Create the new GenAI client for image generation
genai_client = new_genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

manual_agent = Agent(
    model,
    system_prompt='You are an expert technical writer. Create a clear, step-by-step usage manual using the '
                  'provided media, analyze it to understand the product.',
)

html_structure_agent = Agent(
    model,
    system_prompt='''
You are an expert technical writer.

Convert the provided manual into a **clean, well-formatted Markdown document**.

Requirements:
- Use clean markdown sections
- Use readable headings (#, ##, ###)
- Add spacing, lists, tables when helpful
- Add placeholders {{IMAGE_0}}, {{IMAGE_1}}, etc. where images should appear
- Do NOT include HTML unless absolutely necessary
- NO code blocks
Return ONLY the final markdown content.
'''
)


image_prompt_agent = Agent(
    model,
    system_prompt='''Analyze the manual and generate image prompts for illustrations.
    Each prompt should describe a diagram, illustration, or visual that would help explain the manual.
    Return ONLY a JSON array of strings, nothing else.
    Example: ["A diagram showing the product assembly steps", "An illustration of the control panel"]'''
)


async def generate_manual_images(manual_text: str, num_images: int = 3) -> list[str]:
    """Generate images for the manual using Google GenAI"""

    # First, use agent to extract key concepts for image generation
    result = await image_prompt_agent.run(f"Generate {num_images} image prompts for this manual:\n\n{manual_text}")

    try:
        prompts = json.loads(result.output)
    except:
        # Fallback prompts
        prompts = [
            f"Technical illustration for product manual, step {i + 1}, clean diagram style"
            for i in range(num_images)
        ]

    # Generate images using the new Google GenAI client
    image_urls = []
    for prompt in prompts[:num_images]:
        try:
            print(f"Generating image with prompt: {prompt}")

            response = genai_client.models.generate_content(
                model="gemini-3-pro-image-preview",
                contents=[prompt],
            )

            # Process the response parts
            for part in response.parts:
                if part.inline_data is not None:
                    # Get raw bytes from inline_data
                    raw_bytes = part.inline_data.data

                    # Base64 encode directly
                    img_str = base64.b64encode(raw_bytes).decode()
                    data_url = f"data:image/png;base64,{img_str}"

                    image_urls.append(data_url)
                    print("Generated image successfully")
                    break
            else:
                # No image found in response
                image_urls.append("")
                print("No image generated")

        except Exception as e:
            print(f"Error generating image: {e}")
            import traceback
            traceback.print_exc()
            image_urls.append("")

    return image_urls


async def process_media(files: list[UploadFile], prompt: str, generate_images: bool = False):
    media_content = []
    for file in files:
        print(f"Processing {file.filename}...")
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
    manual_text = result.output

    # Generate images if requested
    image_urls = []
    if generate_images:
        print("Generating manual images...")
        image_urls = await generate_manual_images(manual_text)

        # Insert image placeholders into manual
        manual_with_images = manual_text
        for i, url in enumerate(image_urls):
            # Insert image markers that will be replaced in HTML
            manual_with_images += f"\n\n{{{{IMAGE_{i}}}}}\n\n"
    else:
        manual_with_images = manual_text

    return manual_text, manual_with_images, image_urls


async def structure_as_markdown(manual_text: str, image_urls: list[str]) -> str:
    """Convert manual to Markdown and insert image placeholders"""

    # Add image markers to manual text
    manual_with_markers = manual_text
    for i in range(len(image_urls)):
        manual_with_markers += f"\n\n{{{{IMAGE_{i}}}}}\n\n"

    print("Structuring manual as Markdown...")
    result = await html_structure_agent.run(manual_with_markers)
    markdown = result.output.strip()

    # Replace markers with image markdown
    for i, url in enumerate(image_urls):
        if url:
            md_tag = f"![Manual illustration {i + 1}]({url})"
        else:
            md_tag = f"> **Image {i+1} placeholder**"
        markdown = markdown.replace(f"{{{{IMAGE_{i}}}}}", md_tag)

    return markdown

