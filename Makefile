.PHONY: install test scrape process

install:
	poetry install
	poetry run pre-commit install
	poetry run ipython kernel install --user

test:
	poetry run pre-commit run -a
	poetry run pytest

scrape:
	poetry run scrapy runspider scripts/scrape.py

process:
	poetry run python scripts/process.py

elasticsearch:
	docker-compose up -d elasticsearch
	docker-compose up -d kibana

elasticsearch-down:
	docker-compose down

index:
	poetry run python scripts/index.py
