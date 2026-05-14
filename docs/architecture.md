# Architecture

PodCraft AI uses a lightweight monorepo with an Angular frontend and Python backend services.

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

The script agent stays internal to the MCP Host for the MVP.
