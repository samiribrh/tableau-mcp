"""Centralized logging configuration."""
import logging
import sys

from src.config.settings import settings  # Updated import!


def setup_logging(level: str = None) -> None:
    """Configure application-wide logging."""
    log_level = level or settings.log_level
    
    format_string = (
        "%(asctime)s - %(name)s - %(levelname)s - "
        "%(filename)s:%(lineno)d - %(message)s"
    )
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=format_string,
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("tableauserverclient").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a specific module."""
    return logging.getLogger(name)
