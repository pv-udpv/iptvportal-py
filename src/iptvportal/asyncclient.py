"""Asynchronous IPTVPortal API client."""
import asyncio
from typing import Any, Dict, List, Optional

from .config import IPTVPortalSettings
from .auth import AsyncAuthManager
from .transport.http import AsyncHTTPTransport


class AsyncIPTVPortalClient:
    """Asynchronous IPTVPortal API client with context manager support.
    
    Provides a clean async interface to the IPTVPortal JSONRPC API with
    automatic session management, authentication, and retry logic.
    Supports concurrent operations for improved performance.
    
    Example:
        >>> async with AsyncIPTVPortalClient() as client:
        ...     result = await client.execute({
        ...         "jsonrpc": "2.0",
        ...         "id": 1,
        ...         "method": "select",
        ...         "params": {"from": "subscriber", "limit": 10}
        ...     })
    
    Args:
        settings: Configuration settings. If None, loads from environment.
    """
    
    def __init__(self, settings: Optional[IPTVPortalSettings] = None):
        """Initialize async client.
        
        Args:
            settings: Configuration settings. If None, loads from environment.
        """
        self.settings = settings or IPTVPortalSettings()
        self._transport: Optional[AsyncHTTPTransport] = None
        self._auth: Optional[AsyncAuthManager] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def connect(self):
        """Initialize transport and authentication.
        
        This is called automatically when using the context manager,
        but can be called manually if not using async with statement.
        """
        if self._transport is None:
            self._transport = AsyncHTTPTransport(self.settings)
            self._auth = AsyncAuthManager(self.settings, self._transport.client)
    
    async def close(self):
        """Close transport connections.
        
        This is called automatically when using the context manager,
        but can be called manually if not using async with statement.
        """
        if self._transport:
            await self._transport.close()
            self._transport = None
            self._auth = None
    
    async def execute(self, request: Dict[str, Any]) -> Any:
        """Execute JSONRPC request asynchronously.
        
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
            >>> await client.execute({
            ...     "jsonrpc": "2.0",
            ...     "id": 1,
            ...     "method": "get",
            ...     "params": {"from": "media", "limit": 10}
            ... })
        """
        if not self._transport or not self._auth:
            raise RuntimeError("Client not connected. Use context manager or call connect()")
        
        token = await self._auth.get_token()
        return await self._transport.request(request, token)
    
    async def execute_many(self, requests: List[Dict[str, Any]]) -> List[Any]:
        """Execute multiple JSONRPC requests concurrently.
        
        This method enables batch operations with automatic concurrency
        management, significantly improving performance for multiple operations.
        
        Args:
            requests: List of JSONRPC request payloads.
            
        Returns:
            List of API response results in the same order as requests.
            
        Raises:
            RuntimeError: If client is not connected.
            AuthenticationError: If authentication fails.
            APIError: If any API request returns an error.
            RetryExhaustedError: If any retry attempts fail.
            
        Example:
            >>> requests = [
            ...     {"jsonrpc": "2.0", "id": 1, "method": "get", "params": {"from": "media", "limit": 10}},
            ...     {"jsonrpc": "2.0", "id": 2, "method": "get", "params": {"from": "subscriber", "limit": 10}}
            ... ]
            >>> results = await client.execute_many(requests)
        """
        tasks = [self.execute(req) for req in requests]
        return await asyncio.gather(*tasks)
