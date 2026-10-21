# syntax=docker/dockerfile:1
# estadisticas/Dockerfile — una imagen para la API, el consumidor y las migraciones (módulo 85)
FROM python:3.13-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:0.13 /uv /bin/
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never
WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev
COPY . .

FROM python:3.13-slim AS runtime
RUN groupadd --system app && useradd --system --gid app --home /app app
WORKDIR /app
COPY --from=builder --chown=app:app /app /app
ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
USER app
EXPOSE 8000
# Por defecto, la API. El consumidor y las migraciones usan la misma imagen con otro command (compose.prod.yaml)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/estadisticas/v1/salud', timeout=4)"
CMD ["uvicorn", "estadisticas.api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--proxy-headers"]
