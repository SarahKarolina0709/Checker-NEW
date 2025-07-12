"""
Icon-Anpassungs-Demo für die Checker-App
Zeigt die Verwendung des Fluent Icon Managers
"""

import customtkinter as ctk
from fluent_icons_manager import FluentIconManager
import logging

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class IconCustomizationDemo:
    def __init__(self):
        """Initialisiert die Icon-Demo"""
        self.icon_manager = FluentIconManager("demo_icons_config.json")
        
        # Hauptfenster erstellen
        self.root = ctk.CTk()
        self.root.title("Fluent Icons Customization Demo")
        self.root.geometry("800x600")
        ctk.set_appearance_mode("light")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Erstellt die Demo-UI"""
        
        # Hauptframe
        main_frame = ctk.CTkScrollableFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Titel
        title = ctk.CTkLabel(
            main_frame,
            text=f"{self.icon_manager.get_icon('theme')} Fluent Icons Demo",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=(0, 20))
        
        # Aktuelle Icon-Sammlung anzeigen
        self.show_current_icons(main_frame)
        
        # Theme-Wechsel
        self.show_theme_switcher(main_frame)
        
        # Custom Icon hinzufügen
        self.show_custom_icon_creator(main_frame)
        
        # Icon-Suche
        self.show_icon_search(main_frame)
        
    def show_current_icons(self, parent):
        """Zeigt aktuell verfügbare Icons"""
        section_frame = ctk.CTkFrame(parent)
        section_frame.pack(fill="x", pady=(0, 15))
        
        title = ctk.CTkLabel(
            section_frame,
            text=f"{self.icon_manager.get_icon('folder')} Verfügbare Icons",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=10)
        
        # Icon-Grid
        icons_frame = ctk.CTkFrame(section_frame)
        icons_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        all_icons = self.icon_manager.get_all_available_icons()
        
        # Zeige eine Auswahl von Icons
        categories = {
            "Navigation": ['home', 'search', 'settings', 'help', 'menu'],
            "Files": ['file', 'folder', 'save', 'export', 'import'],
            "Workflow": ['workflow', 'process', 'check', 'success', 'error'],
            "User": ['user', 'customer', 'profile', 'account'],
            "UI": ['light_mode', 'dark_mode', 'theme', 'close', 'minimize']
        }
        
        for category, icon_names in categories.items():
            cat_label = ctk.CTkLabel(
                icons_frame,
                text=f"📂 {category}:",
                font=ctk.CTkFont(size=14, weight="bold"),
                anchor="w"
            )
            cat_label.pack(fill="x", padx=5, pady=(5, 0))
            
            icon_text = " | ".join([
                f"{self.icon_manager.get_icon(name)} {name}" 
                for name in icon_names if name in all_icons
            ])
            
            icon_display = ctk.CTkLabel(
                icons_frame,
                text=icon_text,
                font=ctk.CTkFont(size=12),
                anchor="w",
                wraplength=700
            )
            icon_display.pack(fill="x", padx=15, pady=2)
    
    def show_theme_switcher(self, parent):
        """Zeigt Theme-Wechsler"""
        section_frame = ctk.CTkFrame(parent)
        section_frame.pack(fill="x", pady=(0, 15))
        
        title = ctk.CTkLabel(
            section_frame,
            text=f"{self.icon_manager.get_icon('theme')} Theme-Wechsel",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=10)
        
        current_theme = ctk.CTkLabel(
            section_frame,
            text=f"Aktuelles Theme: {self.icon_manager.icon_theme}",
            font=ctk.CTkFont(size=14)
        )
        current_theme.pack(pady=5)
        
        button_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        button_frame.pack(pady=10)
        
        themes = ["fluent", "minimal", "classic", "custom"]
        for theme in themes:
            btn = ctk.CTkButton(
                button_frame,
                text=f"Theme: {theme}",
                command=lambda t=theme: self.switch_theme(t),
                width=120
            )
            btn.pack(side="left", padx=5)
    
    def show_custom_icon_creator(self, parent):
        """Zeigt Custom Icon Creator"""
        section_frame = ctk.CTkFrame(parent)
        section_frame.pack(fill="x", pady=(0, 15))
        
        title = ctk.CTkLabel(
            section_frame,
            text=f"{self.icon_manager.get_icon('settings')} Custom Icon erstellen",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=10)
        
        input_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        input_frame.pack(pady=10)
        
        # Icon Name
        name_label = ctk.CTkLabel(input_frame, text="Icon Name:")
        name_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.name_entry = ctk.CTkEntry(input_frame, placeholder_text="z.B. my_icon")
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Icon Value
        value_label = ctk.CTkLabel(input_frame, text="Icon (Emoji/Unicode):")
        value_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        
        self.value_entry = ctk.CTkEntry(input_frame, placeholder_text="z.B. 🚀 oder ⭐")
        self.value_entry.grid(row=1, column=1, padx=5, pady=5)
        
        create_btn = ctk.CTkButton(
            input_frame,
            text=f"{self.icon_manager.get_icon('success')} Erstellen",
            command=self.create_custom_icon,
            fg_color="#10B981"
        )
        create_btn.grid(row=2, column=0, columnspan=2, pady=10)
    
    def show_icon_search(self, parent):
        """Zeigt Icon-Suchfunktion"""
        section_frame = ctk.CTkFrame(parent)
        section_frame.pack(fill="x", pady=(0, 15))
        
        title = ctk.CTkLabel(
            section_frame,
            text=f"{self.icon_manager.get_icon('search')} Icon-Suche",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=10)
        
        search_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        search_frame.pack(pady=10)
        
        self.search_entry = ctk.CTkEntry(
            search_frame, 
            placeholder_text="Suchbegriff eingeben...",
            width=300
        )
        self.search_entry.pack(side="left", padx=5)
        
        search_btn = ctk.CTkButton(
            search_frame,
            text=f"{self.icon_manager.get_icon('search')} Suchen",
            command=self.search_icons,
            width=100
        )
        search_btn.pack(side="left", padx=5)
        
        # Suchergebnisse
        self.search_results = ctk.CTkTextbox(section_frame, height=100)
        self.search_results.pack(fill="x", padx=10, pady=10)
    
    def switch_theme(self, theme):
        """Wechselt das Icon-Theme"""
        self.icon_manager.set_theme(theme)
        logging.info(f"Theme gewechselt zu: {theme}")
        self.refresh_ui()
    
    def create_custom_icon(self):
        """Erstellt ein neues Custom Icon"""
        name = self.name_entry.get().strip()
        value = self.value_entry.get().strip()
        
        if not name or not value:
            logging.warning("Name und Wert müssen angegeben werden")
            return
        
        self.icon_manager.set_custom_icon(name, value)
        logging.info(f"Custom Icon erstellt: {name} = {value}")
        
        # Felder leeren
        self.name_entry.delete(0, 'end')
        self.value_entry.delete(0, 'end')
        
        self.refresh_ui()
    
    def search_icons(self):
        """Sucht Icons"""
        search_term = self.search_entry.get().strip()
        if not search_term:
            return
        
        results = self.icon_manager.search_icons(search_term)
        
        # Ergebnisse anzeigen
        self.search_results.delete("1.0", "end")
        if results:
            result_text = f"Gefundene Icons für '{search_term}':\n\n"
            for name, icon in results.items():
                result_text += f"{icon} {name}\n"
        else:
            result_text = f"Keine Icons gefunden für: '{search_term}'"
        
        self.search_results.insert("1.0", result_text)
        logging.info(f"Icon-Suche: '{search_term}' - {len(results)} Ergebnisse")
    
    def refresh_ui(self):
        """Aktualisiert die UI nach Änderungen"""
        # In einer echten Anwendung würde hier die gesamte UI neu geladen
        logging.info("UI-Refresh ausgeführt")
    
    def run(self):
        """Startet die Demo"""
        logging.info("Icon-Customization-Demo gestartet")
        self.root.mainloop()

if __name__ == "__main__":
    demo = IconCustomizationDemo()
    demo.run()
