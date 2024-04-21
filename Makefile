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
