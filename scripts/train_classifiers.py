from pathlib import Path

from rich.console import Console
from rich.progress import track

from src.classifiers import ClassifierFactory
from src.concept import Concept

console = Console()

data_dir = Path("./data")
model_dir = data_dir / "models"
model_dir.mkdir(parents=True, exist_ok=True)

concepts_dir = data_dir / "processed" / "concepts"
concepts = [Concept.load(file) for file in concepts_dir.glob("*.json")]
console.print(f"🧠 Loaded {len(concepts)} concepts", style="green")

classifiers = [
    ClassifierFactory.create(concept)
    for concept in track(
        concepts, description="Training classifiers", console=console, transient=True
    )
]
console.print(f"🤖 Created/trained {len(classifiers)} classifiers:", style="green")
for classifier in classifiers:
    console.print(f"  - {classifier}")

for classifier in track(
    classifiers, description="Saving classifiers", console=console, transient=True
):
    classifier.save(model_dir / f"{classifier.concept.id}.pkl")
console.print(f"🥫 Saved {len(classifiers)} classifiers to {model_dir}", style="green")
