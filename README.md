# PodCraft AI

PodCraft AI is an agentic AI application that turns plain text or PDF documents into generated audio using Angular, FastAPI, MCP servers, an internal AI agent, LangChain, LangGraph, and text-to-speech.

The MVP supports two generation modes:

- `podcast`: transforms source content into a podcast-style script before generating audio.
- `read_aloud`: reads the source content directly as narrated audio.

## Why MCP

MCP is used to isolate external capabilities behind tool servers:

- The Document MCP Server owns PDF extraction and text cleanup.
- The Audio MCP Server owns audio generation and metadata tools.
- The API Host orchestrates the workflow and keeps reasoning logic internal.

The Script Agent is intentionally **not** an MCP server in the MVP. It lives inside the API Host because it performs reasoning and transformation rather than exposing an external tool capability.

## Architecture

```txt
Angular Frontend
   |
FastAPI API Host / MCP Host
   |
PodcastPipeline
   |-- DocumentMcpClient -> MCP STDIO -> Document MCP Server
   |-- ScriptAgent -> LangGraph -> LangChain/OpenAI or mock
   `-- AudioMcpClient -> MCP STDIO -> Audio MCP Server
                                  `-- Mock TTS or OpenAI TTS
   |
Generated audio file
```

Mode-specific flow:

```txt
Text/PDF input
   |
Extract text if PDF
   |
Generation mode?
   |-- podcast
   |     |
   |     `-- ScriptAgent graph -> podcast script
   |
   `-- read_aloud
         |
         `-- cleaned source text
   |
Audio MCP Server
   |
audio_url + duration
```

## Monorepo Layout

```txt
apps/
  api-host/            FastAPI API and MCP Host
  web-angular/         Angular frontend
services/
  document-mcp-server/ PDF and text processing tools
  audio-mcp-server/    Audio generation tools
packages/
  shared-contracts/    Shared Python constants/contracts
docs/
  architecture.md
  mcp-flow.md
  local-development.md
  portfolio-notes.md
generated/
  audio/
```

## Requirements

- Python 3.11+
- `uv`
- Node.js
- `pnpm` through Corepack

## Environment

Create a local `.env` from the example:

```bash
cp .env.example .env
```

Default values use mock providers so the project works without paid API calls:

```env
SCRIPT_PROVIDER=mock
TTS_PROVIDER=mock
```

To use OpenAI for both script generation and TTS:

```env
OPENAI_API_KEY=sk-proj-...
SCRIPT_PROVIDER=openai
OPENAI_SCRIPT_MODEL=gpt-4.1-nano
TTS_PROVIDER=openai
OPENAI_TTS_MODEL=tts-1
OPENAI_TTS_VOICE=coral
OPENAI_TTS_RESPONSE_FORMAT=wav
```

LangGraph script guardrails are configurable:

```env
SCRIPT_GRAPH_MAX_SOURCE_CHARS=12000
SCRIPT_GRAPH_MAX_GENERATION_ATTEMPTS=2
```

## Local Development

Install dependencies:

```bash
uv sync
corepack pnpm install
```

Run the API Host:

```bash
uv run uvicorn api_host.main:app --app-dir apps/api-host/src --reload --port 8000
```

Run the Angular frontend:

```bash
npm run web:start
```

Useful URLs:

```txt
Frontend: http://localhost:4200
API docs: http://localhost:8000/docs
Health:   http://localhost:8000/health
```

## Docker Compose

Create `.env` first, then run:

```bash
docker compose up --build
```

Compose starts:

- `api-host` on `http://localhost:8000`
- `web-angular` on `http://localhost:4200`

Generated audio and document folders are mounted as Docker volumes:

```txt
generated-audio
generated-documents
```

The API Host image includes the Document and Audio MCP server source code. The MCP servers are still invoked by the API Host over STDIO; they are not separate HTTP services in the MVP compose setup.

## API Examples

Generate a podcast from text:

```json
{
  "input_type": "text",
  "generation_mode": "podcast",
  "text": "FastAPI coordinates the podcast generation workflow.",
  "style": "educational",
  "voice": "default",
  "language": "en",
  "target_duration": "short"
}
```

Generate direct narration from text:

```json
{
  "input_type": "text",
  "generation_mode": "read_aloud",
  "text": "Read this text directly without turning it into a podcast script.",
  "voice": "default",
  "language": "en"
}
```

Upload a PDF:

```bash
curl -X POST http://localhost:8000/api/podcasts/generate/pdf \
  -F "file=@example.pdf" \
  -F "generation_mode=podcast" \
  -F "style=educational" \
  -F "voice=default" \
  -F "language=en" \
  -F "target_duration=short"
```

Example response:

```json
{
  "podcast_id": "podcast-1234abcd",
  "title": "Generated Podcast Title",
  "script": "Welcome to today's episode...",
  "audio_url": "/generated/audio/podcast-1234abcd.wav",
  "duration_seconds": 120
}
```

## Tests

Run Python tests:

```bash
uv run pytest
```

Run Python lint:

```bash
uv run ruff check .
```

Run frontend build and tests:

```bash
npm run web:build
npm run web:test
```

## Portfolio Value

This project demonstrates:

- Angular frontend development with typed API integration
- FastAPI API design
- MCP host orchestration over STDIO
- Python MCP servers
- Internal AI agent design
- LangChain structured output
- LangGraph workflow control, validation, and retry
- PDF extraction
- Mock and real TTS provider abstraction
- Monorepo organization with shared contracts
- Test coverage across API, MCP clients, MCP servers, and frontend
