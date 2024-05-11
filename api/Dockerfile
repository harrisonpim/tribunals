FROM python:3.10

WORKDIR /api

COPY ./pyproject.toml /api/pyproject.toml
COPY ./poetry.lock /api/poetry.lock

RUN pip install poetry

RUN poetry install --with api

ENV PATH="/root/.local/bin:${PATH}"

COPY ./src/ /api/src/

COPY ./api/app /api/app

CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3000"]
