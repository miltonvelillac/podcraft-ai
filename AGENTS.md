# AGENTS.md

## Project

PodCraft AI

## Purpose

This repository is a portfolio project that demonstrates an agentic AI application using MCP.

The application allows a user to provide either:

- Plain text
- A PDF document

The system converts that input into a podcast-style audio file.

The frontend is built with Angular.

The backend, MCP Host, MCP Servers, and internal AI agent are built with Python.

---

## Main Goal

Build a working MVP that demonstrates:

- Angular frontend development
- Python backend development
- FastAPI
- MCP architecture
- MCP Host orchestration
- Python MCP Servers
- Internal AI agent design
- PDF to text extraction
- Podcast script generation
- Text-to-speech audio generation
- Clean monorepo organization
- Portfolio-ready documentation

---

## Architecture Overview

```txt
Angular Frontend
   ↓
Python FastAPI Backend / MCP Host
   ↓
MCP Host Orchestrator
   ├── Document MCP Server
   ├── Internal Script Agent
   └── Audio MCP Server
   ↓
Generated Podcast Audio
```

---

## Important Architectural Decision

The Script Agent must NOT be implemented as an MCP Server in the first version.

The Script Agent should live inside the MCP Host as an internal Python agent/service.

Reason:

- The Script Agent performs reasoning and transformation.
- The MCP Servers expose external capabilities/tools.
- This keeps the MVP simple while still demonstrating MCP clearly.

Correct architecture:

```txt
MCP Host
   ├── Document MCP Server
   ├── Internal Script Agent
   └── Audio MCP Server
```

Incorrect for MVP:

```txt
MCP Host
   ├── Document MCP Server
   ├── Script MCP Server
   └── Audio MCP Server
```

---

## Current MCP Integration Status

The API Host currently uses MCP client boundary classes, such as `DocumentMcpClient`, but the document client calls the document tools locally in-process.

This is an intentional interim step:

1. Build and test tool logic as plain Python functions.
2. Use those tools locally from the API Host while the MVP pipeline is taking shape.
3. Wrap the tools in real MCP servers.
4. Update the host clients to call those MCP servers through STDIO.

The next MCP implementation step is:

```txt
API Host
   |
DocumentMcpClient
   |
MCP STDIO transport
   |
Document MCP Server
   |
Document tools
```

Rules:

- Do not remove the client boundary just because it currently calls tools locally.
- The local tool call is temporary and should be replaced with MCP STDIO transport.
- Use STDIO as the first MCP transport for the MVP.
- Consider Streamable HTTP after the MVP is working end to end, especially when running MCP servers as independent Docker Compose services.
- Keep `DocumentMcpClient` and `AudioMcpClient` as the host-side integration points.
- Keep the Script Agent internal to the API Host for the MVP.
- Do not convert the Script Agent into an MCP server in the first version.

---

## Monorepo Strategy

Use a lightweight monorepo.

Do not use Nx, Turborepo, or other heavy monorepo frameworks for the first version.

Use:

- `pnpm` for the Angular frontend
- `uv` for Python dependency management
- `Docker Compose` for local orchestration
- `Makefile` for common commands

---

## Suggested Repository Structure

