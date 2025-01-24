import random
from pathlib import Path

from rich.console import Console

from src.document import Document
from src.passage import Page

console = Console()

data_dir = Path("data/raw/text")
file_path = next(data_dir.iterdir())
document = Document.load_from_raw(file_path)

console.print(document)

# choose a random non-page passage object in the document
chosen_passage = random.choice(
    [p for p in document.passages if not isinstance(p, Page)]
)
console.print(chosen_passage)

# find the page which contains the non-page passage
pages = [p for p in document.passages if isinstance(p, Page)]
page = next(
    p
    for p in pages
    if (
        chosen_passage.start_index >= p.start_index
        and chosen_passage.end_index <= p.end_index
    )
)
console.print(f"Passage '{chosen_passage.id}' is on page {page.number}")
