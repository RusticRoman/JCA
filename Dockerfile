FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml .
COPY app/ app/
COPY alembic/ alembic/
COPY alembic.ini .
COPY scripts/ scripts/

RUN pip install --no-cache-dir .

EXPOSE 8000

CMD ["sh", "scripts/start.sh"]
