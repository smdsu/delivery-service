FROM python:3.10-slim-bullseye

WORKDIR /app

RUN python -m pip install --no-cache-dir --upgrade pip

COPY poetry.lock pyproject.toml ./

RUN python -m pip install --no-cache-dir poetry==2.1.2 \
    && poetry config virtualenvs.create false \
    && poetry install --without dev,test --no-interaction --no-ansi \
    && rm -rf $(poetry config cache-dir)/{cache,artifacts}

COPY src/ /app/src/
COPY alembic.ini .

EXPOSE 8000

ENTRYPOINT ["sh", "-c", "alembic upgrade head && exec python -m src.main"]
