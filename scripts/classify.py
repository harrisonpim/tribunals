from rich.progress import track
from rich.console import Console
from src.classifiers import RegexClassifier
from src.document import Document
from src.concept import Concept
import json
from pathlib import Path
import random

console = Console()
data_dir = Path("data/processed")
files = list(data_dir.glob("*.json"))
console.print(f"📄 Loaded {len(files)} documents", style="green")

with open("data/concepts.json") as f:
    concepts_data = json.load(f)
console.print(f"🧠 Loaded {len(concepts_data)} concepts", style="green")

concepts = [Concept.from_dict(concept) for concept in concepts_data]
classifiers = [RegexClassifier(concept) for concept in concepts]
console.print(f"🤖 Created {len(classifiers)} classifiers", style="green")

documents_with_concepts = []
for file in track(
    files, description="Searching for concepts in documents", console=console
):
    document = Document.load(file)
    for classifier in classifiers:
        spans = classifier.predict(document.text)
        document.concept_spans.extend(spans)
    if document.concept_spans:
        documents_with_concepts.append(document)

console.print(
    f"🔍 Found concepts in {len(documents_with_concepts)} documents", style="green"
)

random_document = random.choice(documents_with_concepts)
console.print(random_document.title, style="bold white on blue")
for span in random_document.concept_spans:
    console.print(f"  {span.start_index}-{span.end_index}:")
    console.print(
        f"    {random_document.text[span.start_index-20:span.start_index]}",
        end="",
        highlight=False,
    )
    console.print(
        f"{random_document.text[span.start_index:span.end_index]}",
        end="",
        style="bold white",
        highlight=False,
    )
    console.print(
        f"{random_document.text[span.end_index:span.end_index+20]}",
        highlight=False,
    )
