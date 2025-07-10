# config.py
# central config file for the project

import logging
import logging.handlers
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Model Provider Configuration
MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "ollama").lower()

# Ollama Configuration
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-r1:8b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Hugging Face Configuration
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
HUGGINGFACE_MODEL = os.getenv("HUGGINGFACE_MODEL", "microsoft/DialoGPT-medium")

# Backward compatibility
MODEL_NAME = OLLAMA_MODEL

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


def validate_config():
    """
    Validate the current configuration and check for required settings.
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if MODEL_PROVIDER not in ["ollama", "huggingface"]:
        return False, f"Invalid MODEL_PROVIDER: {MODEL_PROVIDER}. Must be 'ollama' or 'huggingface'"
    
    if MODEL_PROVIDER == "huggingface":
        if not HUGGINGFACE_API_KEY or HUGGINGFACE_API_KEY == "your_huggingface_api_key_here":
            return False, "HUGGINGFACE_API_KEY is required when using Hugging Face provider"
        
        if not HUGGINGFACE_MODEL:
            return False, "HUGGINGFACE_MODEL is required when using Hugging Face provider"
    
    if MODEL_PROVIDER == "ollama":
        if not OLLAMA_MODEL:
            return False, "OLLAMA_MODEL is required when using Ollama provider"
    
    return True, None


def get_model_config():
    """
    Get the current model configuration based on the selected provider.
    
    Returns:
        dict: Configuration dictionary for the current model provider
    """
    if MODEL_PROVIDER == "huggingface":
        return {
            "provider": "huggingface",
            "model_name": HUGGINGFACE_MODEL,
            "api_key": HUGGINGFACE_API_KEY,
        }
    else:  # ollama
        return {
            "provider": "ollama",
            "model_name": OLLAMA_MODEL,
            "base_url": OLLAMA_BASE_URL,
        }


def create_llm_instance():
    """
    Create an LLM instance based on the configured provider.
    
    Returns:
        LLM instance compatible with LangChain
    """
    config = get_model_config()
    logger = get_logger(__name__)
    
    if config["provider"] == "huggingface":
        logger.info(f"🤗 Creating Hugging Face LLM with model: {config['model_name']}")
        # Import here to avoid dependency issues if not using HF
        from .llm_adapters import HuggingFaceLLM
        return HuggingFaceLLM(
            model_name=config["model_name"],
            api_key=config["api_key"]
        )
    else:  # ollama
        logger.info(f"🦙 Creating Ollama LLM with model: {config['model_name']}")
        from langchain_ollama import OllamaLLM
        return OllamaLLM(
            model=config["model_name"],
            base_url=config["base_url"]
        )


# Initialize logging when config is imported
_main_logger = setup_logging()

# Validate configuration on import
_is_valid, _error = validate_config()
if not _is_valid:
    _main_logger.error(f"❌ Configuration Error: {_error}")
    _main_logger.error("Please check your .env file and fix the configuration")
else:
    _main_logger.info(f"✅ Configuration validated successfully - using {MODEL_PROVIDER.upper()} provider")