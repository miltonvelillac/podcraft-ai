from api_host.clients.audio_mcp_client import AudioMcpClient


def test_audio_client_generates_mock_audio_metadata() -> None:
    client = AudioMcpClient()

    result = client.generate_audio_from_text(
        podcast_id="podcast-test",
        script="Welcome to today's episode.",
        voice="default",
        duration_seconds=120,
    )

    assert result.audio_url == "/generated/audio/podcast-test.mp3"
    assert result.format == "mp3"
    assert result.duration_seconds == 120
