"""
Zentralisiertes Logging-System für die Checker-App
"""
import logging
import sys
from datetime import datetime
from pathlib import Path

class AppLogger:
    """Zentrale Logging-Konfiguration für die Checker-App"""
    
    _instance = None
    _logger = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._setup_logging()
        return cls._instance
    
    @classmethod
    def _setup_logging(cls):
        """Konfiguriert das Logging-System"""
        # Logger erstellen
        cls._logger = logging.getLogger('checker_app')
        cls._logger.setLevel(logging.DEBUG)
        
        # Verhindere doppelte Handler
        if cls._logger.handlers:
            return
        
        # Formatters
        console_formatter = logging.Formatter(
            '[%(levelname)s] %(name)s: %(message)s'
        )
        
        file_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s.%(funcName)s:%(lineno)d - %(message)s'
        )
        
        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        cls._logger.addHandler(console_handler)
        
        # File Handler
        try:
            log_dir = Path('logs')
            log_dir.mkdir(exist_ok=True)
            
            log_file = log_dir / f'checker_app_{datetime.now().strftime("%Y%m%d")}.log'
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(file_formatter)
            cls._logger.addHandler(file_handler)
        except Exception as e:
            cls._logger.warning(f"Could not create file handler: {e}")
    
    @classmethod
    def get_logger(cls, name=None):
        """Gibt den konfigurierten Logger zurück"""
        if cls._logger is None:
            cls()
        
        if name:
            return cls._logger.getChild(name)
        return cls._logger

# Convenience functions
def get_logger(name=None):
    """Shortcut für Logger-Erstellung"""
    return AppLogger.get_logger(name)

# Component-spezifische Logger
def get_ui_logger():
    return get_logger('ui')

def get_workflow_logger():
    return get_logger('workflow')

def get_icon_logger():
    return get_logger('icon')

def get_button_logger():
    return get_logger('button')
