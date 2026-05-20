from podcraft_contracts import LanguageCode
from translation_mcp_server.tools.language_detection import detect_language
from translation_mcp_server.translation.mock_provider import MockTranslationProvider
from translation_mcp_server.translation.openai_provider import OpenAiTranslationProvider


def test_detect_language_returns_spanish() -> None:
    result = detect_language(
        "Este documento explica la arquitectura y los pasos para generar audio.",
        provider=MockTranslationProvider(),
    )

    assert result == LanguageCode.SPANISH


def test_detect_language_returns_none_for_ambiguous_text() -> None:
    assert detect_language("Architecture audio workflow", provider=MockTranslationProvider()) is None


def test_openai_provider_detects_short_text_language() -> None:
    model = FakeLanguageModel("Spanish")
    provider = OpenAiTranslationProvider(model=model)

    result = provider.detect_language("hola me gusta la pizza?")

    assert result == LanguageCode.SPANISH
    assert model.input == {
        "supported_languages": "- en: English\n- es: Spanish\n- pt: Portuguese",
        "source_text": "hola me gusta la pizza?",
    }


class FakeLanguageModel:
    def __init__(self, response: str) -> None:
        self._response = response
        self.input: dict[str, str] | None = None

    def invoke(self, input: dict[str, str]) -> str:
        self.input = input
        return self._response
