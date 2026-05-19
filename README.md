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

Copy environment variables:

```bash
cp .env.example .env
```

The default `.env.example` keeps AI providers in mock mode. To use OpenAI-backed script generation through LangChain and real OpenAI TTS, configure:

```env
OPENAI_API_KEY=sk-proj-...
SCRIPT_PROVIDER=openai
OPENAI_SCRIPT_MODEL=gpt-4.1-mini
TTS_PROVIDER=openai
OPENAI_TTS_MODEL=gpt-4o-mini-tts
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
  "language": "en",
  "target_duration": "short"
}
```

Example PDF upload with curl:

```bash
curl -X POST http://localhost:8000/api/podcasts/generate/pdf \
  -F "file=@example.pdf" \
  -F "style=educational" \
  -F "voice=default" \
  -F "language=en" \
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

This repository currently contains the base monorepo configuration, a FastAPI host, a `/health` endpoint, podcast generation endpoints for text and PDF input, real local PDF text extraction through the Document MCP Server, optional LangChain/OpenAI script generation inside the API Host, and mock or OpenAI-backed audio generation through the Audio MCP Server.

## MCP Integration Status

The API Host now uses `DocumentMcpClient` and `AudioMcpClient` to call the Document and Audio MCP Servers through STDIO. PDF bytes are base64-encoded before being sent through MCP because MCP messages are JSON-RPC payloads.

Current MCP flow:

```txt
API Host
   |
DocumentMcpClient / AudioMcpClient
   |
MCP STDIO transport
   |
Document MCP Server / Audio MCP Server
   |
Document tools / Audio tools
```

STDIO is the intended MCP transport for the MVP because it keeps local orchestration simple. After the MVP is working end to end, Streamable HTTP should be considered for running the Document and Audio MCP Servers as independent services, especially under Docker Compose.

The Script Agent remains internal to the API Host for the MVP. It must not be converted into an MCP server in the first version.

Script generation is provider-based:

```txt
ScriptAgent
  |-- MockScriptGenerator
  `-- LangChainScriptGenerator
```

Use `SCRIPT_PROVIDER=mock` for deterministic local development and tests. Use `SCRIPT_PROVIDER=openai` to generate podcast scripts with LangChain and OpenAI structured output.
