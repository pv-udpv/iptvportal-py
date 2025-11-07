"""IPTVPortal Python SDK.

A full-featured Python SDK for the IPTVPortal JSONSQL API with both
synchronous and asynchronous support.

Example:
    Synchronous usage:
    
    >>> from iptvportal import IPTVPortalClient
    >>> with IPTVPortalClient() as client:
    ...     result = client.execute({
    ...         "jsonrpc": "2.0",
    ...         "id": 1,
    ...         "method": "get",
    ...         "params": {"from": "media", "limit": 10}
    ...     })
    
    Asynchronous usage:
    
    >>> from iptvportal import AsyncIPTVPortalClient
    >>> async with AsyncIPTVPortalClient() as client:
    ...     result = await client.execute({
    ...         "jsonrpc": "2.0",
    ...         "id": 1,
    ...         "method": "get",
    ...         "params": {"from": "media", "limit": 10}
    ...     })
"""

__version__ = "0.1.0"
__author__ = "pv-udpv"
__license__ = "MIT"

from .client import IPTVPortalClient
from .asyncclient import AsyncIPTVPortalClient
from .config import IPTVPortalSettings
from .exceptions import (
    IPTVPortalError,
    AuthenticationError,
    APIError,
    RetryExhaustedError,
    ValidationError,
)

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__license__",
    # Main clients
    "IPTVPortalClient",
    "AsyncIPTVPortalClient",
    # Configuration
    "IPTVPortalSettings",
    # Exceptions
    "IPTVPortalError",
    "AuthenticationError",
    "APIError",
    "RetryExhaustedError",
    "ValidationError",
]
