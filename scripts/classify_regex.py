"""
Use a RegexClassifier to find concepts in documents.

The concepts are loaded from data/raw/concepts.json and the documents are loaded
from data/raw/text. After classification, the documents with concepts are saved in
data/processed/documents and the concepts are saved in data/processed/concepts.
"""

from pathlib import Path

from rich.console import Console
from rich.progress import track

from src.classifiers import RegexClassifier
from src.concept import Concept
from src.document import Document

console = Console()
data_dir = Path("./data")
raw_text_dir = data_dir / "raw" / "text"
files = list(raw_text_dir.glob("*.json"))

documents = [
    Document.load_raw(file, parse=False)
    for file in track(
        files, description="Loading documents", console=console, transient=True
    )
]
console.print(f"📄 Loaded {len(files)} documents", style="green")

concepts_dir = data_dir / "processed" / "concepts"
concepts = [Concept.load(file) for file in concepts_dir.glob("*.json")]
console.print(f"🧠 Loaded {len(concepts)} concepts", style="green")

classifiers = [RegexClassifier(concept) for concept in concepts]
console.print(f"🤖 Created {len(classifiers)} classifiers", style="green")

documents_with_concepts = []
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
        documents_with_concepts.append(document)

console.print(
    f"🔍 Found concepts in {len(documents_with_concepts)} documents", style="green"
)

documents_dir = data_dir / "processed" / "documents"
documents_dir.mkdir(parents=True, exist_ok=True)
for file in documents_dir.glob("*"):
    file.unlink()
for document in documents_with_concepts:
    document.save(documents_dir / f"{document.id}.json")
