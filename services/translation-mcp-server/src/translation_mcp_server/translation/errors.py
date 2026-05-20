class TranslationProviderError(RuntimeError):
    """Base class for translation provider failures."""


class TranslationConfigurationError(TranslationProviderError):
    """Raised when the translation provider is not configured correctly."""


class TranslationAuthenticationError(TranslationProviderError):
    """Raised when the translation provider rejects authentication."""


class TranslationRateLimitError(TranslationProviderError):
    """Raised when the translation provider rate-limits a request."""


class TranslationServiceError(TranslationProviderError):
    """Raised when the translation provider cannot complete a request."""
