from uuid import uuid4

from api_host.agents.script_agent import ScriptAgent
from api_host.clients.audio_mcp_client import AudioMcpClient
from api_host.clients.document_mcp_client import DocumentMcpClient
from api_host.schemas.podcast_schemas import (
    GeneratePodcastRequest,
    GeneratePodcastResponse,
    PodcastStyle,
    PodcastTargetDuration,
)


class PodcastPipeline:
    def __init__(
        self,
        script_agent: ScriptAgent | None = None,
        audio_client: AudioMcpClient | None = None,
        document_client: DocumentMcpClient | None = None,
    ) -> None:
        self._script_agent = script_agent or ScriptAgent()
        self._audio_client = audio_client or AudioMcpClient()
        self._document_client = document_client or DocumentMcpClient()

    def generate_from_text(self, request: GeneratePodcastRequest) -> GeneratePodcastResponse:
        return self._generate_from_clean_text(
            text=request.text,
            style=request.style,
            voice=request.voice,
            target_duration=request.target_duration,
        )

    async def generate_from_pdf(
        self,
        filename: str,
        content: bytes,
        style: PodcastStyle,
        voice: str,
        target_duration: PodcastTargetDuration,
    ) -> GeneratePodcastResponse:
        document = await self._document_client.extract_text_from_pdf(
            filename=filename,
            content=content,
        )
        return self._generate_from_clean_text(
            text=document.text,
            style=style,
            voice=voice,
            target_duration=target_duration,
        )

    def _generate_from_clean_text(
        self,
        text: str,
        style: PodcastStyle,
        voice: str,
        target_duration: PodcastTargetDuration,
    ) -> GeneratePodcastResponse:
        script = self._script_agent.generate_script(
            text=text,
            style=style,
            target_duration=target_duration,
        )
        podcast_id = f"podcast-{uuid4().hex[:8]}"
        duration_seconds = script.estimated_duration_minutes * 60
        audio = self._audio_client.generate_audio_from_text(
            podcast_id=podcast_id,
            script=script.script,
            voice=voice,
            duration_seconds=duration_seconds,
        )

        return GeneratePodcastResponse(
            podcast_id=podcast_id,
            title=script.title,
            script=script.script,
            audio_url=audio.audio_url,
            duration_seconds=audio.duration_seconds,
        )
