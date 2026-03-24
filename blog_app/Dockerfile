FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV PATH="/app/.venv/bin:$PATH"

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./
COPY blog_app/pyproject.toml blog_app/README.md ./blog_app/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-install-project

COPY blog_app/src ./blog_app/src
COPY blog_app/alembic ./blog_app/alembic
COPY blog_app/alembic.ini ./blog_app/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

EXPOSE 8000

CMD ["sh", "-c", "uv run alembic -c blog_app/alembic.ini upgrade head && uv run gunicorn blog_app.main:app -c blog_app/src/blog_app/gunicorn_conf.py"]