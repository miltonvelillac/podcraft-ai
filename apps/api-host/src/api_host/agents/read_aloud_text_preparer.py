from typing import Protocol

from api_host.clients.translation_mcp_client import TranslationMcpClient
from api_host.schemas.podcast_schemas import PodcastLanguage


class TranslationClient(Protocol):
    async def detect_language(self, text: str) -> PodcastLanguage | None: ...

    async def translate_text(
        self,
        source_text: str,
        target_language: PodcastLanguage,
        source_language: PodcastLanguage | None = None,
    ) -> str: ...


class ReadAloudTextPreparer:
    def __init__(self, translation_client: TranslationClient | None = None) -> None:
        self._translation_client = translation_client or TranslationMcpClient()

    async def prepare(self, text: str, target_language: PodcastLanguage) -> str:
        normalized_text = " ".join(text.split())
        source_language = await self._translation_client.detect_language(normalized_text)

        if source_language is None or source_language == target_language:
            return normalized_text

        return await self._translation_client.translate_text(
            source_text=normalized_text,
            source_language=source_language,
            target_language=target_language,
        )
