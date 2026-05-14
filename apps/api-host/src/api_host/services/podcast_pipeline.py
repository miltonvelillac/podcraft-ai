from uuid import uuid4

from api_host.agents.script_agent import ScriptAgent
from api_host.schemas.podcast_schemas import GeneratePodcastRequest, GeneratePodcastResponse


class PodcastPipeline:
    def __init__(self, script_agent: ScriptAgent | None = None) -> None:
        self._script_agent = script_agent or ScriptAgent()

    def generate_from_text(self, request: GeneratePodcastRequest) -> GeneratePodcastResponse:
        script = self._script_agent.generate_script(
            text=request.text,
            style=request.style,
            target_duration=request.target_duration,
        )
        podcast_id = f"podcast-{uuid4().hex[:8]}"
        duration_seconds = script.estimated_duration_minutes * 60

        return GeneratePodcastResponse(
            podcast_id=podcast_id,
            title=script.title,
            script=script.script,
            audio_url=f"/generated/audio/{podcast_id}.mp3",
            duration_seconds=duration_seconds,
        )
