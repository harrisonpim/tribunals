"""
Creates a new Argilla object for each concept, and populates each one with a set of
plausible candidate texts to be labelled.

If argilla objects already exist for a concept, they are not overwritten, but are
supplemented with new candidate texts using active learning.

The raw concepts are loaded from ./data/raw/concepts.json, and pre-processed documents
(with some naive concepts identified) are loaded from ./data/processes/documents.
"""

import json
import logging
from pathlib import Path

import argilla as rg
from rich.console import Console
from rich.progress import track

from src.concept import Concept
from src.document import Document

# disable all logs from imported modules
logging.disable(logging.CRITICAL)

console = Console()
data_dir = Path("./data")

with open(data_dir / "raw" / "concepts.json") as f:
    concepts_data = json.load(f)

concepts = [
    Concept.from_dict(concept)
    for concept in track(
        concepts_data, description="🧠 Loading concepts...", transient=True
    )
]
console.print(f"🧠 Loaded {len(concepts_data)} concepts", style="green")

documents_dir = data_dir / "processed" / "documents"
file_paths = list(documents_dir.glob("*.json"))
documents = [
    Document.load(file)
    for file in track(file_paths, description="📄 Loading documents...", transient=True)
]
console.print(f"📄 Loaded {len(documents)} documents", style="green")

# find passages which contain each concept
concept_passages = {concept.id: [] for concept in concepts}
for document in track(
    documents, description="Extracting concept passages", transient=True
):
    if not document.concept_spans:
        continue
    concept_span_iterable = iter(document.concept_spans)
    concept_span = next(concept_span_iterable)
    for sentence_span in document.sentence_spans:
        if (
            sentence_span.start_index <= concept_span.start_index
            and sentence_span.end_index >= concept_span.end_index
        ):
            sentence = document.text[
                sentence_span.start_index : sentence_span.end_index
            ]
            concept_passages[concept_span.identifier].append(sentence)
            try:
                concept_span = next(concept_span_iterable)
            except StopIteration:
                break

console.print("🔍 Found passages containing each concept:", style="green")
for concept_id, passages in concept_passages.items():
    console.print(f"  • {concept_id}: {len(passages)} passages")

with console.status("🔌 Connecting to Argilla..."):
    rg.init(
        api_url="http://localhost:6900",
        api_key="argilla.apikey",
        workspace="argilla",
    )
console.print("🔌 Connected to Argilla", style="green")


created_datasets = []
skipped_datasets = []
for concept in track(
    concepts, description="Populating Argilla objects", transient=True, console=console
):
    try:
        dataset = rg.FeedbackDataset.from_argilla(
            name=concept.preferred_label, workspace="argilla"
        )
    except ValueError:
        pass
    else:
        dataset.delete()

    candidate_passages = concept_passages[concept.id]
    if len(candidate_passages) == 0:
        skipped_datasets.append(concept.preferred_label)
        continue
    dataset = rg.FeedbackDataset.for_text_classification(
        labels=[concept.preferred_label, "not " + concept.preferred_label],
        multi_label=False,
        use_markdown=True,
    )
    dataset.add_records(
        [rg.FeedbackRecord(fields={"text": passage}) for passage in candidate_passages]
    )
    dataset.push_to_argilla(
        name=concept.preferred_label, workspace="argilla", show_progress=False
    )
    created_datasets.append(concept.preferred_label)

if skipped_datasets:
    console.print("📚 Skipped concepts with no candidate passages:", style="green")
    for concept in skipped_datasets:
        console.print(f"  • {concept}")
if created_datasets:
    console.print(
        "📚 Created Argilla objects for the following concepts:", style="green"
    )
    for concept in created_datasets:
        console.print(f"  • {concept}")

console.print("🎉 All done! You can now use Argilla to start labelling.", style="green")
