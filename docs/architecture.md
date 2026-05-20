# Architecture

PodCraft AI uses a lightweight monorepo with an Angular frontend and a Python FastAPI backend that also acts as the MCP Host.

## System View

```txt
Angular Frontend
   |
FastAPI API Host / MCP Host
   |
PodcastPipeline
   |-- DocumentMcpClient
   |     `-- MCP STDIO -> Document MCP Server
   |
   |-- ScriptAgent
   |     `-- LangGraph workflow
   |           `-- MockScriptGenerator or LangChainScriptGenerator
   |
   `-- AudioMcpClient
         `-- MCP STDIO -> Audio MCP Server
               `-- MockTtsProvider or OpenAiTtsProvider
```

## Responsibilities

### Angular Frontend

- Collects text or PDF input.
- Lets the user choose `podcast` or `read_aloud`.
- Sends typed requests to the API Host.
- Displays generated text preview, audio player, and download link.

### FastAPI API Host

- Exposes HTTP endpoints for the frontend.
- Validates request shape.
- Orchestrates the generation pipeline.
- Keeps the Script Agent internal for the MVP.
- Serves generated audio from `/generated`.

### Document MCP Server

- Extracts text from PDFs.
- Cleans extracted text.
- Returns document metadata.
- Does not generate scripts or audio.

### Script Agent

- Runs inside the API Host.
- Uses LangGraph for workflow control.
- Uses either mock generation or LangChain/OpenAI structured output.
- Validates source length and generated script shape.
- Retries script generation when a provider returns an invalid result.

### Audio MCP Server

- Receives text and returns an audio file URL.
- Supports deterministic mock WAV generation.
- Supports OpenAI TTS through a provider abstraction.
- Does not know whether the text came from podcast generation or direct narration.

## Generation Modes

### Podcast

```txt
Text/PDF
   |
Clean source text
   |
ScriptAgent graph
   |
Podcast script
   |
Audio MCP Server
   |
Generated audio
```

### Read Aloud

```txt
Text/PDF
   |
Clean source text
   |
Audio MCP Server
   |
Generated audio
```

`read_aloud` intentionally skips the Script Agent. It is useful when the user wants narration instead of a podcast-style rewrite.

## Shared Contracts

Shared Python constants live in `packages/shared-contracts`:

- provider names
- environment variable names
- language codes
- MCP tool names
- payload field names
- generation modes

This avoids duplicated string contracts across the API Host and MCP servers.

