class TtsProviderError(RuntimeError):
    """Base class for user-facing TTS provider failures."""


class TtsConfigurationError(TtsProviderError):
    """Raised when local TTS provider configuration is invalid."""


class TtsAuthenticationError(TtsProviderError):
    """Raised when the TTS provider rejects credentials."""


class TtsRateLimitError(TtsProviderError):
    """Raised when the TTS provider rate limit is exceeded."""


class TtsServiceError(TtsProviderError):
    """Raised when the TTS provider cannot complete synthesis."""
