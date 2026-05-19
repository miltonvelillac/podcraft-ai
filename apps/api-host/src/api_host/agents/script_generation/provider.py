from dataclasses import dataclass
from typing import Protocol

from api_host.schemas.podcast_schemas import (
    PodcastLanguage,
    PodcastScript,
    PodcastStyle,
    PodcastTargetDuration,
)


@dataclass(frozen=True)
class ScriptGenerationRequest:
    text: str
    style: PodcastStyle
    target_duration: PodcastTargetDuration
    language: PodcastLanguage


class ScriptGenerator(Protocol):
    def generate(self, request: ScriptGenerationRequest) -> PodcastScript:
        """Generate a structured podcast script from normalized source text."""
