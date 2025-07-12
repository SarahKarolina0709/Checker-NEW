"""
Environment Configuration System
===============================

A flexible configuration system that adapts to different environments
(development, testing, production) with sensible defaults and overrides.

Features:
- Environment-specific configuration
- Secret management
- Configuration validation
- Hot reloading
- Observability
"""

import os
import json
import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union, List, Callable
from dataclasses import dataclass, field
import threading
from datetime import datetime

# Environment constants
ENV_DEVELOPMENT = "development"
ENV_TESTING = "testing"
ENV_PRODUCTION = "production"

@dataclass
class ConfigEnvironment:
    """Configuration environment with values and metadata."""
    name: str
    values: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    description: str = ""
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a config value with default fallback."""
        return self.values.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a config value."""
        self.values[key] = value


class EnvironmentConfig:
    """
    Environment-specific configuration system.
    
    Manages configuration for different environments (development, testing, production)
    with environment detection, defaults, and overrides.
    """
    
    def __init__(self, app_name: str = "checker"):
        """Initialize with application name."""
        self.app_name = app_name
        self.logger = logging.getLogger(__name__)
        self.environments: Dict[str, ConfigEnvironment] = {}
        self.current_env_name: str = self._detect_environment()
        self._config_path = self._get_config_path()
        self._secrets_path = self._get_secrets_path()
        self._observers: List[Callable[[str, Any], None]] = []
        self._lock = threading.RLock()
        
        # Initialize environments
        self._init_environments()
        
        # Load configuration files
        self._load_config()
        
        self.logger.info(f"Environment configuration initialized: {self.current_env_name}")
    
    def _detect_environment(self) -> str:
        """Detect the current environment."""
        # Check environment variable
        env = os.environ.get("CHECKER_ENV", "").lower()
        if env in [ENV_DEVELOPMENT, ENV_TESTING, ENV_PRODUCTION]:
            return env
        
        # Check for testing indicators
        if any(test_indicator in sys.modules for test_indicator in ["pytest", "unittest", "nose"]):
            return ENV_TESTING
        
        # Default to development in debug/IDE environments, production otherwise
        if hasattr(sys, 'gettrace') and sys.gettrace():
            return ENV_DEVELOPMENT
        
        return ENV_PRODUCTION
    
    def _get_config_path(self) -> Path:
        """Get the path to the configuration files."""
        # Check for environment-specific config path
        env_config_path = os.environ.get("CHECKER_CONFIG_PATH")
        if env_config_path:
            return Path(env_config_path)
        
        # Default to standard locations based on platform
        if os.name == "nt":  # Windows
            return Path(os.path.expanduser("~")) / "AppData" / "Local" / self.app_name / "config"
        else:  # Unix-like
            return Path(os.path.expanduser("~")) / f".{self.app_name}" / "config"
    
    def _get_secrets_path(self) -> Path:
        """Get the path to the secrets files."""
        # Similar to config path but for secrets
        env_secrets_path = os.environ.get("CHECKER_SECRETS_PATH")
        if env_secrets_path:
            return Path(env_secrets_path)
        
        return self._config_path / "secrets"
    
    def _init_environments(self) -> None:
        """Initialize the environment configurations with defaults."""
        with self._lock:
            # Development environment
            self.environments[ENV_DEVELOPMENT] = ConfigEnvironment(
                name=ENV_DEVELOPMENT,
                description="Development environment for local development",
                values={
                    "debug": True,
                    "log_level": "DEBUG",
                    "enable_dev_tools": True,
                    "show_performance_metrics": True,
                    "auto_reload_templates": True,
                    "use_mock_services": True,
                    "window_size": {
                        "width": 1280,
                        "height": 800,
                        "min_width": 800,
                        "min_height": 600,
                        "start_maximized": False
                    }
                }
            )
            
            # Testing environment
            self.environments[ENV_TESTING] = ConfigEnvironment(
                name=ENV_TESTING,
                description="Testing environment for automated tests",
                values={
                    "debug": True,
                    "log_level": "DEBUG",
                    "enable_dev_tools": False,
                    "show_performance_metrics": False,
                    "use_mock_services": True,
                    "skip_animations": True,
                    "testing_mode": True,
                    "window_size": {
                        "width": 1024,
                        "height": 768,
                        "min_width": 800,
                        "min_height": 600,
                        "start_maximized": False
                    }
                }
            )
            
            # Production environment
            self.environments[ENV_PRODUCTION] = ConfigEnvironment(
                name=ENV_PRODUCTION,
                description="Production environment for end users",
                values={
                    "debug": False,
                    "log_level": "INFO",
                    "enable_dev_tools": False,
                    "show_performance_metrics": False,
                    "use_mock_services": False,
                    "crash_reporting": True,
                    "telemetry_enabled": True,
                    "update_check_enabled": True,
                    "window_size": {
                        "width": 1280,
                        "height": 800,
                        "min_width": 800,
                        "min_height": 600,
                        "start_maximized": True
                    }
                }
            )
    
    def _load_config(self) -> None:
        """Load configuration from files."""
        with self._lock:
            try:
                # Create config directory if it doesn't exist
                os.makedirs(self._config_path, exist_ok=True)
                
                # Load global config if exists
                global_config_path = self._config_path / "config.json"
                if global_config_path.exists():
                    with open(global_config_path, "r", encoding="utf-8") as f:
                        global_config = json.load(f)
                        for env_name, env in self.environments.items():
                            if env_name in global_config:
                                env.values.update(global_config[env_name])
                
                # Load environment-specific config if exists
                env_config_path = self._config_path / f"{self.current_env_name}.json"
                if env_config_path.exists():
                    with open(env_config_path, "r", encoding="utf-8") as f:
                        env_config = json.load(f)
                        self.environments[self.current_env_name].values.update(env_config)
                
                # Load secrets if exists (only load current environment's secrets)
                os.makedirs(self._secrets_path, exist_ok=True)
                secrets_path = self._secrets_path / f"{self.current_env_name}_secrets.json"
                if secrets_path.exists():
                    with open(secrets_path, "r", encoding="utf-8") as f:
                        secrets = json.load(f)
                        # Store secrets in a special _secrets section to separate them
                        self.environments[self.current_env_name].values["_secrets"] = secrets
            
            except Exception as e:
                self.logger.error(f"Error loading configuration: {e}")
                # Continue with defaults
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value for the current environment.
        
        Args:
            key: The configuration key
            default: Default value if key not found
            
        Returns:
            The configuration value
        """
        with self._lock:
            # Get from current environment
            env = self.environments.get(self.current_env_name)
            if env:
                # Check if the key is a nested path (e.g., "window_size.width")
                if "." in key:
                    parts = key.split(".")
                    value = env.values
                    for part in parts:
                        if isinstance(value, dict) and part in value:
                            value = value[part]
                        else:
                            return default
                    return value
                
                return env.get(key, default)
            return default
    
    def set(self, key: str, value: Any, persist: bool = False) -> None:
        """
        Set a configuration value for the current environment.
        
        Args:
            key: The configuration key
            value: The configuration value
            persist: Whether to persist the change to the config file
        """
        with self._lock:
            env = self.environments.get(self.current_env_name)
            if not env:
                return
            
            # Handle nested keys
            if "." in key:
                parts = key.split(".")
                config_dict = env.values
                for part in parts[:-1]:
                    if part not in config_dict:
                        config_dict[part] = {}
                    config_dict = config_dict[part]
                config_dict[parts[-1]] = value
            else:
                env.set(key, value)
            
            # Notify observers
            for observer in self._observers:
                try:
                    observer(key, value)
                except Exception as e:
                    self.logger.error(f"Error notifying observer: {e}")
            
            # Persist if requested
            if persist:
                self._save_config()
    
    def _save_config(self) -> None:
        """Save the current environment configuration to file."""
        with self._lock:
            try:
                env_config_path = self._config_path / f"{self.current_env_name}.json"
                os.makedirs(self._config_path, exist_ok=True)
                
                # Save without secrets
                save_values = self.environments[self.current_env_name].values.copy()
                if "_secrets" in save_values:
                    del save_values["_secrets"]
                
                with open(env_config_path, "w", encoding="utf-8") as f:
                    json.dump(save_values, f, indent=2, ensure_ascii=False)
                
                # Save secrets separately if they exist
                secrets = self.environments[self.current_env_name].values.get("_secrets")
                if secrets:
                    secrets_path = self._secrets_path / f"{self.current_env_name}_secrets.json"
                    os.makedirs(self._secrets_path, exist_ok=True)
                    with open(secrets_path, "w", encoding="utf-8") as f:
                        json.dump(secrets, f, indent=2, ensure_ascii=False)
                
                self.logger.debug(f"Configuration saved for environment: {self.current_env_name}")
                
            except Exception as e:
                self.logger.error(f"Error saving configuration: {e}")
    
    def get_secret(self, key: str, default: Any = None) -> Any:
        """
        Get a secret value for the current environment.
        
        Args:
            key: The secret key
            default: Default value if key not found
            
        Returns:
            The secret value
        """
        with self._lock:
            env = self.environments.get(self.current_env_name)
            if env and "_secrets" in env.values:
                return env.values["_secrets"].get(key, default)
            return default
    
    def set_secret(self, key: str, value: Any, persist: bool = False) -> None:
        """
        Set a secret value for the current environment.
        
        Args:
            key: The secret key
            value: The secret value
            persist: Whether to persist the change to the secrets file
        """
        with self._lock:
            env = self.environments.get(self.current_env_name)
            if not env:
                return
            
            # Create _secrets dict if it doesn't exist
            if "_secrets" not in env.values:
                env.values["_secrets"] = {}
            
            env.values["_secrets"][key] = value
            
            # Persist if requested
            if persist:
                self._save_config()
    
    def register_observer(self, observer: Callable[[str, Any], None]) -> None:
        """
        Register an observer to be notified of configuration changes.
        
        Args:
            observer: A callable that takes (key, value) arguments
        """
        if observer not in self._observers:
            self._observers.append(observer)
    
    def unregister_observer(self, observer: Callable[[str, Any], None]) -> None:
        """
        Unregister an observer.
        
        Args:
            observer: The observer to unregister
        """
        if observer in self._observers:
            self._observers.remove(observer)
    
    def reload(self) -> None:
        """Reload configuration from files."""
        self._load_config()
    
    def is_dev_mode(self) -> bool:
        """Check if running in development mode."""
        return self.current_env_name == ENV_DEVELOPMENT
    
    def is_test_mode(self) -> bool:
        """Check if running in test mode."""
        return self.current_env_name == ENV_TESTING
    
    def is_prod_mode(self) -> bool:
        """Check if running in production mode."""
        return self.current_env_name == ENV_PRODUCTION
    
    def set_environment(self, env_name: str) -> None:
        """
        Manually set the current environment.
        
        Args:
            env_name: The environment name (development, testing, production)
        """
        if env_name in self.environments:
            self.current_env_name = env_name
            self.logger.info(f"Environment switched to: {env_name}")
        else:
            self.logger.error(f"Invalid environment: {env_name}")
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration values for the current environment.
        
        Returns:
            Dictionary of all configuration values
        """
        with self._lock:
            env = self.environments.get(self.current_env_name)
            if env:
                # Return a copy without secrets
                config = env.values.copy()
                if "_secrets" in config:
                    del config["_secrets"]
                return config
            return {}


# Create singleton instance
config = EnvironmentConfig()

# Convenience functions
def get_config(key: str, default: Any = None) -> Any:
    """Get a configuration value."""
    return config.get(key, default)

def set_config(key: str, value: Any, persist: bool = False) -> None:
    """Set a configuration value."""
    config.set(key, value, persist)

def get_secret(key: str, default: Any = None) -> Any:
    """Get a secret value."""
    return config.get_secret(key, default)

def set_secret(key: str, value: Any, persist: bool = False) -> None:
    """Set a secret value."""
    config.set_secret(key, value, persist)

def is_dev_mode() -> bool:
    """Check if running in development mode."""
    return config.is_dev_mode()

def is_test_mode() -> bool:
    """Check if running in test mode."""
    return config.is_test_mode()

def is_prod_mode() -> bool:
    """Check if running in production mode."""
    return config.is_prod_mode()
