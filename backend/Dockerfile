FROM python:3.12

RUN pip install poetry

WORKDIR /workspace

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create true &&\
    poetry config virtualenvs.in-project true &&\
    poetry install --no-root

COPY . .

ENV PATH="/app/.venv/bin:$PATH" 

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Ordem dos comandos no Dockerfile importam
# Apartir do momento em que defino WORKDIR, todo '.' passado à direita dos meus argumentos de meus comandos; são <WORKDIR>
# Se estou usando Poetry, devo declarar as dependências em pyproject.toml
