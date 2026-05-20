# Translation MCP Server

MCP server responsible for language tools used before text-to-speech narration.

The server runs over MCP STDIO and exposes:

- `detect_language`
- `translate_text`

`detect_language` returns a supported language code when the source text is clear enough. In mock mode it uses local heuristics; in OpenAI mode it asks the configured model.
`translate_text` translates narration text to the selected target language.

## Providers

Default local mode uses the mock provider:

```env
TRANSLATION_PROVIDER=mock
```

OpenAI-backed translation:

```env
OPENAI_API_KEY=sk-proj-...
TRANSLATION_PROVIDER=openai
OPENAI_TRANSLATION_MODEL=gpt-4.1-nano
```

## Run

```bash
uv run python services/translation-mcp-server/src/translation_mcp_server/server.py
```

## Test

```bash
uv run pytest services/translation-mcp-server/tests
```
