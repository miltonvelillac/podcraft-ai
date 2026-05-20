# API Host

FastAPI backend and MCP Host for PodCraft AI.

## Responsibilities

- Exposes HTTP endpoints consumed by the Angular frontend.
- Orchestrates text and PDF generation flows.
- Calls the Document MCP Server over STDIO for PDF extraction.
- Runs the internal Script Agent for podcast generation.
- Calls the Audio MCP Server over STDIO for audio generation.
- Serves generated audio under `/generated`.

## Endpoints

```http
GET /health
POST /api/podcasts/generate/text
POST /api/podcasts/generate/pdf
```

## Generation Modes

- `podcast`: source text is converted into a podcast script through the internal Script Agent.
- `read_aloud`: source text is sent directly to audio generation after basic cleanup.

## Script Agent

The Script Agent remains internal to the API Host. It uses `ScriptGenerationGraph` to prepare source text, call the selected generator, validate the result, and retry once when needed.

Provider selection:

```env
SCRIPT_PROVIDER=mock
SCRIPT_PROVIDER=openai
```

Graph controls:

```env
SCRIPT_GRAPH_MAX_SOURCE_CHARS=12000
SCRIPT_GRAPH_MAX_GENERATION_ATTEMPTS=2
```

## Run

```bash
uv run uvicorn api_host.main:app --app-dir apps/api-host/src --reload --port 8000
```

## Run With Docker

From the repository root:

```bash
docker compose up --build api-host
```

The API Host container includes the Document and Audio MCP server source code because the host starts those MCP servers over STDIO.

## Test

```bash
uv run pytest apps/api-host/tests
```
