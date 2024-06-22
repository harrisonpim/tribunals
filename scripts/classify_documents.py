"""
Use a set of Classifiers to find concepts in documents.

The pre-trained classifiers are loaded from data/models and the documents are loaded
from data/raw/text. After classification, the documents with concepts are saved in
data/processed/documents and the concepts are saved in data/processed/concepts.

This script assumes that documents have been parsed using the parse_pdfs.py script, and
that classifiers have been created/trained using the train_classifiers.py script.
"""

from pathlib import Path

from rich.console import Console
from rich.progress import track

from src.classifiers import Classifier
from src.document import Document

console = Console()
data_dir = Path("./data")

model_dir = data_dir / "models"
model_paths = list(model_dir.glob("*.pkl"))
classifiers = [
    Classifier.load(file)
    for file in track(
        model_paths, description="Loading classifiers", console=console, transient=True
    )
]
console.print(f"🤖 Loaded {len(classifiers)} classifiers", style="green")

raw_text_dir = data_dir / "raw" / "text"
document_paths = list(raw_text_dir.glob("*.json"))[:250]
documents = [
    Document.load_raw(file, parse_sentences=True)
    for file in track(
        document_paths, description="Loading documents", console=console, transient=True
    )
]
console.print(f"📄 Loaded {len(documents)} documents", style="green")

n_documents_with_concepts = 0
n_concepts_found = 0
for document in track(
    documents,
    description="Searching for concepts in documents",
    console=console,
    transient=True,
):
    for classifier in classifiers:
        spans = classifier.predict(document)
        document.concept_spans.extend(spans)
    if document.concept_spans:
        n_documents_with_concepts += 1
        n_concepts_found += len(document.concept_spans)

console.print(
    f"🔍 Found {n_concepts_found} concepts in {n_documents_with_concepts} documents",
    style="green",
)

documents_dir = data_dir / "processed" / "documents"
documents_dir.mkdir(parents=True, exist_ok=True)
for file in documents_dir.glob("*"):
    file.unlink()
for document in track(
    documents,
    description="Saving documents with concepts",
    console=console,
    transient=True,
):
    document.save(documents_dir / f"{document.id}.json")
