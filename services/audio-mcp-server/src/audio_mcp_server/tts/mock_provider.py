import math
from pathlib import Path
import wave

from audio_mcp_server.tts.provider import SynthesisRequest, SynthesisResult


MOCK_AUDIO_FORMAT = "wav"
SAMPLE_RATE = 8_000


class MockTtsProvider:
    """Deterministic local TTS placeholder that writes a playable WAV file."""

    def synthesize(self, request: SynthesisRequest) -> SynthesisResult:
        request.output_dir.mkdir(parents=True, exist_ok=True)
        audio_path = request.output_dir / f"{request.podcast_id}.{MOCK_AUDIO_FORMAT}"
        self._write_mock_audio_file(audio_path=audio_path, request=request)

        return SynthesisResult(
            audio_path=audio_path,
            format=MOCK_AUDIO_FORMAT,
            duration_seconds=request.duration_seconds,
        )

    def _write_mock_audio_file(self, audio_path: Path, request: SynthesisRequest) -> None:
        voice_offset = sum(ord(character) for character in request.voice.strip()) % 80
        script_words = max(1, len(request.script.split()))
        base_frequency = 260 + voice_offset
        beat_frequency = 360 + (script_words % 120)

        with wave.open(str(audio_path), "wb") as audio_file:
            audio_file.setnchannels(1)
            audio_file.setsampwidth(2)
            audio_file.setframerate(SAMPLE_RATE)

            total_frames = request.duration_seconds * SAMPLE_RATE
            chunk_size = SAMPLE_RATE
            frames_written = 0

            while frames_written < total_frames:
                frames_in_chunk = min(chunk_size, total_frames - frames_written)
                audio_file.writeframesraw(
                    _build_tone_chunk(
                        start_frame=frames_written,
                        frames=frames_in_chunk,
                        base_frequency=base_frequency,
                        beat_frequency=beat_frequency,
                    )
                )
                frames_written += frames_in_chunk


def _build_tone_chunk(
    start_frame: int,
    frames: int,
    base_frequency: int,
    beat_frequency: int,
) -> bytes:
    chunk = bytearray()

    for offset in range(frames):
        frame = start_frame + offset
        second = frame // SAMPLE_RATE
        frequency = beat_frequency if second % 4 == 0 else base_frequency
        envelope = 0.35 if second % 2 == 0 else 0.22
        sample = int(8_000 * envelope * math.sin(2 * math.pi * frequency * frame / SAMPLE_RATE))
        chunk.extend(sample.to_bytes(2, byteorder="little", signed=True))

    return bytes(chunk)
