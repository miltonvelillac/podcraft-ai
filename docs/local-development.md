# Local Development

This project uses:

- `uv` for Python dependencies and commands
- `pnpm` for the Angular workspace
- FastAPI for the API Host
- MCP STDIO for local MCP server integration

## Install

```bash
uv sync
corepack pnpm install
```

## Environment

Create `.env`:

```bash
cp .env.example .env
```

Default local mode:

```env
SCRIPT_PROVIDER=mock
TTS_PROVIDER=mock
```

This runs without OpenAI calls. It generates deterministic mock scripts and playable mock WAV files.

OpenAI-backed mode:

```env
OPENAI_API_KEY=sk-proj-...
SCRIPT_PROVIDER=openai
OPENAI_SCRIPT_MODEL=gpt-4.1-nano
TTS_PROVIDER=openai
OPENAI_TTS_MODEL=tts-1
OPENAI_TTS_VOICE=coral
OPENAI_TTS_RESPONSE_FORMAT=wav
```

Script graph controls:

```env
SCRIPT_GRAPH_MAX_SOURCE_CHARS=12000
SCRIPT_GRAPH_MAX_GENERATION_ATTEMPTS=2
```

These values limit how much source text is sent into script generation and how many attempts the graph can make when a script result is invalid.

## Run API

```bash
uv run uvicorn api_host.main:app --app-dir apps/api-host/src --reload --port 8000
```

API docs:

```txt
http://localhost:8000/docs
```

Health check:

```txt
http://localhost:8000/health
```

## Run Frontend

```bash
npm run web:start
```

Open:

```txt
http://localhost:4200
```

## Direct MCP Server Commands

The API Host starts MCP servers over STDIO when needed, but they can also be run directly for debugging.

Document MCP Server:

```bash
uv run python services/document-mcp-server/src/document_mcp_server/server.py
```

Audio MCP Server:

```bash
uv run python services/audio-mcp-server/src/audio_mcp_server/server.py
```

## Tests

Python:

```bash
uv run ruff check .
uv run pytest
```

Frontend:

```bash
npm run web:build
npm run web:test
```

## Demo Checklist

1. Start the API Host.
2. Start the Angular frontend.
3. Generate a podcast from plain text.
4. Generate direct narration with `Read aloud`.
5. Upload a PDF and generate a podcast.
6. Verify script/text preview.
7. Play the audio in the browser.
8. Download the generated audio file.

