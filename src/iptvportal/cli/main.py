"""Main CLI application for IPTVPortal SDK."""

import typer
import yaml
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from iptvportal.cli.auth import CLIAuthManager

app = typer.Typer(
    name="iptvportal",
    help="IPTVPortal CLI - Manage subscribers, terminals, and media",
    add_completion=True,
)
console = Console()


@app.callback()
def main(
    ctx: typer.Context,
    config: Optional[str] = typer.Option(
        None,
        "--config",
        "-c",
        envvar="IPTVPORTAL_CONFIG",
        help="Path to YAML config file (relative or absolute)",
    ),
    domain: Optional[str] = typer.Option(
        None,
        "--domain",
        envvar="IPTVPORTAL_DOMAIN",
        help="IPTVPortal domain",
    ),
    username: Optional[str] = typer.Option(
        None,
        "--username",
        "-u",
        envvar="IPTVPORTAL_CLIENT__USERNAME",
        help="Username for authentication",
    ),
    password: Optional[str] = typer.Option(
        None,
        "--password",
        "-p",
        envvar="IPTVPORTAL_CLIENT__PASSWORD",
        help="Password for authentication",
    ),
    force_auth: bool = typer.Option(
        False,
        "--force-auth",
        help="Force new authentication (ignore cached session)",
    ),
):
    """
    Global options for IPTVPortal CLI.

    Authentication priority:
    1. Cached session token (if valid)
    2. Command-line arguments
    3. Environment variables
    4. Interactive prompts
    5. YAML config file
    """
    auth_manager = CLIAuthManager(config_path=config)

    try:
        client = auth_manager.authenticate_with_reuse(
            domain=domain,
            username=username,
            password=password,
            force_new=force_auth,
        )
        ctx.obj = {"client": client, "auth_manager": auth_manager}
    except Exception as e:
        console.print(f"[red]Failed to authenticate: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def auth(
    ctx: typer.Context,
    force: bool = typer.Option(False, "--force", help="Force new authentication"),
):
    """
    Authenticate and save session.

    Example:
        iptvportal auth
        iptvportal auth --force
        iptvportal --config ./myconfig.yaml auth
    """
    if force or ctx.obj is None:
        auth_manager = CLIAuthManager()
        client = auth_manager.authenticate_with_reuse(force_new=True)
        console.print("[green]✓[/green] Authentication complete")
        client.close()
    else:
        console.print("[green]✓[/green] Already authenticated")


@app.command()
def config_show(ctx: typer.Context):
    """
    Display current configuration.

    Example:
        iptvportal config-show
    """
    auth_manager: CLIAuthManager = ctx.obj["auth_manager"]
    config = auth_manager.load_config()

    # Mask sensitive data
    display_config = config.copy()
    if "session" in display_config and "session_id" in display_config["session"]:
        display_config["session"]["session_id"] = "***MASKED***"

    console.print(
        Panel.fit(
            yaml.dump(display_config, default_flow_style=False),
            title="[cyan]Current Configuration[/cyan]",
            border_style="cyan",
        )
    )


@app.command()
def config_path(ctx: typer.Context):
    """
    Show config file path.

    Example:
        iptvportal config-path
    """
    auth_manager: CLIAuthManager = ctx.obj["auth_manager"]
    console.print(f"Config path: [cyan]{auth_manager.config_path}[/cyan]")


if __name__ == "__main__":
    app()
