# config.py
# central config file for the project

import logging
import logging.handlers
import sys
from pathlib import Path

# Define the model name
MODEL_NAME = "deepseek-r1:8b"

# Logging Configuration
LOG_LEVEL = logging.INFO  # Change to DEBUG for more verbose output
LOG_FORMAT = "%(asctime)s [%(levelname)8s] %(name)s: %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# Log file paths
LOG_FILE = LOGS_DIR / "autoanki.log"
ERROR_LOG_FILE = LOGS_DIR / "autoanki_errors.log"


def setup_logging(log_level: int = None, enable_file_logging: bool = True) -> logging.Logger:
    """
    Set up centralized logging configuration for AutoAnki.
    
    Args:
        log_level: Logging level (defaults to LOG_LEVEL from config)
        enable_file_logging: Whether to write logs to files
        
    Returns:
        Configured logger instance
    """
    if log_level is None:
        log_level = LOG_LEVEL
    
    # Get the root logger
    logger = logging.getLogger("autoanki")
    
    # Avoid duplicate handlers if already configured
    if logger.handlers:
        return logger
    
    logger.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    
    # Console handler with colors for different levels
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    if enable_file_logging:
        # File handler for all logs (rotating)
        file_handler = logging.handlers.RotatingFileHandler(
            LOG_FILE, maxBytes=10*1024*1024, backupCount=5  # 10MB files, keep 5 backups
        )
        file_handler.setLevel(logging.DEBUG)  # Log everything to file
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Separate file handler for errors only
        error_handler = logging.handlers.RotatingFileHandler(
            ERROR_LOG_FILE, maxBytes=5*1024*1024, backupCount=3  # 5MB files, keep 3 backups
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)
    
    return logger


def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger instance for a specific module/component.
    
    Args:
        name: Logger name (typically __name__ from the calling module)
        
    Returns:
        Logger instance
    """
    if name is None:
        name = "autoanki"
    elif not name.startswith("autoanki"):
        name = f"autoanki.{name}"
    
    return logging.getLogger(name)


# Initialize logging when config is imported
_main_logger = setup_logging()