# core/exceptions.py
class StockPilotException(Exception):
    """Base exception for all StockPilot AI errors."""
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

class ConfigurationError(StockPilotException):
    """Raised when there is an issue loading or parsing configuration."""

class InitializationError(StockPilotException):
    """Raised when a core service fails to initialize."""

class StorageError(StockPilotException):
    """Raised when a storage operation fails."""

class ProviderError(StockPilotException):
    """Raised when an AI provider encounters an error."""

class PluginError(StockPilotException):
    """Raised when a plugin fails to load or execute."""