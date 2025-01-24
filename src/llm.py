import os

from anthropic import Anthropic


def get_llm_response(prompt: str, model: str = "claude-3-5-haiku-20241022") -> str:
    """
    Get a response from the LLM using the Anthropic API.

    Args:
        prompt: The prompt to send to the model
        model: The model to use, defaults to claude-3-5-haiku

    Returns:
        The model's response as a string
    """
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    llm_response = client.messages.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4096,
    )

    return llm_response.content[0].text
