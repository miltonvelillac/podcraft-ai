from enum import StrEnum


class AiProvider(StrEnum):
    MOCK = "mock"
    OPENAI = "openai"


class EnvVar(StrEnum):
    SCRIPT_PROVIDER = "SCRIPT_PROVIDER"
    TTS_PROVIDER = "TTS_PROVIDER"
    OPENAI_API_KEY = "OPENAI_API_KEY"
    OPENAI_SCRIPT_MODEL = "OPENAI_SCRIPT_MODEL"
    OPENAI_TTS_MODEL = "OPENAI_TTS_MODEL"
    OPENAI_TTS_VOICE = "OPENAI_TTS_VOICE"
    OPENAI_TTS_RESPONSE_FORMAT = "OPENAI_TTS_RESPONSE_FORMAT"
    OPENAI_TTS_INSTRUCTIONS = "OPENAI_TTS_INSTRUCTIONS"


class AudioFormat(StrEnum):
    WAV = "wav"


class LanguageCode(StrEnum):
    ENGLISH = "en"
    SPANISH = "es"
    PORTUGUESE = "pt"


class GeneratedAssetName(StrEnum):
    PODCAST_SERVER_METADATA_AUDIO = "podcast-server-metadata.wav"


class McpToolName(StrEnum):
    EXTRACT_TEXT_FROM_PDF = "extract_text_from_pdf"
    CLEAN_EXTRACTED_TEXT = "clean_extracted_text"
    GET_DOCUMENT_METADATA = "get_document_metadata"
    GENERATE_AUDIO_FROM_TEXT = "generate_audio_from_text"
    SAVE_AUDIO_FILE = "save_audio_file"
    GET_AUDIO_METADATA = "get_audio_metadata"


class PayloadField(StrEnum):
    AUDIO_URL = "audio_url"
    CONTENT_BASE64 = "content_base64"
    DURATION_SECONDS = "duration_seconds"
    FILENAME = "filename"
    FORMAT = "format"
    LANGUAGE = "language"
    PAGES = "pages"
    PODCAST_ID = "podcast_id"
    SCRIPT = "script"
    SIZE_BYTES = "size_bytes"
    TEXT = "text"
    VOICE = "voice"


LANGUAGE_NAMES = {
    LanguageCode.ENGLISH.value: "English",
    LanguageCode.SPANISH.value: "Spanish",
    LanguageCode.PORTUGUESE.value: "Portuguese",
}
SUPPORTED_LANGUAGES = tuple(LANGUAGE_NAMES.keys())
DEFAULT_LANGUAGE = LanguageCode.ENGLISH.value

DEFAULT_AUDIO_VOICE = "default"
SUPPORTED_AUDIO_VOICES = ("default", "studio", "briefing")

AUDIO_VOICE_ALIASES = {
    "default": "coral",
    "studio": "nova",
    "briefing": "onyx",
}

PODCAST_DURATION_MINUTES = {
    "short": 2,
    "medium": 4,
    "long": 6,
}
