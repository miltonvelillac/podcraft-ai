import os

from audio_mcp_server.config import load_project_env
from audio_mcp_server.tts.mock_provider import MockTtsProvider
from audio_mcp_server.tts.openai_provider import OpenAiTtsProvider
from audio_mcp_server.tts.provider import TtsProvider


def build_tts_provider() -> TtsProvider:
    load_project_env()
    provider_name = os.getenv("TTS_PROVIDER", "mock").strip().lower()

    if provider_name == "mock":
        return MockTtsProvider()
    if provider_name == "openai":
        return OpenAiTtsProvider()

    raise ValueError(f"Unsupported TTS_PROVIDER: {provider_name}.")
