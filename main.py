# Startet die Checker-Anwendung

import sys
import os

# Fügt das Hauptverzeichnis zum Python-Pfad hinzu, um die `core`-Module zu finden
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from core.app import CheckerApp

if __name__ == "__main__":
    app = CheckerApp()
    app.mainloop()
