from api_host.schemas.podcast_schemas import GeneratePodcastRequest, PodcastStyle, PodcastTargetDuration
from api_host.services.podcast_pipeline import PodcastPipeline


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
