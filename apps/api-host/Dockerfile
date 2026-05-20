FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV UV_LINK_MODE=copy

COPY pyproject.toml uv.lock README.md ./
COPY packages ./packages
COPY apps/api-host ./apps/api-host
COPY services/document-mcp-server ./services/document-mcp-server
COPY services/translation-mcp-server ./services/translation-mcp-server
COPY services/audio-mcp-server ./services/audio-mcp-server

RUN uv sync --frozen --no-dev
RUN mkdir -p generated/audio generated/documents

EXPOSE 8000

CMD ["uv", "run", "--no-sync", "uvicorn", "api_host.main:app", "--app-dir", "apps/api-host/src", "--host", "0.0.0.0", "--port", "8000"]
