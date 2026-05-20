import os

from podcraft_contracts import AiProvider, EnvVar
from translation_mcp_server.config import load_project_env
from translation_mcp_server.translation.mock_provider import MockTranslationProvider
from translation_mcp_server.translation.openai_provider import OpenAiTranslationProvider
from translation_mcp_server.translation.provider import TranslationProvider


def build_translation_provider() -> TranslationProvider:
    load_project_env()
    provider_name = os.getenv(EnvVar.TRANSLATION_PROVIDER, AiProvider.MOCK).strip().lower()

    if provider_name == AiProvider.MOCK:
        return MockTranslationProvider()
    if provider_name == AiProvider.OPENAI:
        return OpenAiTranslationProvider()

    raise ValueError(f"Unsupported {EnvVar.TRANSLATION_PROVIDER}: {provider_name}.")
