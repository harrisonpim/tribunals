from typing import TYPE_CHECKING

from src.llm import get_llm_response

if TYPE_CHECKING:
    # only import this circular dependency if we're running in a type-checking
    # environment, eg for pyright
    from src.passage_group import PassageGroup


def summarise(
    passage_group: "PassageGroup", model: str = "claude-3-5-haiku-20241022"
) -> str:
    prompt = "Summarise the following text: \n\n" + passage_group.text
    return get_llm_response(prompt, model)
