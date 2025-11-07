"""Tests for configuration management."""

import pytest
from pydantic import ValidationError
from iptvportal.config import IPTVPortalSettings


def test_config_minimal():
    """Test minimal configuration."""
    settings = IPTVPortalSettings(
        domain="test",
        username="user",
        password="pass"
    )
    
    assert settings.domain == "test"
    assert settings.username == "user"


def test_config_missing_required():
    """Test validation error for missing required fields."""
    with pytest.raises(ValidationError):
        IPTVPortalSettings(domain="test")


def test_config_from_env(monkeypatch):
    """Test configuration from environment variables."""
    monkeypatch.setenv("IPTVPORTAL_DOMAIN", "envtest")
    monkeypatch.setenv("IPTVPORTAL_USERNAME", "envuser")
    monkeypatch.setenv("IPTVPORTAL_PASSWORD", "envpass")
    
    settings = IPTVPortalSettings()
    
    assert settings.domain == "envtest"
    assert settings.username == "envuser"
