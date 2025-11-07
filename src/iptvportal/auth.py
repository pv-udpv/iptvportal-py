"""Authentication managers with session caching."""
import asyncio
import time
from typing import Optional

import httpx

from .config import IPTVPortalSettings
from .exceptions import AuthenticationError


class AuthManager:
    """Synchronous authentication manager with session caching.
    
    Manages session tokens with TTL-based expiration to avoid
    unnecessary re-authentication requests.
    
    Args:
        settings: Client configuration settings.
        client: HTTP client for making auth requests.
    """
    
    def __init__(self, settings: IPTVPortalSettings, client: httpx.Client):
        self.settings = settings
        self.client = client
        self._session_token: Optional[str] = None
        self._session_expires: Optional[float] = None
        self._ttl: int = 3600  # 1 hour default TTL
    
    def get_token(self) -> str:
        """Get valid session token, refreshing if needed.
        
        Returns:
            Valid session token.
            
        Raises:
            AuthenticationError: If authentication fails.
        """
        if self._session_token and self._session_expires:
            if time.time() < self._session_expires:
                return self._session_token
        
        return self._authenticate()
    
    def _authenticate(self) -> str:
        """Authenticate and cache session token."""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "authorize",
            "params": {
                "user": self.settings.username,
                "password": self.settings.password.get_secret_value(),
            },
        }
        
        try:
            response = self.client.post(
                f"https://{self.settings.domain}/api",
                json=payload,
                timeout=self.settings.timeout,
            )
            response.raise_for_status()
            data = response.json()
            
            if "error" in data:
                raise AuthenticationError(f"Auth failed: {data['error']}")
            
            self._session_token = data["result"]["sid"]
            self._session_expires = time.time() + self._ttl
            return self._session_token
            
        except httpx.HTTPError as e:
            raise AuthenticationError(f"Authentication request failed: {e}")
    
    def invalidate(self):
        """Invalidate cached session."""
        self._session_token = None
        self._session_expires = None


class AsyncAuthManager:
    """Asynchronous authentication manager with session caching.
    
    Manages session tokens with TTL-based expiration to avoid
    unnecessary re-authentication requests.
    
    Args:
        settings: Client configuration settings.
        client: Async HTTP client for making auth requests.
    """
    
    def __init__(self, settings: IPTVPortalSettings, client: httpx.AsyncClient):
        self.settings = settings
        self.client = client
        self._session_token: Optional[str] = None
        self._session_expires: Optional[float] = None
        self._ttl: int = 3600
    
    async def get_token(self) -> str:
        """Get valid session token, refreshing if needed.
        
        Returns:
            Valid session token.
            
        Raises:
            AuthenticationError: If authentication fails.
        """
        if self._session_token and self._session_expires:
            if time.time() < self._session_expires:
                return self._session_token
        
        return await self._authenticate()
    
    async def _authenticate(self) -> str:
        """Authenticate and cache session token."""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "authorize",
            "params": {
                "user": self.settings.username,
                "password": self.settings.password.get_secret_value(),
            },
        }
        
        try:
            response = await self.client.post(
                f"https://{self.settings.domain}/api",
                json=payload,
                timeout=self.settings.timeout,
            )
            response.raise_for_status()
            data = response.json()
            
            if "error" in data:
                raise AuthenticationError(f"Auth failed: {data['error']}")
            
            self._session_token = data["result"]["sid"]
            self._session_expires = time.time() + self._ttl
            return self._session_token
            
        except httpx.HTTPError as e:
            raise AuthenticationError(f"Authentication request failed: {e}")
    
    def invalidate(self):
        """Invalidate cached session."""
        self._session_token = None
        self._session_expires = None
