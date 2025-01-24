from typing import TYPE_CHECKING

from src.llm import get_llm_response

if TYPE_CHECKING:
    # only import this circular dependency if we're running in a type-checking
    # environment, eg for pyright
    from src.passage_group import PassageGroup


def rag(
    passage_group: "PassageGroup",
    question: str,
    model: str = "claude-3-5-haiku-20241022",
) -> str:
    prompt = (
        "Based on the following sources, answer the following question:\n\n"
        + "<sources>\n"
        + "\n".join(
            [f"<source>{passage.text}</source>" for passage in passage_group.passages]
        )
        + "\n</sources>\n"
        + f"<question>{question}</question>\n\n"
    )

    return get_llm_response(prompt, model)
