"""Exception classes for IPTVPortal client."""


class IPTVPortalError(Exception):
    """Base exception for IPTVPortal client."""
    pass


class AuthenticationError(IPTVPortalError):
    """Authentication failed."""
    pass


class APIError(IPTVPortalError):
    """API request failed.
    
    Attributes:
        status_code: HTTP status code if available.
    """
    
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class RetryExhaustedError(IPTVPortalError):
    """All retry attempts failed."""
    pass


class ValidationError(IPTVPortalError):
    """Request validation failed."""
    pass


class NetworkConnectionError(IPTVPortalError):
    """Network connection failed."""
    pass


class RequestTimeoutError(IPTVPortalError):
    """Request timeout."""
    pass


# Aliases for backwards compatibility
ConnectionError = NetworkConnectionError
TimeoutError = RequestTimeoutError
