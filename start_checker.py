#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 Advanced Translation Quality Checker Launcher
===============================================

Enterprise-Grade Quick Launcher mit intelligenter System-Erkennung
und erweiterten Startup-Optionen für professionelle Arbeitsabläufe.

Features:
• Smart System Detection & Auto-Fallback
• Interactive Startup Mode mit Optionen
• Performance Monitoring & Diagnostics
• Advanced Error Handling & Recovery
• Multi-Mode Operation Support
"""

import subprocess
import sys
import os
import time
from typing import List, Tuple, Optional

# Import configuration manager
try:
    from launcher_config import config_manager
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    print("⚠️ Erweiterte Konfiguration nicht verfügbar")

class QualityCheckerLauncher:
    """🎯 Advanced Quality Checker Launcher with intelligent system detection"""
    
    def __init__(self):
        self.startup_time = time.time()
        self.available_systems = []
        self.launch_modes = {
            'welcome': 'welcome_screen.py',
            'modular': 'modern_translation_quality_gui_modular.py',
            'main': 'quality_gui_main_app.py', 
            'legacy': 'modern_translation_quality_gui.py',
            'fallback': 'checker_app_clean.py'
        }
        
        # Load configuration if available
        if CONFIG_AVAILABLE:
            self.config = config_manager.config
            self.show_performance = config_manager.get('show_performance_report', True)
            self.preferred_system = config_manager.get('preferred_system', 'modular')
            self.verbose = config_manager.get('verbose_logging', False)
        else:
            self.show_performance = True
            # Standardmäßig Welcome Screen als Einstiegspunkt
            self.preferred_system = 'welcome'
            self.verbose = False
    
    def detect_available_systems(self) -> List[Tuple[str, str, float]]:
        """🔍 Detect all available system variants with metadata"""
        systems = []
        
        for mode, filename in self.launch_modes.items():
            if os.path.exists(filename):
                try:
                    size = os.path.getsize(filename) / 1024  # KB
                    systems.append((mode, filename, size))
                    print(f"✅ {mode.capitalize():<12}: {filename:<35} ({size:>6.1f} KB)")
                except:
                    systems.append((mode, filename, 0))
                    print(f"✅ {mode.capitalize():<12}: {filename:<35} (Size unknown)")
            else:
                print(f"❌ {mode.capitalize():<12}: {filename:<35} (Not found)")
        
        self.available_systems = systems
        return systems
    
    def get_recommended_system(self) -> Optional[Tuple[str, str]]:
        """🎯 Get recommended system based on availability, features and user preferences"""
        if not self.available_systems:
            return None
        
        # Check user preference first
        if CONFIG_AVAILABLE and self.preferred_system:
            for mode, filename, size in self.available_systems:
                if mode == self.preferred_system:
                    if self.verbose:
                        print(f"🎯 Verwende Benutzer-Präferenz: {self.preferred_system}")
                    return (mode, filename)

        # Priority order: welcome > modular > main > legacy > fallback
        priority_order = ['welcome', 'modular', 'main', 'legacy', 'fallback']

        for preferred in priority_order:
            for mode, filename, size in self.available_systems:
                if mode == preferred:
                    if self.verbose:
                        print(f"🎯 Auto-Auswahl nach Priorität: {preferred}")
                    return (mode, filename)
        
        # If no priority match, return first available
        return (self.available_systems[0][0], self.available_systems[0][1])
    
    def launch_system(self, mode: str = None, interactive: bool = False) -> bool:
        """🚀 Launch quality checker system with advanced options"""
        try:
            print("🚀 Starte Translation Quality Checker...")
            print("=" * 60)
            
            # System detection
            print("🔍 Verfügbare Systeme:")
            self.detect_available_systems()
            
            if not self.available_systems:
                print("\n❌ Keine verfügbaren Systeme gefunden!")
                return False
            
            # Determine launch target
            if mode:
                # Specific mode requested
                target = next((f for m, f, s in self.available_systems if m == mode), None)
                if not target:
                    print(f"\n❌ Angeforderte Version '{mode}' nicht verfügbar")
                    return False
                launch_mode = mode
                launch_file = target
            else:
                # Auto-select recommended
                recommendation = self.get_recommended_system()
                if not recommendation:
                    print("\n❌ Keine empfohlene Version verfügbar")
                    return False
                launch_mode, launch_file = recommendation
            
            print(f"\n🎯 Gewähltes System: {launch_mode.capitalize()}")
            print(f"📁 Datei: {launch_file}")
            
            # Launch with options
            launch_args = [sys.executable, launch_file]
            
            if interactive:
                launch_args.append("--interactive")
            
            print(f"⚡ Starte Anwendung...")
            
            # Performance monitoring
            launch_start = time.time()
            
            # Execute
            result = subprocess.run(launch_args, 
                                  capture_output=False, 
                                  text=True,
                                  cwd=os.getcwd())
            
            launch_time = time.time() - launch_start
            total_time = time.time() - self.startup_time
            
            if self.show_performance:
                print(f"\n📊 Performance Report:")
                print(f"  • Launcher Zeit: {total_time:.2f}s")
                print(f"  • App Laufzeit: {launch_time:.2f}s")
            
            if result.returncode == 0:
                print("✅ Anwendung erfolgreich beendet")
                return True
            else:
                print(f"⚠️ Anwendung beendet mit Code: {result.returncode}")
                return False
                
        except KeyboardInterrupt:
            print("\n👋 Start abgebrochen durch Benutzer")
            return False
        except Exception as e:
            print(f"\n❌ Fehler beim Start: {e}")
            return False
    
    def interactive_mode(self) -> bool:
        """🎮 Interactive system selection and launch"""
        print("\n🎮 INTERAKTIVER MODUS")
        print("=" * 40)
        
        if not self.available_systems:
            print("❌ Keine Systeme verfügbar")
            return False
        
        print("Verfügbare Systeme:")
        for i, (mode, filename, size) in enumerate(self.available_systems, 1):
            print(f"  {i}. {mode.capitalize():<12} ({size:>6.1f} KB)")
        
        print("  0. Automatische Auswahl (empfohlen)")
        
        try:
            choice = input(f"\nWählen Sie System (0-{len(self.available_systems)}): ").strip()
            
            if choice == "0":
                return self.launch_system()
            
            choice_int = int(choice)
            if 1 <= choice_int <= len(self.available_systems):
                selected_mode = self.available_systems[choice_int - 1][0]
                return self.launch_system(mode=selected_mode)
            else:
                print("❌ Ungültige Auswahl")
                return False
                
        except (ValueError, KeyboardInterrupt):
            print("\n👋 Auswahl abgebrochen")
            return False
    
    def show_help(self):
        """📖 Show detailed help information"""
        print("\n🚀 TRANSLATION QUALITY CHECKER LAUNCHER")
        print("=" * 50)
        print("Verwendung: python start_checker.py [option]")
        print("\nOptionen:")
        print("  -w, --welcome       Welcome Screen (Standard)")
        print("  -i, --interactive    Interaktive System-Auswahl")
        print("  -m, --modular       Modulares System (bevorzugt)")
        print("  -l, --legacy        Legacy-System")
        print("  -f, --fallback      Fallback-System")
        print("  -d, --detect        Nur System-Erkennung")
        if CONFIG_AVAILABLE:
            print("  -c, --config        Konfiguration bearbeiten")
        print("  -h, --help          Diese Hilfe anzeigen")
        print("\nStandard: Welcome Screen, mit automatischer Fallback-Auswahl bei Bedarf")
        if CONFIG_AVAILABLE:
            print(f"Bevorzugtes System: {self.preferred_system}")
        print("\nVerfügbare Systeme werden automatisch erkannt und priorisiert.")

def start_quality_checker():
    """🚀 Legacy function wrapper for compatibility"""
    launcher = QualityCheckerLauncher()
    return launcher.launch_system()

if __name__ == "__main__":
    print()
    print("🔍 TRANSLATION QUALITY CHECKER LAUNCHER")
    print("=" * 50)
    print()
    
    launcher = QualityCheckerLauncher()
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg in ["-i", "--interactive"]:
            success = launcher.interactive_mode()
        elif arg in ["-w", "--welcome"]:
            success = launcher.launch_system(mode="welcome")
        elif arg in ["-m", "--modular"]:
            success = launcher.launch_system(mode="modular")
        elif arg in ["-l", "--legacy"]:
            success = launcher.launch_system(mode="legacy")
        elif arg in ["-f", "--fallback"]:
            success = launcher.launch_system(mode="fallback")
        elif arg in ["-d", "--detect"]:
            print("🔍 System-Erkennung:")
            launcher.detect_available_systems()
            recommendation = launcher.get_recommended_system()
            if recommendation:
                print(f"\n🎯 Empfehlung: {recommendation[0].capitalize()} ({recommendation[1]})")
                if CONFIG_AVAILABLE:
                    print(f"📋 Konfigurierte Präferenz: {launcher.preferred_system}")
            else:
                print("\n❌ Keine Empfehlung verfügbar")
            success = True
        elif arg in ["-c", "--config"] and CONFIG_AVAILABLE:
            config_manager.interactive_config()
            success = True
        elif arg in ["-c", "--config"] and not CONFIG_AVAILABLE:
            print("❌ Konfigurationssystem nicht verfügbar")
            success = False
        elif arg in ["-h", "--help"]:
            launcher.show_help()
            success = True
        else:
            print(f"❓ Unbekannte Option: {arg}")
            launcher.show_help()
            success = False
    else:
        # Standard automatic launch
        success = launcher.launch_system()
    
    if not success:
        print("\n❌ Start fehlgeschlagen")
        input("\nDrücken Sie Enter zum Beenden...")
    else:
        if len(sys.argv) <= 1 or sys.argv[1].lower() not in ["-d", "--detect", "-h", "--help"]:
            print("\n✅ Launcher erfolgreich ausgeführt")
    
    # Final performance summary
    total_runtime = time.time() - launcher.startup_time
    print(f"\n📊 Gesamt-Laufzeit: {total_runtime:.2f}s")
