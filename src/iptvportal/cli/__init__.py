"""CLI module for IPTVPortal SDK."""

from iptvportal.cli.auth import CLIAuthManager
from iptvportal.cli.main import app

__all__ = ["CLIAuthManager", "app"]