```txt
podcraft-ai/
│
├── AGENTS.md
├── README.md
├── .gitignore
├── .env.example
├── docker-compose.yml
├── pnpm-workspace.yaml
├── package.json
├── pyproject.toml
├── uv.lock
├── Makefile
│
├── apps/
│   ├── web-angular/
│   │   ├── src/
│   │   ├── angular.json
│   │   ├── package.json
│   │   └── README.md
│   │
│   └── api-host/
│       ├── src/
│       │   └── api_host/
│       │       ├── main.py
│       │       ├── api/
│       │       │   └── podcast_routes.py
│       │       ├── agents/
│       │       │   └── script_agent.py
│       │       ├── clients/
│       │       │   ├── document_mcp_client.py
│       │       │   └── audio_mcp_client.py
│       │       ├── services/
│       │       │   ├── podcast_pipeline.py
│       │       │   └── file_storage.py
│       │       └── schemas/
│       │           └── podcast_schemas.py
│       ├── tests/
│       └── README.md
│
├── services/
│   ├── document-mcp-server/
│   │   ├── src/
│   │   │   └── document_mcp_server/
│   │   │       ├── server.py
│   │   │       └── tools/
│   │   │           ├── extract_pdf_text.py
│   │   │           └── clean_text.py
│   │   ├── tests/
│   │   └── README.md
│   │
│   └── audio-mcp-server/
│       ├── src/
│       │   └── audio_mcp_server/
│       │       ├── server.py
│       │       └── tools/
│       │           ├── generate_audio.py
│       │           └── audio_metadata.py
│       ├── tests/
│       └── README.md
│
├── packages/
│   └── shared-contracts/
│       └── README.md
│
├── generated/
│   ├── audio/
│   └── documents/
│
└── docs/
    ├── architecture.md
    ├── mcp-flow.md
    ├── local-development.md
    └── portfolio-notes.md
```

---

## Technology Stack

### Frontend

Use:

- Angular 19 or later
- TypeScript
- Angular Material
- Reactive Forms
- Standalone components
- Strict typing

### Backend

Use:

- Python 3.11+
- FastAPI
- Pydantic
- MCP Python SDK
- pytest
- uv

### PDF Processing

Prefer one of:

- PyMuPDF
- pypdf

### Text-to-Speech

Start with a mocked audio response.

Later replace the mock with a real TTS provider.

Possible providers:

- OpenAI TTS
- ElevenLabs
- local TTS engine

Do not hardcode the provider into the architecture. Use an abstraction.

---

## Development Order

Codex should build the project in this order:

1. Create the monorepo folder structure.
2. Add root documentation files.
3. Add root configuration files.
4. Create the Python FastAPI host.
5. Add a `/health` endpoint.
6. Add the Angular application shell.
7. Add a simple Angular page for text input.
8. Connect Angular to FastAPI.
9. Implement the internal Script Agent with a mocked response.
10. Implement the Document MCP Server with real PDF extraction.
11. Implement the Audio MCP Server with mocked audio generation.
12. Implement MCP clients in the host.
13. Implement the podcast pipeline service.
14. Add generated script preview in Angular.
15. Add audio player in Angular.
16. Add PDF upload flow.
17. Add error handling.
18. Add unit tests.
19. Add integration tests.
20. Improve README and docs.

---

## MVP Scope

The first working version must include:

- Angular frontend
- Text input
- PDF upload
- Python FastAPI backend
- Python MCP Host
- Document MCP Server
- Audio MCP Server
- Internal Script Agent
- Script preview
- Audio file generation
- Audio playback
- Downloadable audio file

The first version should NOT include:

- Authentication
- User accounts
- Database
- Payment system
- Cloud deployment
- Advanced RAG
- Multiple speakers
- Background job queue
- Complex audio editing

---

## Backend Responsibilities

The backend must expose HTTP endpoints for the frontend.

Initial endpoints:

```http
GET /health
POST /api/podcasts/generate
```

The `/api/podcasts/generate` endpoint must support:

- Plain text input
- PDF upload through `multipart/form-data`

The route handler should be thin.

Do not put orchestration logic directly inside the route.

Correct:

```txt
route → service → agent / MCP clients → response
```

Incorrect:

```txt
route → all business logic inside controller
```

---

## MCP Host Responsibilities

The MCP Host is responsible for orchestration.

It should:

- Receive normalized requests from the API layer.
- Detect input type.
- Call Document MCP Server when the input is a PDF.
- Use plain text directly when the input is text.
- Call the internal Script Agent.
- Call the Audio MCP Server.
- Return structured output.

Expected pipeline:

```txt
Input
  ↓
Extract text if needed
  ↓
Clean text
  ↓
Generate podcast script
  ↓
Generate audio
  ↓
Return result
```

---

## Document MCP Server

The Document MCP Server exposes document-processing tools.

Initial tools:

- `extract_text_from_pdf`
- `clean_extracted_text`
- `get_document_metadata`

Expected response:

