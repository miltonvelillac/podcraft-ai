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
TRANSLATION_PROVIDER=mock
TTS_PROVIDER=mock
```

This runs without OpenAI calls. It generates deterministic mock scripts, mock translations, and playable mock WAV files.

OpenAI-backed mode:

```env
OPENAI_API_KEY=sk-proj-...
SCRIPT_PROVIDER=openai
OPENAI_SCRIPT_MODEL=gpt-4.1-nano
TRANSLATION_PROVIDER=openai
OPENAI_TRANSLATION_MODEL=gpt-4.1-nano
TTS_PROVIDER=openai
OPENAI_TTS_MODEL=tts-1
OPENAI_TTS_VOICE=coral
OPENAI_TTS_RESPONSE_FORMAT=wav
```

`read_aloud` calls the Translation MCP Server when the input text language differs from the selected output language. With `TRANSLATION_PROVIDER=openai`, source-language detection and translation both use the configured OpenAI model before TTS.

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

## Run With Docker Compose

Create `.env` first:

```bash
cp .env.example .env
```

Start the stack:

```bash
docker compose up --build
```

Docker Desktop must be running before this command. On Windows, make sure the Linux engine is available.

Services:

```txt
api-host:    http://localhost:8000
web-angular: http://localhost:4200
```

The API Host image contains the Document, Translation, and Audio MCP server source code. The host still calls those MCP servers through STDIO as subprocesses; Docker Compose does not run them as separate HTTP services for the MVP.

Generated files are stored in named Docker volumes:

```txt
generated-audio
generated-documents
```

## Direct MCP Server Commands

The API Host starts MCP servers over STDIO when needed, but they can also be run directly for debugging.

Document MCP Server:

```bash
uv run python services/document-mcp-server/src/document_mcp_server/server.py
```

Translation MCP Server:

```bash
uv run python services/translation-mcp-server/src/translation_mcp_server/server.py
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
