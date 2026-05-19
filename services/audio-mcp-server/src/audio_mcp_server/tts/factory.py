import os

from audio_mcp_server.tts.mock_provider import MockTtsProvider
from audio_mcp_server.tts.provider import TtsProvider


def build_tts_provider() -> TtsProvider:
    provider_name = os.getenv("TTS_PROVIDER", "mock").strip().lower()

    if provider_name == "mock":
        return MockTtsProvider()

    raise ValueError(f"Unsupported TTS_PROVIDER: {provider_name}.")
