import os

from anthropic import Anthropic


def summarise(text: str, model: str = "claude-3-5-haiku-20241022") -> str:
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    prompt = "Summarise the following text: " + text
    llm_response = client.messages.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4096,
    )

    return llm_response.content[0].text
