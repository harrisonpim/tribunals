import os
from typing import Optional

from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_llm_response(prompt: str, model: str = "claude-3-5-haiku-20241022") -> str:
    """Get a response from an LLM using the Anthropic API"""
    api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY environment variable not found. "
            "Please set this in your .env file or environment."
        )

    client = Anthropic(api_key=api_key)
    llm_response = client.messages.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4096,
    )

    return llm_response.content[0].text
