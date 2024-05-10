import json
from pathlib import Path

from rich.console import Console

from src.concept import Concept

console = Console()
data_dir = Path("./data")

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
