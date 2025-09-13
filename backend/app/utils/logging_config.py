"""
Logging Configuration

Centralized logging setup for the application.
"""

import logging
import sys
from typing import Dict, Any

from app.core.config import settings


def setup_logging() -> None:
    """Setup application logging configuration"""
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )
    
    # Set specific logger levels
    loggers_config = {
        'uvicorn': logging.INFO,
        'fastapi': logging.INFO,
        'sqlalchemy.engine': logging.WARNING,
        'openai': logging.WARNING,
        'httpx': logging.WARNING,
    }
    
    for logger_name, level in loggers_config.items():
        logging.getLogger(logger_name).setLevel(level)
