import os
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel

load_dotenv()

model = GeminiModel('gemini-3-pro-preview')

manual_agent = Agent(
    model,
    system_prompt='You are an expert technical writer. Create a clear, step-by-step usage manual for the requested topic. Use markdown formatting.',
)