```json
{
  "filename": "example.pdf",
  "pages": 8,
  "text": "Extracted and cleaned text..."
}
```

Rules:

- Keep document processing isolated in this service.
- Do not generate podcast scripts here.
- Do not generate audio here.
- Return clean, structured data.

---

## Audio MCP Server

The Audio MCP Server exposes audio-generation tools.

Initial tools:

- `generate_audio_from_text`
- `save_audio_file`
- `get_audio_metadata`

Expected response:

```json
{
  "audio_url": "/generated/audio/podcast-123.mp3",
  "format": "mp3",
  "duration_seconds": 210
}
```

Rules:

- Keep audio logic isolated in this service.
- Do not extract PDFs here.
- Do not create podcast scripts here.
- Start with mocked audio output if needed.
- Later replace the mock with a real TTS provider.

---

## Internal Script Agent

The Script Agent lives inside the MCP Host.

File:

```txt
apps/api-host/src/api_host/agents/script_agent.py
```

Responsibilities:

- Receive clean text.
- Summarize the content.
- Identify main ideas.
- Convert the content into a podcast-style script.
- Adapt style and tone.
- Return structured output.

Initial styles:

- `educational`
- `conversational`
- `executive_summary`

Expected response:

```json
{
  "title": "Generated podcast title",
  "script": "Welcome to today's episode...",
  "estimated_duration_minutes": 4
}
```

Rules:

- Do not implement this as an MCP Server.
- Keep the agent testable.
- Start with deterministic mock logic if no LLM is configured.
- Use dependency injection or configuration for the LLM provider.

---

## Angular Frontend Requirements

The Angular frontend should include:

- A podcast generation page.
- A form for plain text input.
- A PDF upload input.
- A style selector.
- A voice selector.
- A generate button.
- Loading state.
- Error state.
- Script preview.
- Audio player.
- Download audio button.

Suggested structure:

```txt
apps/web-angular/src/app/
  ├── core/
  │   ├── services/
  │   └── models/
  ├── features/
  │   └── podcast-generator/
  │       ├── pages/
  │       ├── components/
  │       ├── services/
  │       └── models/
  └── shared/
      └── components/
```

Rules:

- Use Reactive Forms.
- Keep API calls inside services.
- Keep components focused on presentation and interaction.
- Use typed interfaces.
- Handle loading, success, and error states.

---

## API Contract

### Generate podcast from text

Request:

```json
{
  "input_type": "text",
  "text": "Content to convert into podcast...",
  "style": "educational",
  "voice": "default",
  "target_duration": "short"
}
```

Response:

```json
{
  "podcast_id": "podcast-123",
  "title": "Generated title",
  "script": "Generated podcast script...",
  "audio_url": "/generated/audio/podcast-123.mp3",
  "duration_seconds": 210
}
```

### Generate podcast from PDF

Use:

```http
multipart/form-data
```

Fields:

```txt
file
style
voice
target_duration
```

Response should use the same structure as text input.

---

## Python Code Style

Use:

- Type hints
- Pydantic models
- Small functions
- Explicit exceptions
- Clear service classes
- pytest tests

Avoid:

- Global mutable state
- Hardcoded API keys
- Business logic in route handlers
- Huge files
- Silent failures
- Unstructured dictionaries when a Pydantic model is better

---

## Angular Code Style

Use:

- Standalone components
- Reactive Forms
- Angular Material
- Typed services
- Strict TypeScript
- Feature-based folder organization

Avoid:

- Business logic in templates
- Huge components
- Untyped API responses
- Hardcoded URLs
- Duplicate interfaces

---

## Environment Variables

Create `.env.example`.

Example:

```env
APP_ENV=development
BACKEND_PORT=8000

OPENAI_API_KEY=
TTS_PROVIDER=mock

GENERATED_AUDIO_DIR=generated/audio
GENERATED_DOCUMENTS_DIR=generated/documents

DOCUMENT_MCP_SERVER_URL=http://localhost:8101
AUDIO_MCP_SERVER_URL=http://localhost:8102
```

Rules:

- Never commit real `.env` files.
- Never hardcode secrets.
- Use `.env.example` for documentation.

