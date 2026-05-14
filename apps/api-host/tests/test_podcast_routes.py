from fastapi.testclient import TestClient

from api_host.main import app


client = TestClient(app)


def test_generate_podcast_from_json_text() -> None:
    response = client.post(
        "/api/podcasts/generate",
        json={
            "input_type": "text",
            "text": "FastAPI coordinates the podcast generation workflow.",
            "style": "educational",
            "voice": "default",
            "target_duration": "short",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["podcast_id"].startswith("podcast-")
    assert body["audio_url"] == f"/generated/audio/{body['podcast_id']}.mp3"
    assert body["duration_seconds"] == 120


def test_generate_podcast_from_multipart_pdf() -> None:
    response = client.post(
        "/api/podcasts/generate",
        data={
            "style": "conversational",
            "voice": "default",
            "target_duration": "medium",
        },
        files={"file": ("source.pdf", b"%PDF-1.7 mock content", "application/pdf")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["podcast_id"].startswith("podcast-")
    assert "mocked text extracted" in body["script"]
    assert body["duration_seconds"] == 240


def test_generate_podcast_rejects_missing_pdf_file() -> None:
    response = client.post(
        "/api/podcasts/generate",
        data={
            "style": "educational",
            "voice": "default",
            "target_duration": "short",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "PDF file is required."
