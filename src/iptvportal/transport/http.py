"""HTTP transport with retry and exponential backoff."""
import asyncio
import time
from typing import Any, Dict

import httpx

from ..config import IPTVPortalSettings
from ..exceptions import APIError, RetryExhaustedError


class HTTPTransport:
    """HTTP transport with retry and exponential backoff.
    
    Provides synchronous HTTP communication with automatic retry logic,
    exponential backoff, and intelligent error handling.
    
    Args:
        settings: Client configuration settings.
    """
    
    def __init__(self, settings: IPTVPortalSettings):
        self.settings = settings
        self.client = httpx.Client(
            timeout=settings.timeout,
            verify=settings.verify_ssl,
            http2=settings.http2,
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100),
        )
    
    def request(self, payload: Dict[str, Any], session_token: str | None = None) -> Dict[str, Any]:
        """Execute JSONRPC request with retry logic.
        
        Args:
            payload: JSONRPC request payload.
            session_token: Optional session token for authenticated requests.
            
        Returns:
            API response result.
            
        Raises:
            APIError: On 4xx errors or API-level errors.
            RetryExhaustedError: When all retry attempts fail.
        """
        url = f"https://{self.settings.domain}/api"
        headers = {}
        if session_token:
            headers["Cookie"] = f"sid={session_token}"
        
        last_exception = None
        for attempt in range(self.settings.max_retries):
            try:
                response = self.client.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=self.settings.timeout,
                )
                
                # Don't retry on 4xx errors
                if 400 <= response.status_code < 500:
                    response.raise_for_status()
                
                response.raise_for_status()
                data = response.json()
                
                if "error" in data:
                    raise APIError(f"API error: {data['error']}")
                
                return data["result"]
                
            except (httpx.HTTPStatusError, httpx.RequestError) as e:
                last_exception = e
                
                # Don't retry on 4xx errors
                if isinstance(e, httpx.HTTPStatusError) and 400 <= e.response.status_code < 500:
                    raise APIError(str(e), e.response.status_code)
                
                # Calculate backoff
                if attempt < self.settings.max_retries - 1:
                    backoff = self.settings.retry_backoff_factor * (2 ** attempt)
                    time.sleep(backoff)
        
        raise RetryExhaustedError(f"Failed after {self.settings.max_retries} attempts: {last_exception}")
    
    def close(self):
        """Close HTTP client."""
        self.client.close()


class AsyncHTTPTransport:
    """Async HTTP transport with retry and exponential backoff.
    
    Provides asynchronous HTTP communication with automatic retry logic,
    exponential backoff, and intelligent error handling.
    
    Args:
        settings: Client configuration settings.
    """
    
    def __init__(self, settings: IPTVPortalSettings):
        self.settings = settings
        self.client = httpx.AsyncClient(
            timeout=settings.timeout,
            verify=settings.verify_ssl,
            http2=settings.http2,
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100),
        )
    
    async def request(self, payload: Dict[str, Any], session_token: str | None = None) -> Dict[str, Any]:
        """Execute JSONRPC request with retry logic.
        
        Args:
            payload: JSONRPC request payload.
            session_token: Optional session token for authenticated requests.
            
        Returns:
            API response result.
            
        Raises:
            APIError: On 4xx errors or API-level errors.
            RetryExhaustedError: When all retry attempts fail.
        """
        url = f"https://{self.settings.domain}/api"
        headers = {}
        if session_token:
            headers["Cookie"] = f"sid={session_token}"
        
        last_exception = None
        for attempt in range(self.settings.max_retries):
            try:
                response = await self.client.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=self.settings.timeout,
                )
                
                if 400 <= response.status_code < 500:
                    response.raise_for_status()
                
                response.raise_for_status()
                data = response.json()
                
                if "error" in data:
                    raise APIError(f"API error: {data['error']}")
                
                return data["result"]
                
            except (httpx.HTTPStatusError, httpx.RequestError) as e:
                last_exception = e
                
                if isinstance(e, httpx.HTTPStatusError) and 400 <= e.response.status_code < 500:
                    raise APIError(str(e), e.response.status_code)
                
                if attempt < self.settings.max_retries - 1:
                    backoff = self.settings.retry_backoff_factor * (2 ** attempt)
                    await asyncio.sleep(backoff)
        
        raise RetryExhaustedError(f"Failed after {self.settings.max_retries} attempts: {last_exception}")
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
