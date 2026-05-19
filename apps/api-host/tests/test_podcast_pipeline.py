import anyio

from api_host.schemas.podcast_schemas import GeneratePodcastRequest, PodcastStyle, PodcastTargetDuration
from api_host.services.podcast_pipeline import PodcastPipeline
from pdf_test_utils import build_pdf_with_text


def test_pipeline_generates_mock_podcast_from_text(monkeypatch) -> None:
    monkeypatch.setenv("TTS_PROVIDER", "mock")
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
    monkeypatch.setenv("TTS_PROVIDER", "mock")
    pipeline = PodcastPipeline()

    response = anyio.run(
        _generate_from_pdf,
        pipeline,
        "source.pdf",
        build_pdf_with_text("Pipeline PDF text"),
        PodcastStyle.CONVERSATIONAL,
        "default",
        PodcastTargetDuration.MEDIUM,
    )

    assert response.podcast_id.startswith("podcast-")
    assert response.title == "Pipeline Pdf Text"
    assert "Pipeline PDF text" in response.script
    assert response.audio_url == f"/generated/audio/{response.podcast_id}.wav"
    assert response.duration_seconds == 240


async def _generate_from_pdf(
    pipeline: PodcastPipeline,
    filename: str,
    content: bytes,
    style: PodcastStyle,
    voice: str,
    target_duration: PodcastTargetDuration,
):
    return await pipeline.generate_from_pdf(
        filename=filename,
        content=content,
        style=style,
        voice=voice,
        target_duration=target_duration,
    )


async def _generate_from_text(
    pipeline: PodcastPipeline,
    request: GeneratePodcastRequest,
):
    return await pipeline.generate_from_text(request)
