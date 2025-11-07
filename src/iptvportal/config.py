"""Configuration for IPTVPortal API client."""
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class IPTVPortalSettings(BaseSettings):
    """Configuration for IPTVPortal API client.
    
    All settings can be loaded from environment variables with IPTVPORTAL_ prefix.
    Client-specific settings use IPTVPORTAL_CLIENT__ prefix for nested config.
    
    Example:
        IPTVPORTAL_DOMAIN=iptvportal.ru
        IPTVPORTAL_CLIENT__USERNAME=admin
        IPTVPORTAL_CLIENT__PASSWORD=secret
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="IPTVPORTAL_CLIENT__",
        case_sensitive=False,
        env_nested_delimiter="__",
    )
    
    domain: str
    username: str
    password: SecretStr
    timeout: float = 30.0
    max_retries: int = 3
    retry_backoff_factor: float = 1.0
    verify_ssl: bool = True
    http2: bool = True
