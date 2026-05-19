from dataclasses import dataclass
from pathlib import Path
import re

from audio_mcp_server.tts import SynthesisRequest, TtsProvider, build_tts_provider
from audio_mcp_server.tts.mock_provider import MOCK_AUDIO_FORMAT
from podcraft_contracts import DEFAULT_LANGUAGE


DEFAULT_AUDIO_DIR = Path("generated/audio")
SUPPORTED_FORMAT = MOCK_AUDIO_FORMAT.value
_SAFE_PODCAST_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")


@dataclass(frozen=True)
class AudioGenerationResult:
    audio_url: str
    format: str
    duration_seconds: int


def generate_audio_from_text(
    podcast_id: str,
    script: str,
    voice: str,
    duration_seconds: int,
    language: str = DEFAULT_LANGUAGE,
    output_dir: Path = DEFAULT_AUDIO_DIR,
    provider: TtsProvider | None = None,
) -> AudioGenerationResult:
    _validate_audio_request(
        podcast_id=podcast_id,
        script=script,
        voice=voice,
        language=language,
        duration_seconds=duration_seconds,
    )

    tts_provider = provider or build_tts_provider()
    synthesis = tts_provider.synthesize(
        SynthesisRequest(
            podcast_id=podcast_id,
            script=script,
            voice=voice,
            language=language,
            duration_seconds=duration_seconds,
            output_dir=output_dir,
        )
    )

    return AudioGenerationResult(
        audio_url=f"/generated/audio/{synthesis.audio_path.name}",
        format=synthesis.format,
        duration_seconds=synthesis.duration_seconds,
    )


def _validate_audio_request(
    podcast_id: str,
    script: str,
    voice: str,
    language: str,
    duration_seconds: int,
) -> None:
    if not _SAFE_PODCAST_ID.fullmatch(podcast_id):
        raise ValueError("Podcast ID must be a safe filename.")
    if not script.strip():
        raise ValueError("Script cannot be empty.")
    if not voice.strip():
        raise ValueError("Voice cannot be empty.")
    if not language.strip():
        raise ValueError("Language cannot be empty.")
    if duration_seconds <= 0:
        raise ValueError("Duration must be greater than zero.")
