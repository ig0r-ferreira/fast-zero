FROM python:3.11-slim
ENV POETRY_VIRTUALENVS_IN_PROJECT true
ENV POETRY_INSTALLER_MAX_WORKERS 10

WORKDIR /app
COPY pyproject.toml poetry.lock ./

RUN pip install poetry && poetry install -n --no-root --no-directory

COPY . .

RUN poetry install -n --no-ansi

EXPOSE 8000
CMD ["poetry", "run", "uvicorn", "--host", "0.0.0.0", "todoapi.main:app"]