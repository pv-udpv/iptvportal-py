"""Synchronous IPTVPortal API client."""
from typing import Any, Dict, Optional

from .config import IPTVPortalSettings
from .auth import AuthManager
from .transport.http import HTTPTransport


class IPTVPortalClient:
    """Synchronous IPTVPortal API client with context manager support.
    
    Provides a clean interface to the IPTVPortal JSONRPC API with automatic
    session management, authentication, and retry logic.
    
    Example:
        >>> with IPTVPortalClient() as client:
        ...     result = client.execute({
        ...         "jsonrpc": "2.0",
        ...         "id": 1,
        ...         "method": "get",
        ...         "params": {"from": "subscriber", "limit": 10}
        ...     })
    
    Args:
        settings: Configuration settings. If None, loads from environment.
    """
    
    def __init__(self, settings: Optional[IPTVPortalSettings] = None):
        """Initialize client.
        
        Args:
            settings: Configuration settings. If None, loads from environment.
        """
        self.settings = settings or IPTVPortalSettings()
        self._transport: Optional[HTTPTransport] = None
        self._auth: Optional[AuthManager] = None
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def connect(self):
        """Initialize transport and authentication.
        
        This is called automatically when using the context manager,
        but can be called manually if not using with statement.
        """
        if self._transport is None:
            self._transport = HTTPTransport(self.settings)
            self._auth = AuthManager(self.settings, self._transport.client)
    
    def close(self):
        """Close transport connections.
        
        This is called automatically when using the context manager,
        but can be called manually if not using with statement.
        """
        if self._transport:
            self._transport.close()
            self._transport = None
            self._auth = None
    
    def execute(self, request: Dict[str, Any]) -> Any:
        """Execute JSONRPC request.
        
        Args:
            request: JSONRPC request payload with jsonrpc, id, method, and params.
            
        Returns:
            API response result.
            
        Raises:
            RuntimeError: If client is not connected.
            AuthenticationError: If authentication fails.
            APIError: If the API returns an error.
            RetryExhaustedError: If all retry attempts fail.
            
        Example:
            >>> client.execute({
            ...     "jsonrpc": "2.0",
            ...     "id": 1,
            ...     "method": "get",
            ...     "params": {"from": "media", "limit": 10}
            ... })
        """
        if not self._transport or not self._auth:
            raise RuntimeError("Client not connected. Use context manager or call connect()")
        
        token = self._auth.get_token()
        return self._transport.request(request, token)
