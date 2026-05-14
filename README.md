# PodCraft AI

PodCraft AI is an agentic AI application that transforms plain text and PDF documents into podcast-style audio using Angular, Python, FastAPI, MCP servers, and an internal script-generation agent.

## Architecture

```txt
Angular Frontend
   |
Python FastAPI Backend / MCP Host
   |
MCP Host Orchestrator
   |-- Document MCP Server
   |-- Internal Script Agent
   `-- Audio MCP Server
   |
Generated Podcast Audio
```

## Monorepo Layout

```txt
apps/
  web-angular/
  api-host/
services/
  document-mcp-server/
  audio-mcp-server/
packages/
  shared-contracts/
docs/
generated/
```

## Local Tooling

- `pnpm` for frontend workspace commands.
- `uv` for Python dependency management.
- `docker compose` for local orchestration.
- `make` for common commands.

## Local Development

Install Python dependencies:

```bash
uv sync
```

Start the FastAPI host:

```bash
uv run uvicorn api_host.main:app --app-dir apps/api-host/src --reload --port 8000
```

Then open Swagger:

```txt
http://localhost:8000/docs
```

Health check:

```txt
http://localhost:8000/health
```

Generate podcast endpoints:

```txt
POST http://localhost:8000/api/podcasts/generate/text
POST http://localhost:8000/api/podcasts/generate/pdf
```

Example JSON body for text input:

```json
{
  "input_type": "text",
  "text": "FastAPI coordinates the podcast generation workflow.",
  "style": "educational",
  "voice": "default",
  "target_duration": "short"
}
```

Example PDF upload with curl:

```bash
curl -X POST http://localhost:8000/api/podcasts/generate/pdf \
  -F "file=@example.pdf" \
  -F "style=educational" \
  -F "voice=default" \
  -F "target_duration=short"
```

## Tests

Run all Python tests:

```bash
uv run pytest
```

Run only the API host tests:

```bash
uv run pytest apps/api-host/tests
```

Run one specific test file:

```bash
uv run pytest apps/api-host/tests/test_podcast_pipeline.py
```

Run linting:

```bash
uv run ruff check .
```

## Make Commands

The root `Makefile` also provides shortcuts:

```bash
make api
make test
make lint
make dev
```

Current command meanings:

- `make api` starts the FastAPI host on port `8000`.
- `make test` runs Python tests and frontend tests.
- `make lint` runs Ruff for Python code.
- `make dev` starts Docker Compose.

## Current Status

This repository currently contains the base monorepo configuration, a FastAPI host, a `/health` endpoint, and mocked podcast generation endpoints for text and PDF input. The Angular app, MCP servers, real PDF extraction, and audio generation will be added incrementally.
