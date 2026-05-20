from podcraft_contracts import LanguageCode
from translation_mcp_server.tools.language_detection import detect_language


def test_detect_language_returns_spanish() -> None:
    result = detect_language(
        "Este documento explica la arquitectura y los pasos para generar audio."
    )

    assert result == LanguageCode.SPANISH


def test_detect_language_returns_none_for_ambiguous_text() -> None:
    assert detect_language("Architecture audio workflow") is None
