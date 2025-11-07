"""
Comprehensive unit tests for CLI authentication manager.

Tests cover edge cases including:
- Invalid tokens (empty, null, malformed)
- Missing credentials
- File permission issues
- Network failures
- Retry logic
- Async authentication
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import httpx
from pathlib import Path
import json
import tempfile
from iptvportal.auth import AuthManager, AsyncAuthManager
from iptvportal.config import IPTVPortalSettings
from iptvportal.exceptions import (
    AuthenticationError,
    IPTVPortalError,
    ConnectionError,
    TimeoutError
)


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def mock_settings():
    """Provide mock settings for testing"""
    return IPTVPortalSettings(
        domain="test.iptvportal.ru",
        username="testuser",
        password="testpass",
        timeout=5.0,
        verify_ssl=True,
        max_retries=3
    )


@pytest.fixture
def mock_http_client():
    """Provide mock HTTP client"""
    return Mock(spec=httpx.Client)


@pytest.fixture
def mock_async_http_client():
    """Provide mock async HTTP client"""
    return Mock(spec=httpx.AsyncClient)


@pytest.fixture
def valid_auth_response():
    """Provide valid authentication response"""
    mock_response = Mock()
    mock_response.json.return_value = {
        "result": {"sessionid": "valid_session_123"}
    }
    mock_response.raise_for_status = Mock()
    return mock_response


# ============================================================================
# Invalid Token Tests
# ============================================================================

class TestAuthManagerInvalidTokens:
    """Test authentication with invalid token formats"""

    def test_invalid_token_format_empty_string(self, mock_settings, mock_http_client):
        """Test authentication fails with empty token string"""
        auth = AuthManager(mock_settings)

        # Mock response with empty session ID
        mock_response = Mock()
        mock_response.json.return_value = {"result": {"sessionid": ""}}
        mock_response.raise_for_status = Mock()
        mock_http_client.post.return_value = mock_response

        with pytest.raises(AuthenticationError, match="Invalid session ID"):
            auth.authenticate(mock_http_client)

    def test_invalid_token_format_null_value(self, mock_settings, mock_http_client):
        """Test authentication fails with null token value"""
        auth = AuthManager(mock_settings)

        mock_response = Mock()
        mock_response.json.return_value = {"result": {"sessionid": None}}
        mock_response.raise_for_status = Mock()
        mock_http_client.post.return_value = mock_response

        with pytest.raises(AuthenticationError, match="Invalid session ID"):
            auth.authenticate(mock_http_client)

    def test_malformed_token_response(self, mock_settings, mock_http_client):
        """Test authentication fails when response structure is malformed"""
        auth = AuthManager(mock_settings)

        # Missing sessionid key
        mock_response = Mock()
        mock_response.json.return_value = {"result": {}}
        mock_response.raise_for_status = Mock()
        mock_http_client.post.return_value = mock_response

        with pytest.raises(AuthenticationError, match="Missing session ID"):
            auth.authenticate(mock_http_client)

    def test_expired_token_rejected(self, mock_settings, mock_http_client):
        """Test that expired tokens are properly rejected"""
        auth = AuthManager(mock_settings)

        # Simulate expired token error
        mock_response = Mock()
        mock_response.json.return_value = {
            "error": {
                "message": "Session expired",
                "code": 401
            }
        }
        mock_response.raise_for_status = Mock()
        mock_http_client.post.return_value = mock_response

        with pytest.raises(AuthenticationError, match="Session expired"):
            auth.authenticate(mock_http_client)


# ============================================================================
# Missing Credentials Tests
# ============================================================================

class TestAuthManagerMissingCredentials:
    """Test authentication with missing or incomplete credentials"""

    def test_missing_username(self):
        """Test authentication fails when username is missing"""
        with pytest.raises(ValueError, match="username"):
            IPTVPortalSettings(
                domain="test.iptvportal.ru",
                username="",
                password="testpass"
            )

    def test_missing_password(self):
        """Test authentication fails when password is missing"""
        with pytest.raises(ValueError, match="password"):
            IPTVPortalSettings(
                domain="test.iptvportal.ru",
                username="testuser",
                password=""
            )

    def test_missing_domain(self):
        """Test authentication fails when domain is missing"""
        with pytest.raises(ValueError, match="domain"):
            IPTVPortalSettings(
                domain="",
                username="testuser",
                password="testpass"
            )

    def test_none_credentials_from_env(self):
        """Test that None values from environment variables are rejected"""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError):
                IPTVPortalSettings()

    def test_partial_credentials_from_cli(self):
        """Test CLI fails gracefully with partial credentials"""
        from iptvportal.cli.app import main
        from typer.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(main, [
            "--domain", "test.iptvportal.ru",
            "--username", "testuser",
            # Missing password
            "subscriber", "list"
        ])

        assert result.exit_code != 0
        assert "password" in result.output.lower()


# ============================================================================
# File Permission Tests
# ============================================================================

class TestAuthManagerFilePermissions:
    """Test authentication with file permission issues"""

    def test_unreadable_env_file(self):
        """Test handling of .env file without read permissions"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("IPTVPORTAL_DOMAIN=test.iptvportal.ru\n")
            f.write("IPTVPORTAL_CLIENT__USERNAME=testuser\n")
            f.write("IPTVPORTAL_CLIENT__PASSWORD=testpass\n")
            env_file = f.name

        try:
            # Remove read permissions
            Path(env_file).chmod(0o000)

            with pytest.raises(PermissionError):
                IPTVPortalSettings(_env_file=env_file)
        finally:
            # Restore permissions and clean up
            Path(env_file).chmod(0o644)
            Path(env_file).unlink()

    def test_write_protected_cache_directory(self, mock_settings, mock_http_client, valid_auth_response):
        """Test handling of cache directory without write permissions"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir) / ".iptvportal_cache"
            cache_dir.mkdir()
            cache_dir.chmod(0o444)  # Read-only

            auth = AuthManager(mock_settings)

            # Should handle gracefully without crashing
            with patch.object(auth, '_cache_dir', cache_dir):
                mock_http_client.post.return_value = valid_auth_response

                # Should authenticate but fail silently on cache write
                sessionid = auth.authenticate(mock_http_client)
                assert sessionid == "valid_session_123"

            cache_dir.chmod(0o755)  # Restore for cleanup

    def test_corrupted_cache_file(self, mock_settings):
        """Test handling of corrupted cache file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content {{{")
            cache_file = f.name

        try:
            auth = AuthManager(mock_settings)

            with patch.object(auth, '_cache_file', cache_file):
                # Should handle corrupted cache gracefully
                cached = auth._load_cached_session()
                assert cached is None
        finally:
            Path(cache_file).unlink()


# ============================================================================
# Network Failure Tests
# ============================================================================

class TestAuthManagerNetworkFailures:
    """Test authentication with network failures"""

    def test_connection_timeout(self, mock_settings, mock_http_client):
        """Test authentication with connection timeout"""
        auth = AuthManager(mock_settings)

        mock_http_client.post.side_effect = httpx.TimeoutException("Connection timeout")

        with pytest.raises(TimeoutError, match="Connection timeout"):
            auth.authenticate(mock_http_client)

    def test_connection_refused(self, mock_settings, mock_http_client):
        """Test authentication when connection is refused"""
        auth = AuthManager(mock_settings)

        mock_http_client.post.side_effect = httpx.ConnectError("Connection refused")

        with pytest.raises(ConnectionError, match="Connection refused"):
            auth.authenticate(mock_http_client)

    def test_ssl_verification_failure(self, mock_settings, mock_http_client):
        """Test authentication with SSL certificate verification failure"""
        auth = AuthManager(mock_settings)

        mock_http_client.post.side_effect = httpx.SSLError("SSL verification failed")

        with pytest.raises(IPTVPortalError, match="SSL"):
            auth.authenticate(mock_http_client)


# ============================================================================
# Async Authentication Tests
# ============================================================================

class TestAsyncAuthManagerEdgeCases:
    """Test async authentication manager edge cases"""

    @pytest.mark.asyncio
    async def test_async_invalid_credentials(self, mock_settings):
        """Test async authentication with invalid credentials"""
        auth = AsyncAuthManager(mock_settings)
        mock_client = Mock(spec=httpx.AsyncClient)

        mock_response = Mock()
        mock_response.json.return_value = {
            "error": {"message": "Invalid credentials", "code": 401}
        }
        mock_response.raise_for_status = Mock()
        mock_client.post = MagicMock(return_value=mock_response)

        with pytest.raises(AuthenticationError, match="Invalid credentials"):
            await auth.authenticate(mock_client)

    @pytest.mark.asyncio
    async def test_async_concurrent_authentication(self, mock_settings):
        """Test concurrent authentication requests"""
        import asyncio

        async def authenticate_task(auth, client):
            return await auth.authenticate(client)

        auth = AsyncAuthManager(mock_settings)
        mock_client = Mock(spec=httpx.AsyncClient)

        mock_response = Mock()
        mock_response.json.return_value = {
            "result": {"sessionid": "concurrent123"}
        }
        mock_response.raise_for_status = Mock()

        async def mock_post(*args, **kwargs):
            await asyncio.sleep(0.1)  # Simulate network delay
            return mock_response

        mock_client.post = mock_post

        # Run multiple concurrent authentications
        tasks = [authenticate_task(auth, mock_client) for _ in range(5)]
        results = await asyncio.gather(*tasks)

        # All should succeed with same session ID
        assert all(r == "concurrent123" for r in results)


# ============================================================================
# Retry Mechanism Tests
# ============================================================================

class TestAuthManagerRetryLogic:
    """Test retry mechanism with exponential backoff"""

    def test_retry_on_transient_failure(self, mock_settings, mock_http_client):
        """Test retry succeeds after transient failures"""
        auth = AuthManager(mock_settings)

        # First two calls fail, third succeeds
        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise httpx.TimeoutException("Temporary timeout")

            mock_response = Mock()
            mock_response.json.return_value = {
                "result": {"sessionid": "retry123"}
            }
            mock_response.raise_for_status = Mock()
            return mock_response

        mock_http_client.post.side_effect = side_effect

        sessionid = auth.authenticate(mock_http_client)
        assert sessionid == "retry123"
        assert call_count == 3

    def test_retry_exhausted_raises_error(self, mock_settings, mock_http_client):
        """Test that error is raised after max retries exhausted"""
        auth = AuthManager(mock_settings)

        mock_http_client.post.side_effect = httpx.TimeoutException("Persistent timeout")

        with pytest.raises(TimeoutError, match="Persistent timeout"):
            auth.authenticate(mock_http_client)

        # Should have tried max_retries + 1 times
        assert mock_http_client.post.call_count == 4  # 1 initial + 3 retries
