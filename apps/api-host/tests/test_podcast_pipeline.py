import anyio

from api_host.schemas.podcast_schemas import (
    GeneratePodcastRequest,
    PodcastLanguage,
    PodcastStyle,
    PodcastTargetDuration,
)
from api_host.services.podcast_pipeline import PodcastPipeline
from pdf_test_utils import build_pdf_with_text
from podcraft_contracts import AiProvider, GenerationMode


def test_pipeline_generates_mock_podcast_from_text(monkeypatch) -> None:
    monkeypatch.setenv("SCRIPT_PROVIDER", AiProvider.MOCK)
    monkeypatch.setenv("TTS_PROVIDER", AiProvider.MOCK)
    pipeline = PodcastPipeline()
    request = GeneratePodcastRequest(
        text="FastAPI coordinates the podcast generation workflow.",
        style=PodcastStyle.EDUCATIONAL,
        voice="default",
        target_duration=PodcastTargetDuration.SHORT,
    )

    response = anyio.run(_generate_from_text, pipeline, request)

    assert response.podcast_id.startswith("podcast-")
    assert response.title == "Fastapi Coordinates The Podcast Generation Workflow"
    assert "FastAPI coordinates" in response.script
    assert response.audio_url == f"/generated/audio/{response.podcast_id}.wav"
    assert response.duration_seconds == 120


def test_pipeline_generates_podcast_from_pdf(monkeypatch) -> None:
    monkeypatch.setenv("SCRIPT_PROVIDER", AiProvider.MOCK)
    monkeypatch.setenv("TTS_PROVIDER", AiProvider.MOCK)
    pipeline = PodcastPipeline()

    response = anyio.run(
        _generate_from_pdf,
        pipeline,
        "source.pdf",
        build_pdf_with_text("Pipeline PDF text"),
        GenerationMode.PODCAST,
        PodcastStyle.CONVERSATIONAL,
        "default",
        PodcastLanguage.ENGLISH,
        PodcastTargetDuration.MEDIUM,
    )

    assert response.podcast_id.startswith("podcast-")
    assert response.title == "Pipeline Pdf Text"
    assert "Pipeline PDF text" in response.script
    assert response.audio_url == f"/generated/audio/{response.podcast_id}.wav"
    assert response.duration_seconds == 240


def test_pipeline_generates_read_aloud_audio_without_script_agent(monkeypatch) -> None:
    monkeypatch.setenv("SCRIPT_PROVIDER", "unsupported")
    monkeypatch.setenv("TTS_PROVIDER", AiProvider.MOCK)
    pipeline = PodcastPipeline()
    request = GeneratePodcastRequest(
        generation_mode=GenerationMode.READ_ALOUD,
        text="  Read this text exactly as a narrated audio file.  ",
        style=PodcastStyle.EDUCATIONAL,
        voice="default",
        target_duration=PodcastTargetDuration.SHORT,
    )

    response = anyio.run(_generate_from_text, pipeline, request)

    assert response.podcast_id.startswith("audio-")
    assert response.title == "Narrated Audio"
    assert response.script == "Read this text exactly as a narrated audio file."
    assert response.audio_url == f"/generated/audio/{response.podcast_id}.wav"
    assert response.duration_seconds == 30


def test_pipeline_sends_prepared_read_aloud_text_to_audio_client(monkeypatch) -> None:
    monkeypatch.setenv("SCRIPT_PROVIDER", "unsupported")
    audio_client = FakeAudioClient()
    pipeline = PodcastPipeline(
        read_aloud_text_preparer=FakeReadAloudTextPreparer("This text is now in English."),
        audio_client=audio_client,
    )
    request = GeneratePodcastRequest(
        generation_mode=GenerationMode.READ_ALOUD,
        text="Este texto esta en espanol.",
        voice="default",
        language=PodcastLanguage.ENGLISH,
    )

    response = anyio.run(_generate_from_text, pipeline, request)

    assert audio_client.script == "This text is now in English."
    assert audio_client.language == "en"
    assert response.script == "This text is now in English."


async def _generate_from_pdf(
    pipeline: PodcastPipeline,
    filename: str,
    content: bytes,
    generation_mode: GenerationMode,
    style: PodcastStyle,
    voice: str,
    language: PodcastLanguage,
    target_duration: PodcastTargetDuration,
):
    return await pipeline.generate_from_pdf(
        filename=filename,
        content=content,
        generation_mode=generation_mode,
        style=style,
        voice=voice,
        language=language,
        target_duration=target_duration,
    )


async def _generate_from_text(
    pipeline: PodcastPipeline,
    request: GeneratePodcastRequest,
):
    return await pipeline.generate_from_text(request)


class FakeReadAloudTextPreparer:
    def __init__(self, prepared_text: str) -> None:
        self._prepared_text = prepared_text

    async def prepare(self, text: str, target_language: PodcastLanguage) -> str:
        return self._prepared_text


class FakeAudioClient:
    def __init__(self) -> None:
        self.script: str | None = None
        self.language: str | None = None

    async def generate_audio_from_text(
        self,
        podcast_id: str,
        script: str,
        voice: str,
        language: str,
        duration_seconds: int,
    ):
        from api_host.schemas.podcast_schemas import AudioGenerationResult

        self.script = script
        self.language = language
        return AudioGenerationResult(
            audio_url=f"/generated/audio/{podcast_id}.wav",
            format="wav",
            duration_seconds=duration_seconds,
        )
