.PHONY: install test scrape_pdfs parse_pdfs elasticsearch kibana index api

install:
	poetry install
	poetry run pre-commit install
	poetry run ipython kernel install --user
	poetry run pre-commit install

test:
	poetry run pre-commit run -a
	poetry run pytest

scrape_pdfs:
	poetry run python scripts/scrape_pdfs.py

parse_pdfs:
	poetry run python scripts/parse_pdfs.py

process_concepts:
	poetry run python scripts/process_concepts.py

classifiers:
	poetry run python scripts/train_classifiers.py

classify_documents:
	poetry run python scripts/classify_documents.py

elasticsearch:
	docker-compose up -d elasticsearch

kibana:
	docker-compose up -d kibana

index:
	poetry run python scripts/index_documents.py
	poetry run python scripts/index_concepts.py

api:
	docker-compose up --build -d api
