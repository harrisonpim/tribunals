import json
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
    Document.load(file)
    for file in track(
        files, description="Loading documents", console=console, transient=True
    )
]
console.print(f"📄 Loaded {len(files)} documents", style="green")

with open("data/raw/concepts.json") as f:
    concepts_data = json.load(f)
console.print(f"🧠 Loaded {len(concepts_data)} concepts", style="green")

concepts = [Concept.from_dict(concept) for concept in concepts_data]
concepts_dir = data_dir / "processed" / "concepts"
concepts_dir.mkdir(parents=True, exist_ok=True)
for file in concepts_dir.glob("*"):
    file.unlink()
for concept in concepts:
    concept.save(concepts_dir / f"{concept.id}.json")

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
        spans = classifier.predict(document.text)
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
