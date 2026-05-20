.PHONY: install dev web api document-server audio-server test lint

install:
	corepack pnpm install
	uv sync

dev:
	docker compose up --build

web:
	npm run web:start

api:
	uv run uvicorn api_host.main:app --app-dir apps/api-host/src --reload --port 8000

document-server:
	uv run python services/document-mcp-server/src/document_mcp_server/server.py

audio-server:
	uv run python services/audio-mcp-server/src/audio_mcp_server/server.py

test:
	uv run pytest
	npm run web:test

lint:
	uv run ruff check .
