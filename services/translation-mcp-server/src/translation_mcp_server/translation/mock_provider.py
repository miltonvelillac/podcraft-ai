from translation_mcp_server.translation.provider import TranslationRequest, TranslationResult
from translation_mcp_server.tools.language_detection import detect_language_with_rules


class MockTranslationProvider:
    def detect_language(self, text: str) -> str | None:
        return detect_language_with_rules(text)

    def translate(self, request: TranslationRequest) -> TranslationResult:
        return TranslationResult(translated_text=request.source_text.strip())
