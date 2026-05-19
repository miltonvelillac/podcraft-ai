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