---

## Root package.json

Use the root `package.json` only for frontend workspace commands.

Example:

```json
{
  "name": "podcraft-ai",
  "private": true,
  "scripts": {
    "web:start": "pnpm --dir apps/web-angular start",
    "web:build": "pnpm --dir apps/web-angular build",
    "web:test": "pnpm --dir apps/web-angular test"
  },
  "packageManager": "pnpm@latest"
}
```

---

## pnpm-workspace.yaml

Use:

```yaml
packages:
  - "apps/web-angular"
  - "packages/*"
```

---

## Makefile

Add a root `Makefile` for common commands.

Suggested commands:

```makefile
.PHONY: install dev web api document-server audio-server test lint

install:
	pnpm install
	uv sync

dev:
	docker compose up --build

web:
	pnpm web:start

api:
	uv run uvicorn api_host.main:app --app-dir apps/api-host/src --reload --port 8000

document-server:
	uv run python services/document-mcp-server/src/document_mcp_server/server.py

audio-server:
	uv run python services/audio-mcp-server/src/audio_mcp_server/server.py

test:
	uv run pytest
	pnpm web:test

lint:
	uv run ruff check .
```

---

## Docker Compose

Create a `docker-compose.yml` that can eventually run:

- Angular frontend
- Python API Host
- Document MCP Server
- Audio MCP Server

For the first version, it is acceptable if Docker Compose only runs the backend services.

---

## Testing Requirements

Backend tests should cover:

- Health endpoint
- Text input validation
- PDF extraction
- Text cleaning
- Script Agent output
- Podcast pipeline orchestration
- Audio MCP client behavior
- Document MCP client behavior

Frontend tests should cover:

- Form validation
- API service calls
- Loading state
- Error state
- Successful generation flow

---

## Error Handling

Handle at least these cases:

- Empty text input
- Missing PDF file
- Invalid PDF
- PDF with no extractable text
- Unsupported file type
- File too large
- MCP server unavailable
- TTS provider failure
- LLM provider failure

Return user-friendly error messages.

---

## Documentation Requirements

Create and maintain:

```txt
README.md
docs/architecture.md
docs/mcp-flow.md
docs/local-development.md
docs/portfolio-notes.md
apps/api-host/README.md
apps/web-angular/README.md
services/document-mcp-server/README.md
services/audio-mcp-server/README.md
```

The root README must include:

- Project description
- Architecture diagram
- Why MCP is used
- How the project works
- How to run locally
- How to test
- Example input
- Example output
- Portfolio value

---

## Commit Message Style

Use conventional-style commit messages.

Examples:

```txt
feat: create FastAPI host
feat: add document MCP server
feat: implement podcast pipeline
feat: connect Angular form to backend
test: add PDF extraction tests
docs: add architecture overview
chore: add monorepo setup
```

---

## Implementation Principles

When modifying this repository:

- Prefer simple working code over complex abstractions.
- Keep each component responsible for one concern.
- Keep the MCP Host focused on orchestration.
- Keep MCP Servers focused on tools.
- Keep the Script Agent internal.
- Add tests for core behavior.
- Update documentation when architecture changes.
- Do not introduce infrastructure that is not needed for the MVP.
- Do not add authentication until the core flow works.
- Do not add a database until persistence is required.
- Use mocks before real providers when building the first version.

---

## Portfolio Positioning

This project should be described as:

> An agentic AI application that transforms plain text or PDF documents into podcast-style audio using Angular, Python, FastAPI, MCP servers, and an internal script-generation agent.

Skills demonstrated:

- Angular frontend engineering
- Python backend engineering
- FastAPI API design
- MCP architecture
- Agent orchestration
- PDF processing
- Text-to-speech generation
- Modular monorepo design
- Testing and documentation

---

## Future Enhancements

After the MVP is complete, consider:

- Two-speaker podcast mode
- Multiple voices
- Voice selection
- Podcast chapters
- Transcript export
- User history
- Database persistence
- Cloud storage
- Background jobs
- Dockerized deployment
- Authentication
- RAG-based grounding
- Admin dashboard
