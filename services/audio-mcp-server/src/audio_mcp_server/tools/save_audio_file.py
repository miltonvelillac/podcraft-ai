import base64
from pathlib import Path
import re

from audio_mcp_server.tools.generate_audio import DEFAULT_AUDIO_DIR, SUPPORTED_FORMAT


_SAFE_PODCAST_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")


def save_audio_file(
    podcast_id: str,
    content_base64: str,
    output_dir: Path = DEFAULT_AUDIO_DIR,
) -> str:
    if not _SAFE_PODCAST_ID.fullmatch(podcast_id):
        raise ValueError("Podcast ID must be a safe filename.")

    try:
        content = base64.b64decode(content_base64, validate=True)
    except ValueError as exc:
        raise ValueError("Audio content must be valid base64.") from exc

    if not content:
        raise ValueError("Audio content cannot be empty.")

    output_dir.mkdir(parents=True, exist_ok=True)
    audio_path = output_dir / f"{podcast_id}.{SUPPORTED_FORMAT}"
    audio_path.write_bytes(content)
    return f"/generated/audio/{audio_path.name}"
