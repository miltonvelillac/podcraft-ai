import os

from audio_mcp_server.config import load_project_env
from audio_mcp_server.tts.mock_provider import MockTtsProvider
from audio_mcp_server.tts.openai_provider import OpenAiTtsProvider
from audio_mcp_server.tts.provider import TtsProvider
from podcraft_contracts import AiProvider, EnvVar


def build_tts_provider() -> TtsProvider:
    load_project_env()
    provider_name = os.getenv(EnvVar.TTS_PROVIDER, AiProvider.MOCK).strip().lower()

    if provider_name == AiProvider.MOCK:
        return MockTtsProvider()
    if provider_name == AiProvider.OPENAI:
        return OpenAiTtsProvider()

    raise ValueError(f"Unsupported {EnvVar.TTS_PROVIDER}: {provider_name}.")
