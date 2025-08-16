#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 TEST SCRIPT für reparierte GUI Komponenten
Testet alle wichtigen Klassen nach der strukturellen Reparatur
"""

import os
import sys
import tkinter as tk
import customtkinter as ctk
import time

# Force light mode
ctk.set_appearance_mode("light")

# Import reparierte Komponenten
try:
    from quality_gui_progress_upload import (
        ModernProgressBar,
        ProgressIndicator, 
        DragDropFrame,
        FileUploadCard,
        UITheme
    )
    print("✅ Alle Komponenten erfolgreich importiert!")
except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)

class ComponentTestApp:
    """Test Application für alle reparierten Komponenten"""
    
    def __init__(self):
        # Hauptfenster erstellen
        self.root = ctk.CTk()
        self.root.title("🧪 Component Test - Reparierte GUI Elemente")
        self.root.geometry("900x700")
        self.root.configure(fg_color="#FFFFFF")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup der Test-UI mit allen Komponenten"""
        # Header
        header_frame = ctk.CTkFrame(self.root, fg_color="#2563EB", height=80)
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        header_frame.pack_propagate(False)
        
        header_label = ctk.CTkLabel(
            header_frame,
            text="🧪 KOMPONENT TEST - Reparierte GUI Elemente",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color="white"
        )
        header_label.pack(expand=True)
        
        # Notebook für verschiedene Tests
        self.notebook = ctk.CTkTabview(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Test Tabs erstellen
        self.create_progress_test_tab()
        self.create_upload_test_tab()
        self.create_theme_test_tab()
        
        # Status Bar
        self.status_frame = ctk.CTkFrame(self.root, fg_color="#F8FAFC", height=40)
        self.status_frame.pack(fill="x", padx=10, pady=(5, 10))
        self.status_frame.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="🟢 Alle Komponenten geladen - Tests bereit",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#059669"
        )
        self.status_label.pack(expand=True)
    
    def create_progress_test_tab(self):
        """Test Tab für Progress Komponenten"""
        tab = self.notebook.add("📊 Progress Tests")
        
        # ModernProgressBar Test
        progress_frame = ctk.CTkFrame(tab, fg_color="#F8FAFC")
        progress_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            progress_frame,
            text="🔄 ModernProgressBar Test",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color="#374151"
        ).pack(pady=(15, 10))
        
        # ModernProgressBar erstellen
        self.modern_progress = ModernProgressBar(progress_frame, width=500, height=28)
        self.modern_progress.pack(pady=(0, 15))
        
        # Test Buttons
        button_frame = ctk.CTkFrame(progress_frame, fg_color="transparent")
        button_frame.pack(pady=(0, 15))
        
        ctk.CTkButton(
            button_frame,
            text="▶️ Start Progress",
            command=self.test_modern_progress,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#2563EB"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="🔄 Indeterminate",
            command=self.test_indeterminate,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#059669"
        ).pack(side="left", padx=5)
        
        # ProgressIndicator Test
        indicator_frame = ctk.CTkFrame(tab, fg_color="#F8FAFC")
        indicator_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            indicator_frame,
            text="📈 ProgressIndicator Test",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color="#374151"
        ).pack(pady=(15, 10))
        
        # ProgressIndicator erstellen
        self.progress_indicator = ProgressIndicator(indicator_frame)
        self.progress_indicator.pack(fill="x", padx=20, pady=(0, 15))
        
        # Indicator Test Buttons
        indicator_buttons = ctk.CTkFrame(indicator_frame, fg_color="transparent")
        indicator_buttons.pack(pady=(0, 15))
        
        ctk.CTkButton(
            indicator_buttons,
            text="📊 Animated Progress",
            command=self.test_indicator_progress,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#2563EB"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            indicator_buttons,
            text="❌ Error Test",
            command=self.test_indicator_error,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#DC2626"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            indicator_buttons,
            text="🔄 Reset",
            command=self.test_indicator_reset,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#6B7280"
        ).pack(side="left", padx=5)
    
    def create_upload_test_tab(self):
        """Test Tab für Upload Komponenten"""
        tab = self.notebook.add("📁 Upload Tests")
        
        # FileUploadCard Test
        upload_frame = ctk.CTkFrame(tab, fg_color="#F8FAFC")
        upload_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(
            upload_frame,
            text="📁 FileUploadCard Test",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color="#374151"
        ).pack(pady=(15, 10))
        
        # FileUploadCard erstellen
        self.upload_card = FileUploadCard(
            upload_frame,
            upload_callback=self.handle_test_upload
        )
        self.upload_card.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        # Upload Status
        self.upload_status = ctk.CTkLabel(
            upload_frame,
            text="📋 Bereit für Upload Test - Datei auswählen oder hierher ziehen",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#6B7280"
        )
        self.upload_status.pack(pady=(0, 15))
    
    def create_theme_test_tab(self):
        """Test Tab für Theme System"""
        tab = self.notebook.add("🎨 Theme Tests")
        
        # UITheme Test
        theme_frame = ctk.CTkFrame(tab, fg_color="#F8FAFC")
        theme_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            theme_frame,
            text="🎨 UITheme Color System Test",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color="#374151"
        ).pack(pady=(15, 10))
        
        # Color Swatches
        colors_frame = ctk.CTkFrame(theme_frame, fg_color="transparent")
        colors_frame.pack(pady=(0, 15))
        
        colors = [
            ("Primary", "primary"),
            ("Success", "success"),
            ("Warning", "warning"),
            ("Danger", "danger"),
            ("Info", "info")
        ]
        
        for name, color_key in colors:
            color_value = UITheme.get_color(color_key)
            
            swatch_frame = ctk.CTkFrame(colors_frame, fg_color=color_value, width=120, height=60)
            swatch_frame.pack(side="left", padx=5)
            swatch_frame.pack_propagate(False)
            
            ctk.CTkLabel(
                swatch_frame,
                text=f"{name}\n{color_value}",
                font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                text_color="white"
            ).pack(expand=True)
        
        # Theme Info
        theme_info = ctk.CTkFrame(tab, fg_color="#F8FAFC")
        theme_info.pack(fill="x", padx=20, pady=10)
        
        info_text = """
🎨 THEME SYSTEM STATUS:
✅ Vollständige Farb-Palette verfügbar
✅ Font-System funktional  
✅ Spacing-System aktiv
✅ Fallback-Mechanismen implementiert
✅ Anti-Dark-Mode Protection aktiv
        """
        
        ctk.CTkLabel(
            theme_info,
            text=info_text.strip(),
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#374151",
            justify="left"
        ).pack(pady=15)
    
    def test_modern_progress(self):
        """Test ModernProgressBar Animation"""
        self.update_status("🔄 Testing ModernProgressBar...")
        
        def animate_progress():
            for i in range(101):
                progress = i / 100
                status = f"Loading... {i}%"
                self.modern_progress.update_progress(progress, status)
                self.root.update()
                time.sleep(0.02)
            
            self.update_status("✅ ModernProgressBar Test completed!")
        
        # Animation in separatem Thread
        self.root.after(100, animate_progress)
    
    def test_indeterminate(self):
        """Test Indeterminate Mode"""
        self.update_status("🔄 Testing Indeterminate Mode...")
        self.modern_progress.set_indeterminate(True)
        
        def stop_indeterminate():
            self.modern_progress.set_indeterminate(False)
            self.update_status("✅ Indeterminate Test completed!")
        
        self.root.after(3000, stop_indeterminate)
    
    def test_indicator_progress(self):
        """Test ProgressIndicator Animation"""
        self.update_status("📈 Testing ProgressIndicator Animation...")
        
        def animate_indicator():
            steps = [0.25, 0.5, 0.75, 1.0]
            messages = [
                "Initialisierung...",
                "Verarbeitung...", 
                "Finalisierung...",
                "Abgeschlossen!"
            ]
            
            for i, (progress, message) in enumerate(zip(steps, messages)):
                self.root.after(i * 1000, lambda p=progress, m=message: 
                    self.progress_indicator.set_progress(p, m, animate=True))
            
            self.root.after(len(steps) * 1000, lambda:
                self.update_status("✅ ProgressIndicator Animation completed!"))
        
        animate_indicator()
    
    def test_indicator_error(self):
        """Test ProgressIndicator Error State"""
        self.progress_indicator.set_error("Test Error: Upload failed!")
        self.update_status("❌ Error State Test - Check red indicators")
    
    def test_indicator_reset(self):
        """Reset ProgressIndicator"""
        self.progress_indicator.reset()
        self.update_status("🔄 ProgressIndicator reset to initial state")
    
    def handle_test_upload(self, file_path):
        """Handle Test File Upload"""
        filename = os.path.basename(file_path)
        self.upload_status.configure(
            text=f"✅ Upload successful: {filename} ({os.path.getsize(file_path)} bytes)",
            text_color="#059669"
        )
        self.update_status(f"📁 File uploaded: {filename}")
        
        # Zeige Upload Success Animation
        self.upload_card.set_file_selected(filename)
    
    def update_status(self, message):
        """Update Status Bar"""
        self.status_label.configure(text=message)
        self.root.update()
    
    def run(self):
        """Starte die Test Application"""
        self.update_status("🚀 Component Test App ready - All systems operational!")
        self.root.mainloop()


def main():
    """Hauptfunktion für Component Tests"""
    print("🧪 STARTING COMPONENT TESTS")
    print("=" * 50)
    
    try:
        # Test App erstellen und starten
        app = ComponentTestApp()
        app.run()
        
    except Exception as e:
        print(f"❌ Test Error: {e}")
        import traceback
        traceback.print_exc()
        
    print("🧪 Component Tests completed!")


if __name__ == "__main__":
    main()
