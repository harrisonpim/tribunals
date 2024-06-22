.PHONY: help install test scrape_pdfs parse_pdfs process_concepts classifiers classify_documents elasticsearch index api argilla populate_argilla

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo "Targets:"
	@egrep "^(.+)\:\ ##\ (.+)" ${MAKEFILE_LIST} | column -t -c 2 -s ':#'
 
install: ## Install the project dependencies
	poetry install
	poetry run pre-commit install
	poetry run ipython kernel install --user
	poetry run pre-commit install

test: ## Run the tests
	poetry run pre-commit run -a
	poetry run pytest

scrape_pdfs: ## Scrape tribunal decision pdfs from gov.uk and save them to data/raw/pdfs
	poetry run python scripts/scrape_pdfs.py

parse_pdfs: ## Parse pdfs in data/raw/pdfs and save them to data/raw/text
	poetry run python scripts/parse_pdfs.py

process_concepts: ## Process concepts metadata in data/raw/concepts.json and save them to data/processed/concepts
	poetry run python scripts/process_concepts.py

classifiers: ## Train a classifier for each concept and save them all to data/models
	poetry run python scripts/train_classifiers.py

classify_documents: ## Use the trained classifiers to find instances of each concept in the documents and save the resulting docs (with concept spans) to data/processed/documents
	poetry run python scripts/classify_documents.py

elasticsearch: ## Start a local elasticsearch instance
	docker compose up --build -d elasticsearch

index: ## Index the documents and concepts into elasticsearch. Depends on a local running elasticsearch instance
	poetry run python scripts/index_documents.py
	poetry run python scripts/index_concepts.py

api: ## Run a local FastAPI app to query the elasticsearch index. Depends on a local running elasticsearch instance
	docker compose up --build -d api

argilla: ## Start a local argilla instance for manual concept labelling
	docker compose up --build -d argilla

populate_argilla: ## Populate the argilla instance with candidate examples to label
	poetry run python scripts/populate_argilla.py
