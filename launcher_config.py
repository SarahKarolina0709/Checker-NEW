#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 Advanced Launcher Configuration Manager
==========================================

Enterprise-Grade Configuration System für den Translation Quality Checker.
Ermöglicht erweiterte Konfiguration von Startup-Verhalten, Performance-Settings
und System-Präferenzen.
"""

import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class LauncherConfig:
    """📋 Launcher Configuration Data Class"""
    
    # Startup Preferences
    preferred_system: str = "modular"
    auto_detect_best: bool = True
    show_performance_report: bool = True
    enable_diagnostics: bool = False
    
    # UI Preferences
    startup_splash: bool = True
    color_output: bool = True
    verbose_logging: bool = False
    
    # Performance Settings
    preload_modules: bool = True
    cache_module_info: bool = True
    parallel_loading: bool = False
    
    # System Settings
    fallback_timeout: int = 30
    max_retries: int = 3
    backup_system: str = "main"
    
    # Advanced Features
    interactive_mode_default: bool = False
    auto_update_check: bool = False
    telemetry_enabled: bool = False

class LauncherConfigManager:
    """🔧 Advanced Configuration Manager"""
    
    def __init__(self, config_file: str = "launcher_config.json"):
        self.config_file = config_file
        self.config = LauncherConfig()
        self._load_config()
    
    def _load_config(self) -> None:
        """📖 Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Update config with loaded data
                for key, value in data.items():
                    if hasattr(self.config, key):
                        setattr(self.config, key, value)
                
                print(f"✅ Konfiguration geladen: {self.config_file}")
            else:
                # Create default config
                self._save_config()
                print(f"📝 Standard-Konfiguration erstellt: {self.config_file}")
                
        except Exception as e:
            print(f"⚠️ Fehler beim Laden der Konfiguration: {e}")
            print("📋 Verwende Standard-Einstellungen")
    
    def _save_config(self) -> None:
        """💾 Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.config), f, indent=4, ensure_ascii=False)
            
        except Exception as e:
            print(f"❌ Fehler beim Speichern der Konfiguration: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """🔍 Get configuration value"""
        return getattr(self.config, key, default)
    
    def set(self, key: str, value: Any) -> bool:
        """✏️ Set configuration value"""
        try:
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                self._save_config()
                return True
            else:
                print(f"⚠️ Unbekannter Konfigurationsschlüssel: {key}")
                return False
        except Exception as e:
            print(f"❌ Fehler beim Setzen der Konfiguration: {e}")
            return False
    
    def reset_to_defaults(self) -> None:
        """🔄 Reset to default configuration"""
        self.config = LauncherConfig()
        self._save_config()
        print("🔄 Konfiguration auf Standard zurückgesetzt")
    
    def show_config(self) -> None:
        """📊 Show current configuration"""
        print("\n📋 AKTUELLE KONFIGURATION")
        print("=" * 40)
        
        config_dict = asdict(self.config)
        for category in ["Startup Preferences", "UI Preferences", "Performance Settings", "System Settings", "Advanced Features"]:
            print(f"\n{category}:")
            
            # Map categories to config keys (simplified)
            if "Startup" in category:
                keys = ["preferred_system", "auto_detect_best", "show_performance_report", "enable_diagnostics"]
            elif "UI" in category:
                keys = ["startup_splash", "color_output", "verbose_logging"]
            elif "Performance" in category:
                keys = ["preload_modules", "cache_module_info", "parallel_loading"]
            elif "System" in category:
                keys = ["fallback_timeout", "max_retries", "backup_system"]
            else:  # Advanced
                keys = ["interactive_mode_default", "auto_update_check", "telemetry_enabled"]
            
            for key in keys:
                if key in config_dict:
                    value = config_dict[key]
                    print(f"  • {key.replace('_', ' ').title():<25}: {value}")
        
        print("=" * 40)
    
    def interactive_config(self) -> None:
        """🎮 Interactive configuration editor"""
        print("\n🎮 INTERAKTIVE KONFIGURATION")
        print("=" * 40)
        print("1. Startup-Einstellungen")
        print("2. UI-Einstellungen") 
        print("3. Performance-Einstellungen")
        print("4. System-Einstellungen")
        print("5. Erweiterte Einstellungen")
        print("6. Aktuelle Konfiguration anzeigen")
        print("7. Auf Standard zurücksetzen")
        print("0. Beenden")
        
        try:
            choice = input("\nWählen Sie eine Option (0-7): ").strip()
            
            if choice == "1":
                self._edit_startup_settings()
            elif choice == "2":
                self._edit_ui_settings()
            elif choice == "3":
                self._edit_performance_settings()
            elif choice == "4":
                self._edit_system_settings()
            elif choice == "5":
                self._edit_advanced_settings()
            elif choice == "6":
                self.show_config()
            elif choice == "7":
                confirm = input("Wirklich auf Standard zurücksetzen? (j/N): ")
                if confirm.lower() in ['j', 'ja', 'y', 'yes']:
                    self.reset_to_defaults()
            elif choice == "0":
                print("👋 Konfiguration beendet")
                return
            else:
                print("❌ Ungültige Auswahl")
            
            # Continue editing
            self.interactive_config()
            
        except KeyboardInterrupt:
            print("\n👋 Konfiguration abgebrochen")
    
    def _edit_startup_settings(self) -> None:
        """⚙️ Edit startup settings"""
        print("\n⚙️ STARTUP-EINSTELLUNGEN")
        print(f"Aktuelles bevorzugtes System: {self.config.preferred_system}")
        
        systems = ["welcome", "modular", "main", "legacy", "fallback"]
        print("Verfügbare Systeme:", ", ".join(systems))
        
        new_system = input("Neues bevorzugtes System (Enter für keine Änderung): ").strip()
        if new_system and new_system in systems:
            self.set("preferred_system", new_system)
            print(f"✅ Bevorzugtes System geändert zu: {new_system}")
    
    def _edit_ui_settings(self) -> None:
        """🎨 Edit UI settings"""
        print("\n🎨 UI-EINSTELLUNGEN")
        
        settings = [
            ("startup_splash", "Startup-Splash anzeigen"),
            ("color_output", "Farbige Ausgabe"),
            ("verbose_logging", "Ausführliches Logging")
        ]
        
        for key, description in settings:
            current = getattr(self.config, key)
            print(f"{description}: {current}")
            
            toggle = input(f"Ändern? (j/N): ").strip().lower()
            if toggle in ['j', 'ja', 'y', 'yes']:
                self.set(key, not current)
                print(f"✅ {description} geändert zu: {not current}")
    
    def _edit_performance_settings(self) -> None:
        """🚀 Edit performance settings"""
        print("\n🚀 PERFORMANCE-EINSTELLUNGEN")
        
        settings = [
            ("preload_modules", "Module vorladen"),
            ("cache_module_info", "Modul-Info cachen"),
            ("parallel_loading", "Paralleles Laden")
        ]
        
        for key, description in settings:
            current = getattr(self.config, key)
            print(f"{description}: {current}")
            
            toggle = input(f"Ändern? (j/N): ").strip().lower()
            if toggle in ['j', 'ja', 'y', 'yes']:
                self.set(key, not current)
                print(f"✅ {description} geändert zu: {not current}")
    
    def _edit_system_settings(self) -> None:
        """🔧 Edit system settings"""
        print("\n🔧 SYSTEM-EINSTELLUNGEN")
        print(f"Fallback-Timeout: {self.config.fallback_timeout}s")
        print(f"Max. Wiederholungen: {self.config.max_retries}")
        print(f"Backup-System: {self.config.backup_system}")
        
        # Simple editing for now
        try:
            timeout = input("Neuer Timeout (Enter für keine Änderung): ").strip()
            if timeout:
                self.set("fallback_timeout", int(timeout))
                print(f"✅ Timeout geändert zu: {timeout}s")
        except ValueError:
            print("❌ Ungültiger Timeout-Wert")
    
    def _edit_advanced_settings(self) -> None:
        """🔬 Edit advanced settings"""
        print("\n🔬 ERWEITERTE EINSTELLUNGEN")
        
        settings = [
            ("interactive_mode_default", "Interaktiver Modus als Standard"),
            ("auto_update_check", "Automatische Update-Prüfung"),
            ("telemetry_enabled", "Telemetrie aktiviert")
        ]
        
        for key, description in settings:
            current = getattr(self.config, key)
            print(f"{description}: {current}")
            
            toggle = input(f"Ändern? (j/N): ").strip().lower()
            if toggle in ['j', 'ja', 'y', 'yes']:
                self.set(key, not current)
                print(f"✅ {description} geändert zu: {not current}")

# Global configuration manager instance
config_manager = LauncherConfigManager()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--config":
        config_manager.interactive_config()
    else:
        config_manager.show_config()
