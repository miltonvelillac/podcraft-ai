# MCP Flow

Expected MVP flow:

```txt
Input
  |
Extract text if needed
  |
Clean text
  |
Generate podcast script
  |
Generate audio
  |
Return result
```

Document processing and audio generation are isolated behind MCP servers. The script-generation agent remains internal to the API Host.

## Current STDIO Integration

```txt
FastAPI route
  |
PodcastPipeline
  |-- DocumentMcpClient -> MCP STDIO -> Document MCP Server
  |-- ScriptAgent internal service
  `-- AudioMcpClient -> MCP STDIO -> Audio MCP Server
```

The Audio MCP Server currently writes deterministic mock audio files to `generated/audio/`. This keeps the end-to-end API contract working before adding a real TTS provider.
