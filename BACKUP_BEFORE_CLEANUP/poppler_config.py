"""
Poppler Configuration Manager für Checker-App
Automatische Erkennung und Konfiguration von Poppler-Pfaden
"""

import os
import sys
from pathlib import Path


class PopplerConfig:
    """Verwaltet Poppler-Konfiguration und automatische Pfad-Erkennung"""
    
    def __init__(self):
        self.poppler_path = None
        self.is_configured = False
        self.detect_poppler()
    
    def detect_poppler(self):
        """Automatische Erkennung des Poppler-Pfads"""
        
        # 1. Prüfe Umgebungsvariable POPPLER_PATH
        env_path = os.getenv("POPPLER_PATH")
        if env_path and self.validate_poppler_path(env_path):
            self.poppler_path = env_path
            self.is_configured = True
            print(f"[OK] Poppler gefunden via POPPLER_PATH: {env_path}")
            return
        
        # 2. Lokale Poppler-Installation im Checker-Verzeichnis
        checker_dir = Path(__file__).parent
        local_poppler_paths = [
            checker_dir / "poppler" / "bin",
            checker_dir / "poppler-24.08.0" / "poppler-24.08.0" / "Library" / "bin",
            checker_dir / "tools" / "poppler" / "bin"
        ]
        
        for path in local_poppler_paths:
            if self.validate_poppler_path(str(path)):
                self.poppler_path = str(path)
                self.is_configured = True
                print(f"[OK] Lokale Poppler-Installation gefunden: {path}")
                return
        
        # 3. Standard Windows-Installationspfade
        if os.name == 'nt':
            standard_paths = [
                r"C:\Tools\poppler-24.08.0\poppler-24.08.0\Library\bin",
                r"C:\Program Files\poppler\bin",
                r"C:\Program Files (x86)\poppler\bin",
                r"C:\poppler\bin",
                r"C:\Tools\poppler\bin"
            ]
            
            for path in standard_paths:
                if self.validate_poppler_path(path):
                    self.poppler_path = path
                    self.is_configured = True
                    print(f"[OK] System Poppler-Installation gefunden: {path}")
                    return
        
        # 4. PATH-Suche
        if self.check_poppler_in_path():
            self.poppler_path = None  # None bedeutet: verwende PATH
            self.is_configured = True
            print("[OK] Poppler im System PATH gefunden")
            return
        
        # Nicht gefunden
        print("[FEHLER] Poppler nicht gefunden!")
        self.suggest_installation()
    
    def validate_poppler_path(self, path):
        """Validiert einen Poppler-Pfad"""
        if not path or not os.path.exists(path):
            return False
        
        # Prüfe auf wichtige Poppler-Executables
        required_files = ['pdftoppm.exe', 'pdfinfo.exe'] if os.name == 'nt' else ['pdftoppm', 'pdfinfo']
        
        for file in required_files:
            if not os.path.exists(os.path.join(path, file)):
                return False
        
        return True
    
    def check_poppler_in_path(self):
        """Prüft ob Poppler im System PATH verfügbar ist"""
        try:
            from pdf2image import convert_from_path
            from io import BytesIO
            
            # Teste mit einem minimalen PDF
            test_result = self.create_test_pdf_and_convert()
            return test_result
        except Exception:
            return False
    
    def create_test_pdf_and_convert(self):
        """Erstellt ein Test-PDF und prüft die Konvertierung"""
        try:
            # Minimaler Test ohne echte PDF-Erstellung
            # Nur prüfen ob pdf2image ohne poppler_path funktioniert
            import subprocess
            result = subprocess.run(['pdftoppm', '-h'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            return False
    
    def get_poppler_path(self):
        """Gibt den konfigurierten Poppler-Pfad zurück"""
        return self.poppler_path if self.is_configured else None
    
    def setup_environment(self):
        """Setzt Umgebungsvariablen für Poppler"""
        if self.is_configured and self.poppler_path:
            os.environ["POPPLER_PATH"] = self.poppler_path
            print(f"[KONFIG] POPPLER_PATH gesetzt: {self.poppler_path}")
    
    def suggest_installation(self):
        """Schlägt Installationsschritte vor"""
        print("\n[KONFIG] POPPLER INSTALLATION ERFORDERLICH")
        print("=" * 50)
        
        if os.name == 'nt':
            print("Windows-Installation:")
            print("1. Lade Poppler herunter: https://github.com/oschwartz10612/poppler-windows/releases/")
            print("2. Entpacke nach: C:\\Tools\\poppler\\")
            print("3. Füge C:\\Tools\\poppler\\bin zum System PATH hinzu")
            print("4. ODER setze Umgebungsvariable: POPPLER_PATH=C:\\Tools\\poppler\\bin")
            print("\nAlternativ: Lokale Installation im Checker-Verzeichnis:")
            print(f"- Entpacke Poppler nach: {Path(__file__).parent}\\poppler\\")
        else:
            print("Linux/macOS Installation:")
            print("Ubuntu/Debian: sudo apt-get install poppler-utils")
            print("CentOS/RHEL: sudo yum install poppler-utils")
            print("macOS: brew install poppler")
    
    def get_status_info(self):
        """Gibt Statusinformationen zurück"""
        status = {
            'configured': self.is_configured,
            'path': self.poppler_path,
            'method': 'PATH' if (self.is_configured and not self.poppler_path) else 'Explicit Path'
        }
        return status


def auto_configure_poppler():
    """Automatische Poppler-Konfiguration für die gesamte App"""
    config = PopplerConfig()
    
    if config.is_configured:
        config.setup_environment()
        return config
    else:
        print("[WARNUNG] Warnung: Poppler nicht konfiguriert - PDF-Verarbeitung eingeschränkt")
        return None


def get_poppler_path_for_pdf2image():
    """Gibt den Poppler-Pfad für pdf2image zurück"""
    config = PopplerConfig()
    return config.get_poppler_path()


# Globale Konfiguration beim Import
POPPLER_CONFIG = auto_configure_poppler()


if __name__ == "__main__":
    # Test-Modus
    print("Poppler Configuration Test")
    print("=" * 30)
    
    config = PopplerConfig()
    status = config.get_status_info()
    
    print(f"Konfiguriert: {status['configured']}")
    print(f"Pfad: {status['path'] or 'System PATH'}")
    print(f"Methode: {status['method']}")
    
    if not config.is_configured:
        config.suggest_installation()
