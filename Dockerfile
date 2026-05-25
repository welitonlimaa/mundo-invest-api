FROM python:3.11-slim AS base

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

RUN pip install --no-cache-dir --upgrade pip

COPY pyproject.toml .

RUN pip install --no-cache-dir \
    fastapi==0.115.0 \
    "uvicorn[standard]==0.30.6" \
    sqlalchemy==2.0.35 \
    alembic==1.13.3 \
    asyncpg==0.29.0 \
    aiosqlite==0.20.0 \
    "pydantic[email]==2.9.2" \
    pydantic-settings==2.5.2 \
    mangum==0.19.0 \
    python-json-logger==2.0.7


FROM base AS dev

RUN pip install --no-cache-dir \
    pytest==8.3.3 \
    pytest-asyncio==0.24.0 \
    httpx==0.27.2 \
    pytest-cov==5.0.0

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


FROM public.ecr.aws/lambda/python:3.11 AS prod

WORKDIR ${LAMBDA_TASK_ROOT}

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    fastapi==0.115.0 \
    "uvicorn[standard]==0.30.6" \
    sqlalchemy==2.0.35 \
    alembic==1.13.3 \
    asyncpg==0.29.0 \
    aiosqlite==0.20.0 \
    "pydantic[email]==2.9.2" \
    pydantic-settings==2.5.2 \
    mangum==0.19.0 \
    python-json-logger==2.0.7

COPY app/ ./app/

CMD ["app.main.handler"]