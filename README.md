# Employment appeal tribunal decisions

Scraping tribunal decision documents from [gov.uk](https://www.gov.uk/employment-appeal-tribunal-decisions) and making them super searchable.

This project is written in python, with dependencies managed by poetry. Core jobs and services are managed by a [Makefile](./Makefile) and a [docker-compose.yml](./docker-compose.yml) file.

There's also a next.js [webapp](./webapp) which provides a simple interface to search the decisions.

## Getting started

Start by running `make install` to install the project dependencies, and then take a look at the other available core commands with `make help`. This should give you a good idea of the project structure and the overall workflow.
