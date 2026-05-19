from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class SynthesisRequest:
    podcast_id: str
    script: str
    voice: str
    language: str
    duration_seconds: int
    output_dir: Path


@dataclass(frozen=True)
class SynthesisResult:
    audio_path: Path
    format: str
    duration_seconds: int


class TtsProvider(Protocol):
    def synthesize(self, request: SynthesisRequest) -> SynthesisResult:
        """Generate an audio file from text and return its file details."""
