import os

from anthropic import Anthropic

from src.passage import Passage


def rag(
    passages: list[Passage], question: str, model: str = "claude-3-5-haiku-20241022"
) -> str:
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    prompt = (
        "Based on the following sources, answer the following question:\n\n"
        + f"<question>{question}</question>\n\n"
        + "<sources>\n"
        + "\n".join([f"<source>{passage.text}</source>" for passage in passages])
        + "\n</sources>"
    )

    llm_response = client.messages.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4096,
    )

    return llm_response.content[0].text
