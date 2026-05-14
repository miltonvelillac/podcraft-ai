from api_host.schemas.podcast_schemas import GeneratePodcastRequest, PodcastStyle, PodcastTargetDuration
from api_host.services.podcast_pipeline import PodcastPipeline
from pdf_test_utils import build_pdf_with_text


def test_pipeline_generates_mock_podcast_from_text() -> None:
    pipeline = PodcastPipeline()
    request = GeneratePodcastRequest(
        text="FastAPI coordinates the podcast generation workflow.",
        style=PodcastStyle.EDUCATIONAL,
        voice="default",
        target_duration=PodcastTargetDuration.SHORT,
    )

    response = pipeline.generate_from_text(request)

    assert response.podcast_id.startswith("podcast-")
    assert response.title == "Fastapi Coordinates The Podcast Generation Workflow"
    assert "FastAPI coordinates" in response.script
    assert response.audio_url == f"/generated/audio/{response.podcast_id}.mp3"
    assert response.duration_seconds == 120


def test_pipeline_generates_podcast_from_pdf() -> None:
    pipeline = PodcastPipeline()

    response = pipeline.generate_from_pdf(
        filename="source.pdf",
        content=build_pdf_with_text("Pipeline PDF text"),
        style=PodcastStyle.CONVERSATIONAL,
        voice="default",
        target_duration=PodcastTargetDuration.MEDIUM,
    )

    assert response.podcast_id.startswith("podcast-")
    assert response.title == "Pipeline Pdf Text"
    assert "Pipeline PDF text" in response.script
    assert response.audio_url == f"/generated/audio/{response.podcast_id}.mp3"
    assert response.duration_seconds == 240
