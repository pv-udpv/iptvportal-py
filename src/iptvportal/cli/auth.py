"""Authentication manager for CLI with session reuse and config persistence."""

import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from getpass import getpass
from pydantic import SecretStr, ValidationError
from iptvportal.config import IPTVPortalSettings
from iptvportal import IPTVPortalClient
from iptvportal.exceptions import IPTVPortalError

console = Console()


class CLIAuthManager:
    """Manages CLI authentication with session reuse and config persistence."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize auth manager.

        Args:
            config_path: Path to YAML config (relative or absolute).
                        Falls back to IPTVPORTAL_CONFIG env var if not provided.
        """
        self.config_path = self._resolve_config_path(config_path)
        self.config_data: Dict[str, Any] = {}

    def _resolve_config_path(self, path: Optional[str]) -> Path:
        """
        Resolve config file path from argument or environment.

        Priority:
        1. Provided path argument
        2. IPTVPORTAL_CONFIG environment variable
        3. Default: ~/.config/iptvportal/config.yaml

        Args:
            path: Optional path string

        Returns:
            Resolved Path object
        """
        if path:
            resolved = Path(path).expanduser().resolve()
        elif env_path := os.getenv("IPTVPORTAL_CONFIG"):
            resolved = Path(env_path).expanduser().resolve()
        else:
            resolved = Path.home() / ".config" / "iptvportal" / "config.yaml"

        return resolved

    def load_config(self) -> Dict[str, Any]:
        """
        Load existing YAML config if present.

        Returns:
            Configuration dictionary
        """
        if self.config_path.exists():
            try:
                with open(self.config_path, "r") as f:
                    self.config_data = yaml.safe_load(f) or {}
                console.print(
                    f"[green]✓[/green] Loaded config from {self.config_path}"
                )
            except Exception as e:
                console.print(f"[yellow]⚠[/yellow] Could not load config: {e}")
                self.config_data = {}
        else:
            console.print(f"[dim]No config found at {self.config_path}[/dim]")
            self.config_data = {}

        return self.config_data

    def save_config(self, data: Dict[str, Any]) -> None:
        """
        Save configuration to YAML file.

        Args:
            data: Configuration dictionary to save
        """
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.config_path, "w") as f:
            yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)

        console.print(f"[green]✓[/green] Saved config to {self.config_path}")

    def get_credentials_interactive(self) -> Dict[str, str]:
        """
        Gather credentials interactively with env var defaults.

        Environment variables checked:
        - IPTVPORTAL_DOMAIN
        - IPTVPORTAL_CLIENT__USERNAME
        - IPTVPORTAL_CLIENT__PASSWORD

        Returns:
            Dictionary with domain, username, password
        """
        console.print(
            Panel.fit(
                "[bold cyan]IPTVPortal Authentication[/bold cyan]\n"
                "Enter credentials (press Enter to use default from env vars)",
                border_style="cyan",
            )
        )

        # Load existing config
        existing = self.load_config()

        # Get domain
        domain_default = os.getenv("IPTVPORTAL_DOMAIN") or existing.get("domain", "")
        domain = Prompt.ask(
            "Domain", default=domain_default if domain_default else None
        )

        # Get username
        username_default = os.getenv("IPTVPORTAL_CLIENT__USERNAME") or existing.get(
            "username", ""
        )
        username = Prompt.ask(
            "Username", default=username_default if username_default else None
        )

        # Get password (hidden input)
        password_env = os.getenv("IPTVPORTAL_CLIENT__PASSWORD")
        if password_env:
            use_env = Confirm.ask(
                "Use password from IPTVPORTAL_CLIENT__PASSWORD env var?", default=True
            )
            password = password_env if use_env else getpass("Password: ")
        else:
            password = getpass("Password: ")

        return {"domain": domain, "username": username, "password": password}

    def authenticate_with_reuse(
        self,
        domain: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        force_new: bool = False,
    ) -> IPTVPortalClient:
        """
        Authenticate with session token reuse.

        Args:
            domain: Override domain
            username: Override username
            password: Override password
            force_new: Force new authentication even if session exists

        Returns:
            Authenticated IPTVPortalClient instance

        Raises:
            ValidationError: If configuration is invalid
            IPTVPortalError: If authentication fails
        """
        # Load existing config
        config = self.load_config()

        # Check for existing valid session
        if not force_new and "session" in config:
            session_data = config["session"]

            try:
                console.print("[cyan]Attempting to reuse existing session...[/cyan]")

                settings = IPTVPortalSettings(
                    domain=session_data.get("domain"),
                    username=session_data.get("username"),
                    password=SecretStr("dummy"),  # Not needed for session reuse
                )

                client = IPTVPortalClient(settings=settings)
                client.sessionid = session_data.get("session_id")
                client.connect()

                # Test session validity with simple query
                try:
                    client.query.select(data=["id"], from_="subscriber", limit=1)
                    console.print(
                        "[green]✓[/green] Session is valid, reusing token"
                    )
                    return client
                except Exception:
                    console.print(
                        "[yellow]⚠[/yellow] Session expired, re-authenticating..."
                    )
                    client.close()

            except Exception as e:
                console.print(f"[yellow]⚠[/yellow] Session reuse failed: {e}")

        # Get credentials (interactive if not provided)
        if not all([domain, username, password]):
            creds = self.get_credentials_interactive()
            domain = domain or creds["domain"]
            username = username or creds["username"]
            password = password or creds["password"]

        # Ask to save config
        should_save = Confirm.ask(
            f"Save configuration to {self.config_path}?", default=True
        )

        # Create new authenticated client
        try:
            settings = IPTVPortalSettings(
                domain=domain, username=username, password=SecretStr(password)
            )

            with console.status("[cyan]Authenticating...[/cyan]"):
                client = IPTVPortalClient(settings=settings)
                client.connect()

            console.print("[green]✓[/green] Authentication successful")

            # Save session if requested
            if should_save:
                config["domain"] = domain
                config["username"] = username
                config["session"] = {
                    "domain": domain,
                    "username": username,
                    "session_id": client.sessionid,
                }
                self.save_config(config)

            return client

        except ValidationError as e:
            console.print(f"[red]✗[/red] Invalid configuration: {e}")
            raise
        except IPTVPortalError as e:
            console.print(f"[red]✗[/red] Authentication failed: {e}")
            raise
