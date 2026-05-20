# Portfolio Notes

PodCraft AI is positioned as:

> An agentic AI application that transforms plain text or PDF documents into podcast-style audio or direct narrated audio using Angular, Python, FastAPI, MCP servers, LangChain, LangGraph, and text-to-speech.

## Skills Demonstrated

- Angular frontend engineering
- Reactive, typed UI integration
- Python backend engineering
- FastAPI API design
- MCP architecture and host orchestration
- MCP servers over STDIO
- Internal AI agent design
- LangChain structured output
- LangGraph workflow control and retry
- PDF extraction
- Translation tools exposed through MCP
- Text-to-speech generation
- Provider abstraction for mock and real AI services
- Shared contracts in a monorepo
- Unit and integration testing

## Demo Scenarios

### Text To Podcast

Shows end-to-end agentic transformation:

```txt
Text input -> ScriptAgent graph -> podcast script -> Audio MCP -> audio
```

### PDF To Podcast

Shows MCP tool isolation:

```txt
PDF -> Document MCP -> ScriptAgent graph -> Audio MCP -> audio
```

### Read Aloud

Shows flexible orchestration with the same audio tool:

```txt
Text/PDF -> Translation MCP if needed -> Audio MCP -> audio
```

Demo input for translated narration:

```txt
hola me gusta la pizza -> language=en -> English narration preview and audio
```

## Architecture Talking Points

- MCP servers expose tools, not reasoning.
- The Script Agent stays internal to the Host for MVP simplicity.
- LangGraph adds workflow control without changing the MCP boundary.
- Read aloud translation is a separate MCP tool capability, not part of the Audio MCP Server.
- Audio generation is provider-based, so mock and OpenAI TTS share the same host contract.
- The frontend does not know whether audio came from a podcast script or direct narration; it only consumes the API response.

## Future Enhancements

- Deploy frontend and backend to cloud infrastructure.
- Move generated audio to object storage such as S3 or Cloudflare R2.
- Add two-speaker podcast mode.
- Add transcript export.
- Add chapter generation.
- Add background jobs for long documents.
- Add persistent history with a database.
