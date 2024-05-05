FROM python:3.10 as requirements-stage

COPY ./pyproject.toml /pyproject.toml
COPY ./poetry.lock /poetry.lock

RUN pip install poetry

RUN poetry config virtualenvs.create false

RUN poetry export -f requirements.txt --output /tmp/requirements.txt --without-hashes

FROM python:3.10

WORKDIR /api

COPY --from=requirements-stage /tmp/requirements.txt /api/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /api/requirements.txt

COPY ./api/app /api/app

CMD ["fastapi", "run", "app/main.py", "--port", "3000"]
