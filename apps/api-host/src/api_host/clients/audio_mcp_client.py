from api_host.schemas.podcast_schemas import AudioGenerationResult


class AudioMcpClient:
    """Client boundary for the Audio MCP Server.

    The current implementation is deterministic and mocked. Later this class can call the
    real Audio MCP Server without changing the podcast pipeline contract.
    """

    def generate_audio_from_text(
        self,
        podcast_id: str,
        script: str,
        voice: str,
        duration_seconds: int,
    ) -> AudioGenerationResult:
        return AudioGenerationResult(
            audio_url=f"/generated/audio/{podcast_id}.mp3",
            format="mp3",
            duration_seconds=duration_seconds,
        )
