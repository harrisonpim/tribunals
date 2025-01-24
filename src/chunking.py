import spacy

from src.passage import Passage


def split_text_into_sentences(text: str) -> list[Passage]:
    nlp = spacy.blank("en")
    nlp.add_pipe("sentencizer")

    return [
        Passage(
            text=sent.text,
            zoom_level=0,
            start_index=sent.start_char,
            end_index=sent.end_char,
        )
        for sent in nlp(text).sents
    ]
