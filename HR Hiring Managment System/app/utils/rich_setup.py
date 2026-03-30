"""
Rich-powered terminal output: colored logs, tracebacks, and startup banners.
"""
from __future__ import annotations

import logging
import sys
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.text import Text
from rich.traceback import install as install_rich_traceback
from rich import box

# Single shared console for banners (stderr so it stays above uvicorn noise when possible)
_console: Optional[Console] = None


def get_console() -> Console:
    global _console
    if _console is None:
        _console = Console(stderr=True, soft_wrap=True)
    return _console


def configure_rich_logging(level: str = "INFO") -> None:
    """
    Replace default logging with RichHandler for readable, colored log lines.
    Call once at process startup (before other modules emit logs if possible).
    """
    install_rich_traceback(show_locals=False, width=min(120, Console().width))

    log_level = getattr(logging, str(level).upper(), logging.INFO)
    rich_handler = RichHandler(
        console=get_console(),
        show_time=True,
        show_path=True,
        rich_tracebacks=True,
        tracebacks_show_locals=False,
        markup=True,
        log_time_format="[%Y-%m-%d %H:%M:%S]",
        omit_repeated_times=False,
    )

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(log_level)
    root.addHandler(rich_handler)

    # Quieter third-party noise unless debugging
    logging.getLogger("watchfiles").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)


def print_banner(title: str, subtitle: str, version: str) -> None:
    c = get_console()
    c.print()
    text = Text.assemble(
        (title, "bold cyan"),
        "\n",
        (subtitle, "dim"),
        "\n",
        ("v", "dim"),
        (version, "bold white"),
    )
    c.print(
        Panel.fit(
            text,
            border_style="cyan",
            box=box.ROUNDED,
            title="[bold]Fealty HR[/bold]",
            subtitle="[dim]API Service[/dim]",
        )
    )
    c.print()


def print_shutdown_banner(message: str = "Shutdown complete") -> None:
    c = get_console()
    c.print(
        Panel(
            f"[dim]{message}[/dim]",
            border_style="yellow",
            box=box.ROUNDED,
            title="[bold yellow]Stopped[/bold yellow]",
        )
    )
