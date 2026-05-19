class ScriptGenerationError(RuntimeError):
    """Base class for user-facing script generation failures."""


class ScriptGenerationConfigurationError(ScriptGenerationError):
    """Raised when script generation configuration is invalid."""


class ScriptGenerationServiceError(ScriptGenerationError):
    """Raised when the script generation provider cannot complete."""
