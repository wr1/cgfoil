"""Logger configuration with rich formatting."""

import logging
import sys

from rich.console import Console
from rich.logging import RichHandler

logging.basicConfig(
    level="INFO",
    format="%(message)s",
    handlers=[
        RichHandler(
            rich_tracebacks=True,
            console=Console(file=sys.stdout),
            show_time=False,
        ),
    ],
)

logger = logging.getLogger("cgfoil")
