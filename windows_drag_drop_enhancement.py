#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alternative Drag & Drop Lösung für Windows
"""

def install_tkdnd():
    """Installiert tkdnd für besseres Drag & Drop."""
    try:
        import subprocess
        import sys
        
        print("🔄 Installiere tkdnd für besseres Drag & Drop...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "tkdnd2"])
        print("✅ tkdnd erfolgreich installiert!")
        return True
    except Exception as e:
        print(f"❌ tkdnd Installation fehlgeschlagen: {e}")
        return False

def add_enhanced_drag_drop_to_checker():
    """Verbessert das Drag & Drop-System in der Checker-App."""
    
    # Alternative Implementierung für Drop-Zone
    enhanced_drop_zone_code = '''
    def _create_drop_zone_enhanced(self, parent):
        """Erstellt eine verbesserte Drag & Drop Zone mit besserer Windows-Kompatibilität."""
        drop_zone = ctk.CTkFrame(parent, fg_color="white", corner_radius=12, border_width=2, border_color="#DBEAFE")
        drop_zone.pack(fill="x", padx=10, pady=10)
        
        # Speichere Referenz für Drag & Drop
        self.drop_zone = drop_zone
        self.is_dragging = False
        
        # Content-Bereich
        upload_content = ctk.CTkFrame(drop_zone, fg_color="transparent")
        upload_content.pack(fill="x", padx=15, pady=15)
        
        # Icon
        drop_icon = ctk.CTkLabel(upload_content, text="📁", font=ctk.CTkFont(size=24))
        drop_icon.pack()
        
        # Text
        self.drop_text = ctk.CTkLabel(
            upload_content,
            text="Dateien hier ablegen oder klicken",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#1F2937"
        )
        self.drop_text.pack(pady=(5, 10))
        
        # Button
        upload_btn = ctk.CTkButton(
            upload_content,
            text="📂 Dateien auswählen",
            height=35,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#3B82F6",
            hover_color="#2563EB",
            command=self._select_upload_files
        )
        upload_btn.pack(fill="x")
        
        # Alle Widgets für Click und Hover
        widgets = [drop_zone, upload_content, drop_icon, self.drop_text]
        
        for widget in widgets:
            # Klick-Events
            widget.bind("<Button-1>", lambda e: self._select_upload_files())
            
            # Hover-Effects
            widget.bind("<Enter>", self._on_hover_enter)
            widget.bind("<Leave>", self._on_hover_leave)
        
        # Versuche erweiterte Drop-Funktionalität
        self._setup_enhanced_drop_events(widgets)
        
        return drop_zone
    
    def _setup_enhanced_drop_events(self, widgets):
        """Konfiguriert erweiterte Drop-Events."""
        
        # Versuche tkdnd2 wenn verfügbar
        try:
            import tkdnd2
            for widget in widgets:
                try:
                    widget.drop_target_register(tkdnd2.DND_FILES)
                    widget.dnd_bind('<<Drop>>', self._on_enhanced_drop)
                    widget.dnd_bind('<<DropEnter>>', self._on_enhanced_drag_enter)
                    widget.dnd_bind('<<DropLeave>>', self._on_enhanced_drag_leave)
                    print("✅ tkdnd2 Events erfolgreich registriert")
                except Exception as e:
                    print(f"tkdnd2 Widget-Registrierung fehlgeschlagen: {e}")
                    
        except ImportError:
            print("tkdnd2 nicht verfügbar - verwende alternative Methoden")
            
        # Alternative: Windows-spezifische Methoden
        self._setup_windows_drop_alternative(widgets)
    
    def _setup_windows_drop_alternative(self, widgets):
        """Alternative Windows-Drop-Lösung."""
        
        # Keyboard-Shortcuts als Alternative
        for widget in widgets:
            widget.bind("<Control-v>", self._paste_files_alternative)
            widget.bind("<Control-o>", lambda e: self._select_upload_files())
            
        # Mittlere Maustaste für spezielle Aktionen
        for widget in widgets:
            widget.bind("<Button-2>", self._middle_click_action)
            
        # Double-Click als Fallback
        for widget in widgets:
            widget.bind("<Double-Button-1>", lambda e: self._select_upload_files())
    
    def _on_enhanced_drop(self, event):
        """Erweiterte Drop-Event-Behandlung."""
        print("Enhanced Drop Event empfangen")
        
        files = []
        
        # tkdnd2 Format
        if hasattr(event, 'data'):
            file_paths = event.data.split()
            for path in file_paths:
                # Windows-spezifische Pfad-Bereinigung
                clean_path = path.strip('{}').strip()
                if os.path.isfile(clean_path):
                    files.append(clean_path)
        
        if files:
            print(f"Enhanced Drop: {len(files)} Dateien empfangen")
            self._process_dropped_files(files)
        else:
            print("Keine Dateien in Enhanced Drop gefunden")
            # Fallback: Dialog öffnen
            self._select_upload_files()
    
    def _on_enhanced_drag_enter(self, event):
        """Enhanced Drag Enter."""
        self.is_dragging = True
        if hasattr(self, 'drop_zone'):
            self.drop_zone.configure(border_color="#10B981", fg_color="#ECFDF5", border_width=3)
            self.drop_text.configure(text="Dateien jetzt loslassen\\n📁 ⬇️", text_color="#10B981")
    
    def _on_enhanced_drag_leave(self, event):
        """Enhanced Drag Leave."""
        self.is_dragging = False
        if hasattr(self, 'drop_zone'):
            self.drop_zone.configure(border_color="#DBEAFE", fg_color="white", border_width=2)
            self.drop_text.configure(text="Dateien hier ablegen oder klicken", text_color="#1F2937")
    
    def _on_hover_enter(self, event):
        """Hover-Effekt beim Betreten."""
        if not self.is_dragging and hasattr(self, 'drop_zone'):
            self.drop_zone.configure(border_color="#3B82F6", fg_color="#F8FAFC")
    
    def _on_hover_leave(self, event):
        """Hover-Effekt beim Verlassen.""" 
        if not self.is_dragging and hasattr(self, 'drop_zone'):
            self.drop_zone.configure(border_color="#DBEAFE", fg_color="white")
    
    def _paste_files_alternative(self, event):
        """Alternative: Einfügen via Strg+V."""
        try:
            # Versuche Dateipfade aus der Zwischenablage zu lesen
            clipboard_data = self.root.clipboard_get()
            
            if clipboard_data:
                # Parse mögliche Dateipfade
                files = self._parse_file_paths(clipboard_data)
                
                if files:
                    print(f"Dateien via Zwischenablage: {files}")
                    self._process_dropped_files(files)
                else:
                    # Fallback: Datei-Dialog
                    self._select_upload_files()
        except:
            # Fallback: Datei-Dialog
            self._select_upload_files()
    
    def _middle_click_action(self, event):
        """Mittlere Maustaste: Quick-Upload."""
        # Schneller Zugriff auf zuletzt verwendete Dateien oder Dialog
        self._select_upload_files()
    '''
    
    print("📋 Code für verbesserte Drag & Drop-Funktionalität bereit!")
    print("\nVerbesserungen:")
    print("✅ Bessere Windows-Kompatibilität")
    print("✅ tkdnd2-Unterstützung (falls verfügbar)")
    print("✅ Alternative Eingabemethoden (Strg+V, Strg+O)")
    print("✅ Verbesserte visuelle Feedback")
    print("✅ Fallback-Mechanismen")
    
    return enhanced_drop_zone_code

if __name__ == "__main__":
    print("🎯 Alternative Drag & Drop-Lösung für Checker App")
    print("=" * 50)
    
    # Versuche tkdnd zu installieren
    if install_tkdnd():
        print("\n✅ tkdnd ist jetzt verfügbar für besseres Drag & Drop!")
    else:
        print("\n⚠️ tkdnd nicht verfügbar - verwende alternative Methoden")
    
    # Zeige Code für Verbesserungen
    print("\n🔧 Verbesserte Drag & Drop-Implementierung:")
    code = add_enhanced_drag_drop_to_checker()
    
    print("\n📋 Integration:")
    print("1. Stoppe die laufende Checker-App")
    print("2. Ersetze _create_drop_zone() mit _create_drop_zone_enhanced()")
    print("3. Füge die neuen Methoden hinzu")
    print("4. Starte die App neu")
    
    print("\n🎯 Alternative Eingabemethoden:")
    print("• Strg+V: Einfügen von Dateipfaden aus Zwischenablage")
    print("• Strg+O: Datei-Dialog öffnen")
    print("• Doppelklick: Datei-Dialog öffnen")
    print("• Mittlere Maustaste: Quick-Upload")
