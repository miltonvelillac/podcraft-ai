from api_host.agents.script_generation import (
    ScriptGenerationRequest,
    ScriptGenerator,
    build_script_generator,
)
from api_host.schemas.podcast_schemas import PodcastLanguage, PodcastScript, PodcastStyle, PodcastTargetDuration


class ScriptAgent:
    """Internal script-generation agent used by the MCP host."""

    def __init__(self, generator: ScriptGenerator | None = None) -> None:
        self._generator = generator or build_script_generator()

    def generate_script(
        self,
        text: str,
        style: PodcastStyle,
        target_duration: PodcastTargetDuration,
        language: PodcastLanguage = PodcastLanguage.ENGLISH,
    ) -> PodcastScript:
        return self._generator.generate(
            ScriptGenerationRequest(
                text=text,
                style=style,
                target_duration=target_duration,
                language=language,
            )
        )
