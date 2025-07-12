"""
Zentrales Konfigurationsmanagement für die Checker-App
"""
import json
from pathlib import Path
from app_logger import get_logger

class ConfigManager:
    """Zentrale Konfigurationsverwaltung"""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._load_config()
        return cls._instance
    
    @classmethod
    def _load_config(cls):
        """Lädt die Konfiguration aus der JSON-Datei"""
        cls._logger = get_logger('config')
        
        try:
            config_path = Path('config.json')
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    cls._config = json.load(f)
                cls._logger.info("Configuration loaded successfully")
            else:
                cls._logger.warning("Config file not found, using defaults")
                cls._config = cls._get_default_config()
        except Exception as e:
            cls._logger.error(f"Error loading config: {e}")
            cls._config = cls._get_default_config()
    
    @classmethod
    def _get_default_config(cls):
        """Gibt Standard-Konfiguration zurück"""
        return {
            "app": {
                "name": "Checker-App",
                "version": "2.0.0",
                "window": {
                    "default_geometry": "1400x900",
                    "min_size": [1400, 900],
                    "max_size": [2560, 1440]
                }
            },
            "ui": {
                "theme": {
                    "appearance_mode": "light",
                    "color_theme": "blue",
                    "scaling": {
                        "widget_scaling": 1.0,
                        "window_scaling": 1.0,
                        "dpi_awareness": False
                    }
                }
            },
            "paths": {
                "icons": "icons",
                "logs": "logs"
            },
            "features": {
                "optimizations_enabled": False,
                "splash_screen": True
            }
        }
    
    def get(self, key_path, default=None):
        """
        Holt einen Konfigurationswert über einen Pfad
        
        Args:
            key_path: Pfad zum Wert (z.B. 'app.window.min_size')
            default: Standardwert falls nicht gefunden
        
        Returns:
            Der Konfigurationswert oder default
        """
        try:
            keys = key_path.split('.')
            value = self._config
            
            for key in keys:
                value = value[key]
            
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path, value):
        """
        Setzt einen Konfigurationswert
        
        Args:
            key_path: Pfad zum Wert
            value: Neuer Wert
        """
        try:
            keys = key_path.split('.')
            config = self._config
            
            for key in keys[:-1]:
                if key not in config:
                    config[key] = {}
                config = config[key]
            
            config[keys[-1]] = value
            self._logger.debug(f"Config updated: {key_path} = {value}")
        except Exception as e:
            self._logger.error(f"Error setting config {key_path}: {e}")
    
    def save(self):
        """Speichert die Konfiguration"""
        try:
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            self._logger.info("Configuration saved")
        except Exception as e:
            self._logger.error(f"Error saving config: {e}")

# Singleton-Instanz für globalen Zugriff
config = ConfigManager()
