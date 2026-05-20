import pytest

from translation_mcp_server.tools.translate_text import translate_text
from translation_mcp_server.translation.provider import TranslationRequest, TranslationResult


def test_translate_text_uses_provider_when_language_differs() -> None:
    provider = FakeTranslationProvider("Translated narration.")

    result = translate_text(
        source_text="Texto original.",
        source_language="es",
        target_language="en",
        provider=provider,
    )

    assert result.translated_text == "Translated narration."
    assert provider.request == TranslationRequest(
        source_text="Texto original.",
        source_language="es",
        target_language="en",
    )


def test_translate_text_skips_provider_when_language_matches() -> None:
    provider = FakeTranslationProvider("Should not be used.")

    result = translate_text(
        source_text="  Texto   original.  ",
        source_language="es",
        target_language="es",
        provider=provider,
    )

    assert result.translated_text == "Texto original."
    assert provider.request is None


def test_translate_text_rejects_empty_source_text() -> None:
    with pytest.raises(ValueError, match="Source text cannot be empty"):
        translate_text(source_text="   ", target_language="en")


class FakeTranslationProvider:
    def __init__(self, translated_text: str) -> None:
        self._translated_text = translated_text
        self.request: TranslationRequest | None = None

    def translate(self, request: TranslationRequest) -> TranslationResult:
        self.request = request
        return TranslationResult(translated_text=self._translated_text)
