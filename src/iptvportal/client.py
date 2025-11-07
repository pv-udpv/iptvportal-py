from typing import Optional, Any
import httpx
from .config import IPTVPortalSettings
from .auth import AuthManager
from .query.builder import QueryBuilder
from .resources.subscribers import SubscriberResource
from .exceptions import IPTVPortalError, APIError, TimeoutError, ConnectionError

class IPTVPortalClient:
    """
    Synchronous client for IPTVPortal JSONSQL API.
    Usage:
        with IPTVPortalClient() as client:
            result = client.subscribers.list()
    """
    def __init__(self, settings: Optional[IPTVPortalSettings] = None, **kwargs):
        self.settings = settings or IPTVPortalSettings(**kwargs)
        self.auth = AuthManager(self.settings)
        self.query = QueryBuilder()
        self.httpclient: Optional[httpx.Client] = None
        self.sessionid: Optional[str] = None
        self.subscribers = SubscriberResource(self)
        # Initialize other resource managers...

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exctype, excval, exctb):
        self.close()

    def connect(self):
        self.httpclient = httpx.Client(timeout=self.settings.timeout, verify=self.settings.verifyssl, http2=True)
        self.sessionid = self.auth.authenticate(self.httpclient)

    def close(self):
        if self.httpclient:
            self.httpclient.close()
            self.httpclient = None
            self.sessionid = None

    def execute(self, query: dict[str, Any]) -> Any:
        """
        Send JSONSQL query to the API, handle retries and errors.
        """
        if not self.httpclient or not self.sessionid:
            raise IPTVPortalError('Client not connected. Use with statement or call connect.')
        headers = {
            "Iptvportal-Authorization": f"sessionid {self.sessionid}",
            "Content-Type": "application/json"
        }
        import time
        lasterror = None
        for attempt in range(self.settings.maxretries + 1):
            try:
                response = self.httpclient.post(self.settings.apiurl, json=query, headers=headers)
                response.raise_for_status()
                data = response.json()
                if 'error' in data:
                    raise APIError(data['error'].get('message', 'API error'), details=data['error'])
                return data.get('result')
            except httpx.TimeoutException as e:
                lasterror = TimeoutError(f'Request timeout: {e}')
            except httpx.ConnectError as e:
                lasterror = ConnectionError(f'Connection failed: {e}')
            except httpx.HTTPStatusError as e:
                if 400 <= e.response.status_code < 500:
                    raise APIError(f'Client error: {e}')
                lasterror = APIError(f'HTTP error: {e}')
            except Exception as e:
                lasterror = IPTVPortalError(f'Unexpected error: {e}')
            # Exponential backoff
            if attempt < self.settings.maxretries:
                delay = self.settings.retrydelay * (2 ** attempt)
                if self.settings.logrequests:
                    print(f'Retry attempt {attempt + 1}/{self.settings.maxretries}, waiting {delay}s...')
                time.sleep(delay)
        raise lasterror
