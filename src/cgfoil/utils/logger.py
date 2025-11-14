"""Logger configuration with rich formatting."""

from rich.logging import RichHandler
from rich.console import Console
import logging
import sys

logging.basicConfig(
    level="INFO",
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True, console=Console(file=sys.stdout), show_time=False)],
)

logger = logging.getLogger("cgfoil")
