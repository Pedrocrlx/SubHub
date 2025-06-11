FROM python:3.12

RUN pip install poetry

WORKDIR /app

COPY . .

RUN poetry install

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Ordem dos comandos no Dockerfile importam
# Apartir do momento em que defino WORKDIR, todo '.' passado à direita dos meus argumentos de meus comandos; são <WORKDIR>
# Se estou usando Poetry, devo declarar as dependências em pyproject.toml
