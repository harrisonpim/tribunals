import random
from pathlib import Path

from src.document import Document
from src.logging import get_logger
from src.passage import Page, Sentence

log = get_logger(__name__)

data_dir = Path("data/raw/text")
file_path = next(data_dir.iterdir())
document = Document.load_from_raw(file_path)

log.info(document)


# choose a random non-page passage object in the document
chosen_sentence = random.choice(
    [p for p in document.passages if isinstance(p, Sentence)]
)
log.info(chosen_sentence)

# find the page which contains the non-page passage
pages = [p for p in document.passages if isinstance(p, Page)]
page = next(
    p
    for p in pages
    if (
        chosen_sentence.start_index >= p.start_index
        and chosen_sentence.end_index <= p.end_index
    )
)
log.info(f"Passage '{chosen_sentence.id}' is on page {page.number}")
