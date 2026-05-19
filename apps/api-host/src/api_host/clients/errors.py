class McpClientError(RuntimeError):
    """Base class for MCP client failures."""


class McpToolInputError(McpClientError):
    """Raised when an MCP tool rejects user input or local configuration."""


class McpExternalServiceError(McpClientError):
    """Raised when an MCP tool cannot complete because an external service failed."""
