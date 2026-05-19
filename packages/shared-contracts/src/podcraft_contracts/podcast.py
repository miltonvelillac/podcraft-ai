LANGUAGE_NAMES = {
    "en": "English",
    "es": "Spanish",
    "pt": "Portuguese",
}
SUPPORTED_LANGUAGES = tuple(LANGUAGE_NAMES.keys())

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
