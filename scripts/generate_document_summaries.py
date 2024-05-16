"""
Use an LLM to generate summaries for the documents in the dataset.

Save them to the same file as the original document, with a new `summary` property.
"""

import os
import time
from pathlib import Path

from anthropic import Anthropic, RateLimitError
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import track

from src.document import Document

console = Console()

load_dotenv()

data_dir = Path("data")
documents_dir = data_dir / "processed" / "documents"
file_paths = list(documents_dir.glob("*.json"))
documents = [
    Document.load(file, parse_sentences=False)
    for file in track(file_paths, description="📄 Loading documents...", transient=True)
]
console.print(f"📄 Loaded {len(documents)} documents", style="green")

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def generate_summary(text: str) -> str:
    try:
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            temperature=0,
            system="Provide a one-paragraph blurb/description/summary for a document.",
            messages=[
                {"role": "user", "content": [{"type": "text", "text": document.text}]},
                {
                    "role": "assistant",
                    "content": [
                        {"type": "text", "text": "Here is the document summary:"}
                    ],
                },
            ],
        )
        return message.content[0].text
    except RateLimitError:
        print("Rate limit exceeded. Waiting for 60 seconds...")
        time.sleep(60)
        return generate_summary(text)


for document in track(
    documents,
    description="🤓 Reading documents and writing summaries...",
    transient=True,
):
    if document.summary:
        continue
    document.summary = generate_summary(document.text)
    document.save(documents_dir / f"{document.id}.json")

console.print(
    f"🤓 Summarized {len(documents)} documents and saved them to {documents_dir}",
    style="green",
)
