"""
Poppler Status Widget für die Checker-App
Zeigt den aktuellen Poppler-Konfigurationsstatus in der UI an
"""

import customtkinter as ctk
from poppler_config import POPPLER_CONFIG
import os


class PopplerStatusWidget:
    """Widget zur Anzeige des Poppler-Status in der UI"""
    
    def __init__(self, parent):
        self.parent = parent
        self.status_frame = None
        self.create_status_widget()
      def create_status_widget(self):
        """Erstellt das Status-Widget"""
        
        # Clear any existing status frame to avoid conflicts
        if self.status_frame:
            try:
                self.status_frame.destroy()
            except:
                pass
        
        # Status Frame
        self.status_frame = ctk.CTkFrame(
            self.parent,
            corner_radius=8,
            height=60
        )
        
        # Status ermitteln
        if POPPLER_CONFIG and POPPLER_CONFIG.is_configured:
            status_info = POPPLER_CONFIG.get_status_info()
            
            # Erfolgs-Status
            self.status_frame.configure(fg_color=("lightgreen", "darkgreen"))
            
            status_label = ctk.CTkLabel(
                self.status_frame,
                text="🔧 PDF-Engine",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="white"
            )
            status_label.pack(side="left", padx=10, pady=5)
            
            # Details
            path_text = "System PATH" if not status_info['path'] else os.path.basename(status_info['path'])
            detail_label = ctk.CTkLabel(
                self.status_frame,
                text=f"✅ Poppler aktiv ({path_text})",
                font=ctk.CTkFont(size=10),
                text_color="white"
            )
            detail_label.pack(side="left", padx=(0, 10), pady=5)
            
        else:
            # Fehler-Status
            self.status_frame.configure(fg_color=("orange", "darkorange"))
            
            status_label = ctk.CTkLabel(
                self.status_frame,
                text="⚠️ PDF-Engine",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="white"
            )
            status_label.pack(side="left", padx=10, pady=5)
            
            detail_label = ctk.CTkLabel(
                self.status_frame,
                text="❌ Poppler nicht verfügbar",
                font=ctk.CTkFont(size=10),
                text_color="white"
            )
            detail_label.pack(side="left", padx=(0, 10), pady=5)
            
            # Setup-Button
            setup_button = ctk.CTkButton(
                self.status_frame,
                text="Setup",
                width=60,
                height=25,
                command=self.open_setup_dialog,
                fg_color="white",
                text_color="black",
                hover_color="lightgray"
            )
            setup_button.pack(side="right", padx=10, pady=17)
    
    def open_setup_dialog(self):
        """Öffnet den Setup-Dialog für Poppler"""
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Poppler PDF-Engine Setup")
        dialog.geometry("500x350")
        dialog.grab_set()
        
        # Header
        header_label = ctk.CTkLabel(
            dialog,
            text="🔧 PDF-Engine (Poppler) Setup",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        header_label.pack(pady=20)
        
        # Status-Info
        info_frame = ctk.CTkFrame(dialog)
        info_frame.pack(fill="x", padx=20, pady=10)
        
        info_text = """
Die Checker-App benötigt Poppler für die PDF-Verarbeitung.
Poppler wurde nicht gefunden oder ist nicht konfiguriert.

Optionen:
1. Automatische Installation (Empfohlen)
2. Manuelle Installation
3. System-Installation verwenden
        """
        
        info_label = ctk.CTkLabel(
            info_frame,
            text=info_text.strip(),
            font=ctk.CTkFont(size=12),
            justify="left"
        )
        info_label.pack(padx=15, pady=15)
        
        # Buttons
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=20)
        
        auto_button = ctk.CTkButton(
            button_frame,
            text="🚀 Automatische Installation",
            command=lambda: self.start_auto_installation(dialog),
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        auto_button.pack(fill="x", pady=5)
        
        manual_button = ctk.CTkButton(
            button_frame,
            text="📋 Manuelle Anleitung",
            command=lambda: self.show_manual_guide(dialog),
            height=35,
            fg_color="gray"
        )
        manual_button.pack(fill="x", pady=5)
        
        close_button = ctk.CTkButton(
            button_frame,
            text="Schließen",
            command=dialog.destroy,
            height=30,
            fg_color="darkgray"
        )
        close_button.pack(fill="x", pady=5)
    
    def start_auto_installation(self, dialog):
        """Startet die automatische Installation"""
        import subprocess
        import threading
        
        def run_installation():
            try:
                # Führe das Installationsskript aus
                result = subprocess.run(
                    ["install_poppler.bat"],
                    cwd=os.path.dirname(__file__),
                    capture_output=True,
                    text=True,
                    shell=True
                )
                
                if result.returncode == 0:
                    # Erfolg - aktualisiere die Konfiguration
                    self.refresh_status()
                    dialog.destroy()
                else:
                    print(f"Installation fehlgeschlagen: {result.stderr}")
                    
            except Exception as e:
                print(f"Fehler bei der Installation: {e}")
        
        # Installation in separatem Thread starten
        thread = threading.Thread(target=run_installation)
        thread.daemon = True
        thread.start()
        
        dialog.destroy()
    
    def show_manual_guide(self, dialog):
        """Zeigt die manuelle Installationsanleitung"""
        guide_window = ctk.CTkToplevel(dialog)
        guide_window.title("Manuelle Poppler-Installation")
        guide_window.geometry("600x500")
        
        guide_text = """
MANUELLE POPPLER-INSTALLATION

Schritt 1: Download
• Gehen Sie zu: https://github.com/oschwartz10612/poppler-windows/releases/
• Laden Sie die neueste "Release-XX.XX.X-X.zip" herunter

Schritt 2: Installation
• Entpacken Sie die ZIP-Datei
• Kopieren Sie den Ordner nach: C:\\Tools\\poppler\\
  ODER in das Checker-Verzeichnis: poppler\\

Schritt 3: Pfad-Struktur
Stellen Sie sicher, dass folgende Struktur existiert:
• poppler\\bin\\pdftoppm.exe
• poppler\\bin\\pdfinfo.exe

Schritt 4: Umgebungsvariable (Optional)
• Setzen Sie POPPLER_PATH auf den bin-Ordner
• Beispiel: POPPLER_PATH=C:\\Tools\\poppler\\bin

Schritt 5: Test
• Starten Sie die Checker-App neu
• Der Status sollte sich automatisch aktualisieren

Alternative: System-Installation
• Installieren Sie Poppler über einen Paketmanager
• Fügen Sie den bin-Ordner zur PATH-Umgebungsvariable hinzu
        """
        
        text_widget = ctk.CTkTextbox(
            guide_window,
            font=ctk.CTkFont(family="Consolas", size=11)
        )
        text_widget.pack(fill="both", expand=True, padx=20, pady=20)
        text_widget.insert("1.0", guide_text.strip())
        text_widget.configure(state="disabled")
        
        close_btn = ctk.CTkButton(
            guide_window,
            text="Schließen",
            command=guide_window.destroy
        )
        close_btn.pack(pady=10)
    
    def refresh_status(self):
        """Aktualisiert den Status nach Änderungen"""
        # Entferne altes Widget
        if self.status_frame:
            self.status_frame.destroy()
        
        # Lade Konfiguration neu
        from poppler_config import PopplerConfig
        global POPPLER_CONFIG
        POPPLER_CONFIG = PopplerConfig()
        
        # Erstelle neues Widget
        self.create_status_widget()
      def pack(self, **kwargs):
        """Pack-Methode für einfache Integration"""
        if self.status_frame:
            # Ensure no grid manager is being used
            try:
                self.status_frame.grid_forget()
            except:
                pass
            self.status_frame.pack(**kwargs)


def create_poppler_status_widget(parent):
    """Factory-Funktion zur Erstellung des Status-Widgets (als Frame, nicht als Objekt)."""
    widget = PopplerStatusWidget(parent)
    return widget.status_frame


if __name__ == "__main__":
    # Test des Widgets
    import tkinter as tk
    
    root = tk.Tk()
    root.title("Poppler Status Test")
    root.geometry("400x200")
    
    widget = PopplerStatusWidget(root)
    widget.pack(fill="x", padx=20, pady=20)
    
    root.mainloop()
