from translation_mcp_server.translation.provider import TranslationRequest, TranslationResult


class MockTranslationProvider:
    def translate(self, request: TranslationRequest) -> TranslationResult:
        return TranslationResult(translated_text=request.source_text.strip())
