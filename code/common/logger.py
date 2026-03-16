"""
Logging utility for the bug hunter system
"""
from loguru import logger
import sys
from common.config import LOG_LEVEL, LOG_FORMAT

# Remove default handler
logger.remove()

# Add custom handler
logger.add(
    sys.stdout,
    format=LOG_FORMAT,
    level=LOG_LEVEL,
    colorize=True
)

# Add file handler
logger.add(
    "logs/bug_hunter_{time:YYYY-MM-DD}.log",
    format=LOG_FORMAT,
    level="DEBUG",
    rotation="1 day",
    retention="7 days",
    compression="zip"
)

def get_logger(name: str):
    """Get a logger with a specific name"""
    return logger.bind(name=name)
