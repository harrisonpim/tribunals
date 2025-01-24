import random
from pathlib import Path

from src.document import Document
from src.logging import get_logger
from src.passage import Page, Passage, Sentence
from src.passage_group import PassageGroup

log = get_logger(__name__)

data_dir = Path("data/raw/text")
file_path = next(data_dir.iterdir())
document = Document.load_from_raw(file_path)

log.info(document)

# choose a random sentence object in the document
chosen_sentence = random.choice(
    [p for p in document.passages if isinstance(p, Sentence)]
)
log.info(chosen_sentence)

# find the page which contains the sentence
pages = [p for p in document.passages if isinstance(p, Page)]
page = next(
    page
    for page in pages
    if (
        chosen_sentence.start_index >= page.start_index
        and chosen_sentence.end_index <= page.end_index
    )
)
log.info(f"Sentence '{chosen_sentence.id}' is on page {page.number}")
log.info(f"Document {document.id} has {document.n_passages} passages")

# get all of the sentences on the page, and structure them into a PassageGroup
page_sentences: list[Passage] = [
    passage
    for passage in document.passages
    if (
        isinstance(passage, Sentence)
        and passage.start_index >= page.start_index
        and passage.end_index <= page.end_index
    )
]
page_sentences.sort(key=lambda x: x.start_index)
page_group = PassageGroup(passages=page_sentences)
log.info(page_group)
log.info(f"Page group has {page_group.n_passages} passages")

# generate a summary of the page
log.info("Generating summary of page")
summary = page_group.summarise()
log.info(summary)

# ask a question about the page
log.info("Asking a question about the page")
question = "Was the claimant successful in their claim?"
answer = page_group.ask_a_question(question)
log.info(answer)
