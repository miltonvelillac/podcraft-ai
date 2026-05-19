# Audio MCP Server

MCP server responsible for audio tools such as mocked text-to-speech generation, audio file saving, and audio metadata.

## Current MVP Behavior

The server runs over MCP STDIO and exposes:

- `generate_audio_from_text`
- `save_audio_file`
- `get_audio_metadata`

`generate_audio_from_text` writes a deterministic mock `.mp3` file under `generated/audio/` and returns:

```json
{
  "audio_url": "/generated/audio/podcast-test.mp3",
  "format": "mp3",
  "duration_seconds": 120
}
```

The mock keeps the host pipeline end to end while leaving room to replace the implementation with a real TTS provider later.

Run the server directly:

```bash
uv run python services/audio-mcp-server/src/audio_mcp_server/server.py
```
