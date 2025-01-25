import random
from pathlib import Path

from src.chunking import split_text_into_sentences
from src.document import Document
from src.logging import get_logger
from src.passage import Page, Passage, Sentence
from src.passage_group import PassageGroup

log = get_logger(__name__)

data_dir = Path("data/raw/text")
file_path = next(data_dir.iterdir())
log.info(f'Loading document from "{file_path}"')
document = Document.load_from_raw(file_path)


sentences = [
    sentence
    for page in document.passages
    for sentence in split_text_into_sentences(page)
]
document.passages.extend(sentences)
log.info(document)

# choose a random sentence object in the document
chosen_sentence = random.choice(
    [p for p in document.passages if isinstance(p, Sentence) and len(p.text)]
)
log.info(chosen_sentence)
log.info(chosen_sentence.text)
log.info(chosen_sentence.transformation_history)

# find the page which contains the sentence using the history of the sentence
page_ids = [
    parent.id
    for event in chosen_sentence.transformation_history
    for parent in event.parents
    if parent.type == "Page"
]
log.info(page_ids)
page_id = page_ids[0]
page = next(p for p in document.passages if isinstance(p, Page) and p.id == page_id)
log.info(f"Sentence '{chosen_sentence.id}' is on page {page.number}")
log.info(f"Document {document.id} has {document.n_passages} passages")

page_sentences: list[Passage] = [
    passage
    for passage in document.passages
    if (
        isinstance(passage, Sentence)
        and page_id
        in set(
            parent.id
            for event in passage.transformation_history
            for parent in event.parents
        )
    )
]

page_group = PassageGroup(passages=page_sentences)
log.info(f"Passage group {page_group.id} has {page_group.n_passages} passages")


# generate a summary of the page
log.info("Generating summary of page")
summary = page_group.summarise()
log.info(summary)

# ask a question about the page
log.info("Asking a question about the page")
question = "Was the claimant successful in their claim?"
answer = page_group.ask_a_question(question)
log.info(answer)
