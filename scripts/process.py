"""
Extract text from PDFs

Transforms the text of every PDF in the data/raw folder into a json file containing a 
list of strings, one for each page of the PDF. The json files are saved in the 
data/processed folder.
"""

import pdfplumber
from pathlib import Path
import json
from src.logging import get_logger

logger = get_logger(__name__)

data_dir = Path("./data")
raw_dir = data_dir / "raw"
processed_dir = data_dir / "processed"
processed_dir.mkdir(parents=True, exist_ok=True)

for pdf_path in raw_dir.glob("*.pdf"):
    logger.info(f"Processing {pdf_path.stem}")
    with pdfplumber.open(pdf_path) as pdf:
        text = [page.extract_text() for page in pdf.pages]

    output_path = processed_dir / f"{pdf_path.stem}.json"
    with open(output_path, "w") as f:
        json.dump(text, f)
        logger.info(f"Saved {output_path}")
