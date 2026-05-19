from pathlib import Path

import pytest

from audio_mcp_server.tools.audio_metadata import get_audio_metadata
from audio_mcp_server.tools.generate_audio import generate_audio_from_text
from audio_mcp_server.tools.save_audio_file import save_audio_file


def test_generate_audio_from_text_writes_mock_audio_file(tmp_path: Path) -> None:
    result = generate_audio_from_text(
        podcast_id="podcast-test",
        script="Welcome to today's episode.",
        voice="default",
        duration_seconds=120,
        output_dir=tmp_path,
    )

    audio_path = tmp_path / "podcast-test.mp3"
    assert result.audio_url == "/generated/audio/podcast-test.mp3"
    assert result.format == "mp3"
    assert result.duration_seconds == 120
    assert audio_path.exists()
    assert audio_path.read_bytes().startswith(b"ID3")


def test_generate_audio_from_text_rejects_empty_script(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Script cannot be empty"):
        generate_audio_from_text(
            podcast_id="podcast-test",
            script=" ",
            voice="default",
            duration_seconds=120,
            output_dir=tmp_path,
        )


def test_save_audio_file_writes_base64_content(tmp_path: Path) -> None:
    result = save_audio_file(
        podcast_id="podcast-saved",
        content_base64="YWJj",
        output_dir=tmp_path,
    )

    assert result == "/generated/audio/podcast-saved.mp3"
    assert (tmp_path / "podcast-saved.mp3").read_bytes() == b"abc"


def test_get_audio_metadata_returns_file_details(tmp_path: Path) -> None:
    audio_path = tmp_path / "podcast-test.mp3"
    audio_path.write_bytes(b"abc")

    result = get_audio_metadata(str(audio_path))

    assert result.filename == "podcast-test.mp3"
    assert result.format == "mp3"
    assert result.size_bytes == 3
