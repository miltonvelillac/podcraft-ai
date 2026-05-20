from mcp.server.fastmcp.exceptions import ToolError
import pytest

from podcraft_contracts import LanguageCode, PayloadField
from translation_mcp_server.server import detect_language_tool, translate_text_mcp_tool


def test_detect_language_tool_returns_language_payload(monkeypatch) -> None:
    monkeypatch.setenv("TRANSLATION_PROVIDER", "mock")

    result = detect_language_tool(
        text="Este documento explica la arquitectura y los pasos para generar audio."
    )

    assert result == {PayloadField.SOURCE_LANGUAGE: LanguageCode.SPANISH}


def test_translate_text_tool_returns_mock_translation(monkeypatch) -> None:
    monkeypatch.setenv("TRANSLATION_PROVIDER", "mock")

    result = translate_text_mcp_tool(
        source_text="Texto original.",
        source_language="es",
        target_language="en",
    )

    assert result == {PayloadField.TRANSLATED_TEXT: "Texto original."}


def test_translate_text_tool_returns_clean_error() -> None:
    with pytest.raises(ToolError, match="Source text cannot be empty"):
        translate_text_mcp_tool(source_text="   ", target_language="en")
