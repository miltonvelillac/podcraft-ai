import anyio
import pytest

from api_host.clients.audio_mcp_client import AudioMcpClient


def test_audio_client_generates_mock_audio_metadata_over_mcp() -> None:
    client = AudioMcpClient()

    result = anyio.run(
        _generate_audio_from_text,
        client,
        "podcast-test",
        "Welcome to today's episode.",
        "default",
        120,
    )

    assert result.audio_url == "/generated/audio/podcast-test.wav"
    assert result.format == "wav"
    assert result.duration_seconds == 120


def test_audio_client_rejects_empty_script() -> None:
    client = AudioMcpClient()

    with pytest.raises(ValueError, match="Script cannot be empty"):
        anyio.run(
            _generate_audio_from_text,
            client,
            "podcast-empty",
            "   ",
            "default",
            120,
        )


async def _generate_audio_from_text(
    client: AudioMcpClient,
    podcast_id: str,
    script: str,
    voice: str,
    duration_seconds: int,
):
    return await client.generate_audio_from_text(
        podcast_id=podcast_id,
        script=script,
        voice=voice,
        duration_seconds=duration_seconds,
    )
