import anyio

from api_host.agents.read_aloud_text_preparer import ReadAloudTextPreparer
from api_host.schemas.podcast_schemas import PodcastLanguage


def test_read_aloud_preparer_skips_translation_when_language_matches() -> None:
    client = FakeTranslationClient(source_language=PodcastLanguage.SPANISH)
    preparer = ReadAloudTextPreparer(translation_client=client)

    result = anyio.run(
        _prepare,
        preparer,
        "Este documento explica la arquitectura del sistema.",
        PodcastLanguage.SPANISH,
    )

    assert result == "Este documento explica la arquitectura del sistema."
    assert client.translated_input is None


def test_read_aloud_preparer_translates_when_language_differs() -> None:
    client = FakeTranslationClient(
        source_language=PodcastLanguage.SPANISH,
        translated_text="This document explains the system architecture.",
    )
    preparer = ReadAloudTextPreparer(translation_client=client)

    result = anyio.run(
        _prepare,
        preparer,
        "Este documento explica la arquitectura del sistema.",
        PodcastLanguage.ENGLISH,
    )

    assert result == "This document explains the system architecture."
    assert client.translated_input == {
        "source_text": "Este documento explica la arquitectura del sistema.",
        "source_language": PodcastLanguage.SPANISH,
        "target_language": PodcastLanguage.ENGLISH,
    }


async def _prepare(
    preparer: ReadAloudTextPreparer,
    text: str,
    target_language: PodcastLanguage,
) -> str:
    return await preparer.prepare(text=text, target_language=target_language)


class FakeTranslationClient:
    def __init__(
        self,
        source_language: PodcastLanguage | None,
        translated_text: str = "Should not be used.",
    ) -> None:
        self._source_language = source_language
        self._translated_text = translated_text
        self.translated_input: dict[str, object] | None = None

    async def detect_language(self, text: str) -> PodcastLanguage | None:
        return self._source_language

    async def translate_text(
        self,
        source_text: str,
        target_language: PodcastLanguage,
        source_language: PodcastLanguage | None = None,
    ) -> str:
        self.translated_input = {
            "source_text": source_text,
            "source_language": source_language,
            "target_language": target_language,
        }
        return self._translated_text
