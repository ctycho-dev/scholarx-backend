# app/core/logger.py
import os
import logging
import logging.config
import yaml
from typing import Optional


class LoggerManager:
    _instance: Optional['LoggerManager'] = None
    _initialized: bool = False

    def __new__(cls) -> 'LoggerManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._setup_logging()
            LoggerManager._initialized = True

    def _setup_logging(self):
        """Setup logging configuration once."""
        config_path = 'logger_config.yaml'
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                logging.config.dictConfig(config)
        else:
            # Fallback basic configuration
            logging.basicConfig(level=logging.INFO)

    def get_logger(self, name: str = 'root') -> logging.Logger:
        """Get logger instance."""
        return logging.getLogger(name)

    @classmethod
    def cleanup_log_file(cls, path: str = 'logout.log'):
        """Clean up log files."""
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            pass


# Global instance
logger_manager = LoggerManager()


def get_logger(name: str = 'root') -> logging.Logger:
    """Get logger instance - use this function across your app."""
    return logger_manager.get_logger(name)


def cleanup_logger():
    """Cleanup function for backward compatibility."""
    LoggerManager.cleanup_log_file()
