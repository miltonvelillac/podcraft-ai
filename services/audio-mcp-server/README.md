# Audio MCP Server

MCP server responsible for audio tools such as mocked text-to-speech generation, audio file saving, and audio metadata.

## Current MVP Behavior

The server runs over MCP STDIO and exposes:

- `generate_audio_from_text`
- `save_audio_file`
- `get_audio_metadata`

`generate_audio_from_text` writes a deterministic mock `.wav` file under `generated/audio/` and returns:

```json
{
  "audio_url": "/generated/audio/podcast-test.wav",
  "format": "wav",
  "duration_seconds": 120
}
```

The mock keeps the host pipeline end to end while leaving room to replace the implementation with a real TTS provider later.

## TTS Provider Layer

Audio synthesis is isolated behind `TtsProvider`:

```txt
Audio MCP tool
  |
TtsProvider
  |-- MockTtsProvider
  `-- OpenAiTtsProvider
```

Provider selection is controlled by:

```env
TTS_PROVIDER=mock
OPENAI_API_KEY=
OPENAI_TTS_MODEL=gpt-4o-mini-tts
OPENAI_TTS_VOICE=coral
OPENAI_TTS_RESPONSE_FORMAT=wav
OPENAI_TTS_INSTRUCTIONS=Speak clearly in a warm podcast narration style.
```

Use `TTS_PROVIDER=openai` to generate real speech through OpenAI. Keep `TTS_PROVIDER=mock` for local development without API calls.

Run the server directly:

```bash
uv run python services/audio-mcp-server/src/audio_mcp_server/server.py
```
