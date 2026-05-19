# Shared Contracts

Shared API contract notes and cross-service option metadata live here.

The Python package `podcraft-contracts` currently centralizes values shared by the API Host and MCP services:

- supported podcast languages
- UI voice aliases
- default podcast duration minutes

This keeps provider-specific code from duplicating shared product choices.
