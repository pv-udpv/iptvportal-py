"""Shared pytest fixtures for IPTVPortal tests."""

import pytest
from iptvportal.config import IPTVPortalSettings


# Test configuration
TEST_SESSION_ID = "bbce5e5653cb4c0199e1e398cde99b16"
TEST_DOMAIN = "adstat"
TEST_USERNAME = "pasha"
TEST_PASSWORD = "test_password"


@pytest.fixture
def test_settings():
    """Create test settings instance."""
    return IPTVPortalSettings(
        domain=TEST_DOMAIN,
        username=TEST_USERNAME,
        password=TEST_PASSWORD
    )


@pytest.fixture
def mock_auth_response():
    """Mock successful authentication response."""
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "id": 1113,
            "name": "pasha",
            "role": "assistant",
            "session_id": TEST_SESSION_ID,
            "language_iso639_1": "ru"
        }
    }


@pytest.fixture
def mock_select_response():
    """Mock successful SELECT response."""
    return {
        "id": 1,
        "method": "select",
        "result": [
            [5402, "Салям"],
            [2808, "Карибу"],
            [10295, "B 24"],
            [17065, "Rutube TV"],
            [5360, "Русь Кострома"],
            [17875, "TV3 Sport (бывший TVPlay Sports)"],
            [5500104, "Amazon Sat BR"],
            [5500105, "Animal Planet BR"],
            [5500106, "Baby TV BR"],
            [5500107, "BIS BR"]
        ]
    }


@pytest.fixture
def mock_error_response():
    """Mock error response."""
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "error": {
            "code": -32600,
            "message": "Invalid Request",
            "data": "Additional error information"
        }
    }
