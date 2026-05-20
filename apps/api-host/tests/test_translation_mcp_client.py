import anyio

from api_host.clients.translation_mcp_client import TranslationMcpClient
from api_host.clients.translation_mcp_client import (
    _is_external_service_error,
    _to_friendly_error_message,
)
from api_host.schemas.podcast_schemas import PodcastLanguage
from podcraft_contracts import AiProvider


def test_translation_client_detects_language_over_mcp() -> None:
    client = TranslationMcpClient()

    result = anyio.run(
        _detect_language,
        client,
        "Este documento explica la arquitectura y los pasos para generar audio.",
    )

    assert result == PodcastLanguage.SPANISH


def test_translation_client_translates_with_mock_provider(monkeypatch) -> None:
    monkeypatch.setenv("TRANSLATION_PROVIDER", AiProvider.MOCK)
    client = TranslationMcpClient()

    result = anyio.run(
        _translate_text,
        client,
        "Este documento explica la arquitectura.",
        PodcastLanguage.ENGLISH,
        PodcastLanguage.SPANISH,
    )

    assert result == "Este documento explica la arquitectura."


def test_translation_client_maps_missing_openai_key_to_configuration_message() -> None:
    result = _to_friendly_error_message(
        "OPENAI_API_KEY is required when TRANSLATION_PROVIDER=openai."
    )

    assert result == (
        "Translation is not configured. Set OPENAI_API_KEY or use "
        "TRANSLATION_PROVIDER=mock."
    )


def test_translation_client_classifies_openai_auth_as_external_service_error() -> None:
    assert _is_external_service_error("OpenAI translation authentication failed.")


async def _detect_language(
    client: TranslationMcpClient,
    text: str,
) -> PodcastLanguage | None:
    return await client.detect_language(text)


async def _translate_text(
    client: TranslationMcpClient,
    source_text: str,
    target_language: PodcastLanguage,
    source_language: PodcastLanguage | None,
) -> str:
    return await client.translate_text(
        source_text=source_text,
        target_language=target_language,
        source_language=source_language,
    )
