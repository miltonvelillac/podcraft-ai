from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PodcastInputType(StrEnum):
    TEXT = "text"
    PDF = "pdf"


class PodcastStyle(StrEnum):
    EDUCATIONAL = "educational"
    CONVERSATIONAL = "conversational"
    EXECUTIVE_SUMMARY = "executive_summary"


class PodcastTargetDuration(StrEnum):
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"


class PodcastFormField(StrEnum):
    FILE = "file"
    STYLE = "style"
    VOICE = "voice"
    TARGET_DURATION = "target_duration"


class GeneratePodcastRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    input_type: PodcastInputType = PodcastInputType.TEXT
    text: str = Field(min_length=1)
    style: PodcastStyle = PodcastStyle.EDUCATIONAL
    voice: str = Field(default="default", min_length=1)
    target_duration: PodcastTargetDuration = PodcastTargetDuration.SHORT

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Text input cannot be empty.")
        return normalized


class GeneratePodcastPdfFormRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    style: PodcastStyle = PodcastStyle.EDUCATIONAL
    voice: str = Field(default="default", min_length=1)
    target_duration: PodcastTargetDuration = PodcastTargetDuration.SHORT

    @field_validator("voice")
    @classmethod
    def validate_voice(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Voice cannot be empty.")
        return normalized


class PodcastScript(BaseModel):
    title: str
    script: str
    estimated_duration_minutes: int


class AudioGenerationResult(BaseModel):
    audio_url: str
    format: str
    duration_seconds: int


class DocumentExtractionResult(BaseModel):
    filename: str
    pages: int
    text: str


class GeneratePodcastResponse(BaseModel):
    podcast_id: str
    title: str
    script: str
    audio_url: str
    duration_seconds: int
