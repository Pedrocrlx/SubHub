FROM python:3.12

RUN pip install poetry

RUN poetry install uvicorn

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

COPY . /app

EXPOSE 8000

CMD ["poetry", "run ""uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]


