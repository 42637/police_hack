import os
import sys
from pathlib import Path
from loguru import logger

# Configure Loguru logger
def setup_logging():
    # Resolve backend logs directory
    backend_dir = Path(__file__).resolve().parent.parent.parent
    log_dir = backend_dir / "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = log_dir / "sentinel_ai.log"

    # Remove the default logger handler
    logger.remove()

    # Formatter for terminal (console)
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level:7}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    # Console Handler
    logger.add(
        sys.stderr,
        format=console_format,
        level="INFO",
        colorize=True
    )

    # File Handler for audit trails & analysis logs
    file_format = (
        "{time:YYYY-MM-DD HH:mm:ss} | {level:7} | {name}:{function}:{line} - {message}"
    )
    logger.add(
        str(log_file),
        format=file_format,
        level="DEBUG",
        rotation="10 MB",
        retention="30 days",
        compression="zip"
    )
    
    logger.info("Logging initialized. Output target: {}", log_file)

# Initialize on import
setup_logging()
