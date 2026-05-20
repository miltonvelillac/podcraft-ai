from fastapi.testclient import TestClient

import api_host.api.podcast_routes as podcast_routes_module
from api_host.agents.script_generation.errors import ScriptGenerationServiceError
from api_host.clients.errors import McpExternalServiceError
from api_host.main import app
from pdf_test_utils import build_pdf_with_text
from podcraft_contracts import AiProvider


client = TestClient(app)


def test_generate_podcast_from_json_text(monkeypatch) -> None:
    monkeypatch.setenv("SCRIPT_PROVIDER", AiProvider.MOCK)
    monkeypatch.setenv("TTS_PROVIDER", AiProvider.MOCK)
    response = client.post(
        "/api/podcasts/generate/text",
        json={
            "input_type": "text",
            "generation_mode": "podcast",
            "text": "FastAPI coordinates the podcast generation workflow.",
            "style": "educational",
            "voice": "default",
            "language": "es",
            "target_duration": "short",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["podcast_id"].startswith("podcast-")
    assert "Bienvenido" in body["script"]
    assert body["audio_url"] == f"/generated/audio/{body['podcast_id']}.wav"
    assert body["duration_seconds"] == 120


def test_generate_podcast_from_multipart_pdf(monkeypatch) -> None:
    monkeypatch.setenv("SCRIPT_PROVIDER", AiProvider.MOCK)
    monkeypatch.setenv("TTS_PROVIDER", AiProvider.MOCK)
    response = client.post(
        "/api/podcasts/generate/pdf",
        data={
            "generation_mode": "podcast",
            "style": "conversational",
            "voice": "default",
            "language": "pt",
            "target_duration": "medium",
        },
        files={
            "file": (
                "source.pdf",
                build_pdf_with_text("Podcast route PDF text"),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["podcast_id"].startswith("podcast-")
    assert "Bem-vindo" in body["script"]
    assert "Podcast route PDF text" in body["script"]
    assert body["duration_seconds"] == 240


def test_generate_read_aloud_from_json_text(monkeypatch) -> None:
    monkeypatch.setenv("SCRIPT_PROVIDER", "unsupported")
    monkeypatch.setenv("TTS_PROVIDER", AiProvider.MOCK)
    response = client.post(
        "/api/podcasts/generate/text",
        json={
            "input_type": "text",
            "generation_mode": "read_aloud",
            "text": "Read this source text directly without creating a podcast script.",
            "style": "educational",
            "voice": "default",
            "language": "en",
            "target_duration": "long",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["podcast_id"].startswith("audio-")
    assert body["title"] == "Narrated Audio"
    assert body["script"] == "Read this source text directly without creating a podcast script."
    assert body["duration_seconds"] == 30


def test_generate_podcast_rejects_missing_pdf_file() -> None:
    response = client.post(
        "/api/podcasts/generate/pdf",
        data={
            "style": "educational",
            "voice": "default",
            "language": "en",
            "target_duration": "short",
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "file"]


def test_generate_podcast_rejects_unknown_json_fields() -> None:
    response = client.post(
        "/api/podcasts/generate/text",
        json={
            "input_type": "text",
            "text": "FastAPI coordinates the podcast generation workflow.",
            "style": "educational",
            "voice": "default",
            "target-duration": "short",
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "extra_forbidden"


def test_generate_podcast_rejects_unknown_form_fields() -> None:
    response = client.post(
        "/api/podcasts/generate/pdf",
        data={
            "style": "educational",
            "voice": "default",
            "target-duration": "short",
        },
        files={"file": ("source.pdf", build_pdf_with_text("Unknown field test"), "application/pdf")},
    )

    assert response.status_code == 400
    assert "Unknown form field(s): target-duration" in response.json()["detail"]


def test_generate_text_endpoint_rejects_pdf_input_type() -> None:
    response = client.post(
        "/api/podcasts/generate/text",
        json={
            "input_type": "pdf",
            "text": "This should use the PDF endpoint.",
            "style": "educational",
            "voice": "default",
            "target_duration": "short",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Use /api/podcasts/generate/pdf for PDF input."


def test_generate_text_endpoint_returns_bad_gateway_for_tts_failure(monkeypatch) -> None:
    class FailingPipeline:
        async def generate_from_text(self, _request):
            raise McpExternalServiceError("OpenAI TTS authentication failed.")

    monkeypatch.setattr(podcast_routes_module, "PodcastPipeline", FailingPipeline)

    response = client.post(
        "/api/podcasts/generate/text",
        json={
            "input_type": "text",
            "text": "FastAPI coordinates the podcast generation workflow.",
            "style": "educational",
            "voice": "default",
            "target_duration": "short",
        },
    )

    assert response.status_code == 502
    assert response.json()["detail"] == "OpenAI TTS authentication failed."


def test_generate_text_endpoint_returns_bad_gateway_for_script_failure(monkeypatch) -> None:
    class FailingPipeline:
        async def generate_from_text(self, _request):
            raise ScriptGenerationServiceError("OpenAI script generation failed.")

    monkeypatch.setattr(podcast_routes_module, "PodcastPipeline", FailingPipeline)

    response = client.post(
        "/api/podcasts/generate/text",
        json={
            "input_type": "text",
            "text": "FastAPI coordinates the podcast generation workflow.",
            "style": "educational",
            "voice": "default",
            "language": "en",
            "target_duration": "short",
        },
    )

    assert response.status_code == 502
    assert response.json()["detail"] == "OpenAI script generation failed."


def test_generate_text_endpoint_returns_bad_request_for_translation_configuration(
    monkeypatch,
) -> None:
    class FailingPipeline:
        async def generate_from_text(self, _request):
            raise podcast_routes_module.McpToolInputError(
                "Translation is not configured. Set OPENAI_API_KEY or use "
                "TRANSLATION_PROVIDER=mock."
            )

    monkeypatch.setattr(podcast_routes_module, "PodcastPipeline", FailingPipeline)

    response = client.post(
        "/api/podcasts/generate/text",
        json={
            "input_type": "text",
            "generation_mode": "read_aloud",
            "text": "hola me gusta la pizza",
            "style": "educational",
            "voice": "default",
            "language": "en",
            "target_duration": "short",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Translation is not configured. Set OPENAI_API_KEY or use "
        "TRANSLATION_PROVIDER=mock."
    )


def test_generate_text_endpoint_returns_bad_gateway_for_translation_provider_failure(
    monkeypatch,
) -> None:
    class FailingPipeline:
        async def generate_from_text(self, _request):
            raise McpExternalServiceError("Translation provider failed. Try again.")

    monkeypatch.setattr(podcast_routes_module, "PodcastPipeline", FailingPipeline)

    response = client.post(
        "/api/podcasts/generate/text",
        json={
            "input_type": "text",
            "generation_mode": "read_aloud",
            "text": "hola me gusta la pizza",
            "style": "educational",
            "voice": "default",
            "language": "en",
            "target_duration": "short",
        },
    )

    assert response.status_code == 502
    assert response.json()["detail"] == "Translation provider failed. Try again."
