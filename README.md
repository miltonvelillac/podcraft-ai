# PodCraft AI

PodCraft AI is an agentic AI application that transforms plain text and PDF documents into podcast-style audio using Angular, Python, FastAPI, MCP servers, and an internal script-generation agent.

## Architecture

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

## Current Status

This repository currently contains the base monorepo configuration and documentation scaffolding. The Angular app, FastAPI host, MCP servers, and podcast pipeline will be added incrementally.
