from podcraft_contracts import SUPPORTED_LANGUAGES
from translation_mcp_server.translation import (
    TranslationProvider,
    TranslationRequest,
    TranslationResult,
    build_translation_provider,
)


def translate_text(
    source_text: str,
    target_language: str,
    source_language: str | None = None,
    provider: TranslationProvider | None = None,
) -> TranslationResult:
    normalized_text = " ".join(source_text.split())
    if not normalized_text:
        raise ValueError("Source text cannot be empty.")

    normalized_target_language = target_language.strip().lower()
    if normalized_target_language not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported target language: {target_language}.")

    normalized_source_language = _normalize_optional_language(source_language)
    if normalized_source_language == normalized_target_language:
        return TranslationResult(translated_text=normalized_text)

    translation_provider = provider or build_translation_provider()
    return translation_provider.translate(
        TranslationRequest(
            source_text=normalized_text,
            source_language=normalized_source_language,
            target_language=normalized_target_language,
        )
    )


def _normalize_optional_language(language: str | None) -> str | None:
    if language is None:
        return None

    normalized = language.strip().lower()
    if not normalized:
        return None
    if normalized not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported source language: {language}.")

    return normalized
