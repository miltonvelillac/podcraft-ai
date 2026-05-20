# MCP Flow

PodCraft AI uses MCP to isolate document and audio capabilities from the API Host.

The current MVP uses **MCP STDIO**. This keeps local development simple because the API Host can start each MCP server as a subprocess and communicate through JSON-RPC messages.

## Text To Podcast

```txt
POST /api/podcasts/generate/text
   |
GeneratePodcastRequest
   |
PodcastPipeline
   |
ScriptAgent
   |
ScriptGenerationGraph
   |-- prepare_source_text
   |-- generate_script
   |-- retry or fail if invalid
   |
AudioMcpClient
   |
MCP STDIO
   |
Audio MCP Server
   |
generate_audio_from_text
   |
audio_url
```

## PDF To Podcast

```txt
POST /api/podcasts/generate/pdf
   |
UploadFile
   |
DocumentMcpClient
   |
MCP STDIO
   |
Document MCP Server
   |
extract_text_from_pdf
   |
clean text
   |
ScriptAgent
   |
AudioMcpClient
   |
Audio MCP Server
   |
audio_url
```

PDF bytes are base64-encoded before being sent through MCP because MCP payloads are JSON-RPC messages.

## Read Aloud Mode

`read_aloud` uses the same Document and Audio MCP servers but skips the Script Agent.

```txt
Text/PDF
   |
Clean source text
   |
AudioMcpClient
   |
Audio MCP Server
   |
audio_url
```

## MCP Tools

Document MCP Server:

- `extract_text_from_pdf`
- `clean_extracted_text`
- `get_document_metadata`

Audio MCP Server:

- `generate_audio_from_text`
- `save_audio_file`
- `get_audio_metadata`

## Why The Script Agent Is Internal

The Script Agent performs reasoning and transformation. In the MVP it is not an external capability, so it remains inside the API Host.

Correct MVP shape:

```txt
API Host
   |-- Document MCP Server
   |-- Internal Script Agent
   `-- Audio MCP Server
```

Incorrect for MVP:

```txt
API Host
   |-- Document MCP Server
   |-- Script MCP Server
   `-- Audio MCP Server
```

## Future Transport

Streamable HTTP can be considered after the MVP when the MCP servers are deployed as independent services or Docker Compose containers. STDIO remains the simplest transport for the current local MVP.

