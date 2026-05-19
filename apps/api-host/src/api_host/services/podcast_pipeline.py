from uuid import uuid4

from api_host.agents.script_agent import ScriptAgent
from api_host.clients.audio_mcp_client import AudioMcpClient
from api_host.clients.document_mcp_client import DocumentMcpClient
from api_host.schemas.podcast_schemas import (
    GeneratePodcastRequest,
    GeneratePodcastResponse,
    PodcastLanguage,
    PodcastStyle,
    PodcastTargetDuration,
)
from podcraft_contracts import GenerationMode


READ_ALOUD_TITLE = "Narrated Audio"
WORDS_PER_MINUTE = 150
MIN_READ_ALOUD_SECONDS = 30


class PodcastPipeline:
    def __init__(
        self,
        script_agent: ScriptAgent | None = None,
        audio_client: AudioMcpClient | None = None,
        document_client: DocumentMcpClient | None = None,
    ) -> None:
        self._script_agent = script_agent
        self._audio_client = audio_client or AudioMcpClient()
        self._document_client = document_client or DocumentMcpClient()

    async def generate_from_text(self, request: GeneratePodcastRequest) -> GeneratePodcastResponse:
        return await self._generate_from_clean_text(
            text=request.text,
            generation_mode=request.generation_mode,
            style=request.style,
            voice=request.voice,
            language=request.language,
            target_duration=request.target_duration,
        )

    async def generate_from_pdf(
        self,
        filename: str,
        content: bytes,
        generation_mode: GenerationMode,
        style: PodcastStyle,
        voice: str,
        language: PodcastLanguage,
        target_duration: PodcastTargetDuration,
    ) -> GeneratePodcastResponse:
        document = await self._document_client.extract_text_from_pdf(
            filename=filename,
            content=content,
        )
        return await self._generate_from_clean_text(
            text=document.text,
            generation_mode=generation_mode,
            style=style,
            voice=voice,
            language=language,
            target_duration=target_duration,
        )

    async def _generate_from_clean_text(
        self,
        text: str,
        generation_mode: GenerationMode,
        style: PodcastStyle,
        voice: str,
        language: PodcastLanguage,
        target_duration: PodcastTargetDuration,
    ) -> GeneratePodcastResponse:
        if generation_mode == GenerationMode.READ_ALOUD:
            return await self._generate_read_aloud(
                text=text,
                voice=voice,
                language=language,
            )

        script = self._get_script_agent().generate_script(
            text=text,
            style=style,
            target_duration=target_duration,
            language=language,
        )
        podcast_id = f"podcast-{uuid4().hex[:8]}"
        duration_seconds = script.estimated_duration_minutes * 60
        audio = await self._audio_client.generate_audio_from_text(
            podcast_id=podcast_id,
            script=script.script,
            voice=voice,
            language=language.value,
            duration_seconds=duration_seconds,
        )

        return GeneratePodcastResponse(
            podcast_id=podcast_id,
            title=script.title,
            script=script.script,
            audio_url=audio.audio_url,
            duration_seconds=audio.duration_seconds,
        )

    def _get_script_agent(self) -> ScriptAgent:
        if self._script_agent is None:
            self._script_agent = ScriptAgent()
        return self._script_agent

    async def _generate_read_aloud(
        self,
        text: str,
        voice: str,
        language: PodcastLanguage,
    ) -> GeneratePodcastResponse:
        normalized_text = " ".join(text.split())
        podcast_id = f"audio-{uuid4().hex[:8]}"
        duration_seconds = _estimate_read_aloud_duration_seconds(normalized_text)
        audio = await self._audio_client.generate_audio_from_text(
            podcast_id=podcast_id,
            script=normalized_text,
            voice=voice,
            language=language.value,
            duration_seconds=duration_seconds,
        )

        return GeneratePodcastResponse(
            podcast_id=podcast_id,
            title=READ_ALOUD_TITLE,
            script=normalized_text,
            audio_url=audio.audio_url,
            duration_seconds=audio.duration_seconds,
        )


def _estimate_read_aloud_duration_seconds(text: str) -> int:
    word_count = len(text.split())
    estimated_seconds = round((word_count / WORDS_PER_MINUTE) * 60)
    return max(MIN_READ_ALOUD_SECONDS, estimated_seconds)
