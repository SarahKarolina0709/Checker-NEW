#!/usr/bin/env python3
"""
Upload-Probleme Fix für die Checker App
Behebt Probleme mit dem Upload-Bereich, speziell Icon-Sichtbarkeit
"""

import os
import sys
import customtkinter as ctk
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui_theme import UITheme

class UploadTestApp(ctk.CTk):
    """Test-App für Upload-Funktionalität"""
    
    def __init__(self):
        super().__init__()
        
        self.title("Upload Test - Checker App")
        self.geometry("600x400")
        
        # Set theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        self.create_upload_test()
    
    def create_upload_test(self):
        """Erstellt Test-Upload-Bereich"""
        
        # Header
        header = ctk.CTkLabel(
            self,
            text="Upload-Test",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        header.pack(pady=20)
        
        # Upload-Bereich
        upload_frame = ctk.CTkFrame(self)
        upload_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Upload-Icon (großes Emoji als Fallback)
        icon_label = ctk.CTkLabel(
            upload_frame,
            text="📤",
            font=ctk.CTkFont(size=64)
        )
        icon_label.pack(pady=(20, 10))
        
        # Upload-Text
        text_label = ctk.CTkLabel(
            upload_frame,
            text="Dateien hierher ziehen oder Button klicken",
            font=ctk.CTkFont(size=16)
        )
        text_label.pack(pady=10)
        
        # Upload-Button mit Emoji als Icon-Ersatz
        upload_button = ctk.CTkButton(
            upload_frame,
            text="📤 Datei auswählen",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=50,
            width=200,
            command=self.upload_file_action
        )
        upload_button.pack(pady=20)
        
        # Status-Label
        self.status_label = ctk.CTkLabel(
            upload_frame,
            text="Status: Bereit zum Upload",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=10)
        
        # Test-Button für verschiedene Icons
        test_frame = ctk.CTkFrame(upload_frame)
        test_frame.pack(fill="x", padx=20, pady=10)
        
        # Test verschiedene Emoji-Icons
        emojis = ["📤", "⬆️", "➕", "📁", "📋", "📝"]
        for i, emoji in enumerate(emojis):
            btn = ctk.CTkButton(
                test_frame,
                text=emoji,
                width=40,
                height=40,
                font=ctk.CTkFont(size=20),
                command=lambda e=emoji: self.change_icon(e)
            )
            btn.grid(row=0, column=i, padx=5, pady=5)
    
    def upload_file_action(self):
        """Simulates file upload action"""
        from tkinter import filedialog
        
        file_path = filedialog.askopenfilename(
            title="Wählen Sie eine Datei aus",
            filetypes=[("Alle Dateien", "*.*")]
        )
        
        if file_path:
            filename = os.path.basename(file_path)
            self.status_label.configure(text=f"Status: Datei ausgewählt - {filename}")
            print(f"Datei ausgewählt: {file_path}")
        else:
            self.status_label.configure(text="Status: Kein Datei ausgewählt")
    
    def change_icon(self, emoji):
        """Ändert das Upload-Icon"""
        # Finde das Icon-Label und ändere es
        for widget in self.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                for child in widget.winfo_children():
                    if isinstance(child, ctk.CTkLabel) and child.cget("font").cget("size") == 64:
                        child.configure(text=emoji)
                        self.status_label.configure(text=f"Status: Icon geändert zu {emoji}")
                        break

def main():
    """Hauptfunktion"""
    print("=== Upload-Test wird gestartet ===")
    print("Dieser Test zeigt:")
    print("1. Wie der Upload-Bereich aussehen sollte")
    print("2. Verschiedene Icon-Optionen")
    print("3. Upload-Button Funktionalität")
    print()
    
    app = UploadTestApp()
    app.mainloop()

if __name__ == "__main__":
    main()
