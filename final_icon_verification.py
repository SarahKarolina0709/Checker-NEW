#!/usr/bin/env python3
"""
Finale Verifikation der Icon-Replacement-Erfolg
Überprüft, ob businesswoman und client Icons korrekt angezeigt werden
"""

import customtkinter as ctk
import tkinter as tk
from PIL import Image
import os
import sys

# Pfad für Imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fluent_icons_manager import EnhancedFluentIconManager
from ultra_modern_welcome_screen_simplified import UltraModernWelcomeScreen

def test_final_icons():
    """Finale Test der Customer-Icons in einer realistischen UI"""
    
    # Mock App-Klasse für Welcome Screen
    class MockApp:
        def __init__(self):
            # Icon Manager initialisieren
            workspace_path = os.path.dirname(os.path.abspath(__file__))
            self.icon_manager = EnhancedFluentIconManager(workspace_path)
        
        def get_icon(self, icon_name, size=(20, 20)):
            """Mock der get_icon-Methode"""
            return self.icon_manager.get_icon(icon_name, size)
        
        def start_workflow(self, workflow_name):
            """Mock der start_workflow-Methode"""
            print(f"🚀 Workflow gestartet: {workflow_name}")
    
    # UI erstellen
    root = ctk.CTk()
    root.title("Final Icon Test - Customer Icons")
    root.geometry("1200x800")
    
    mock_app = MockApp()
    
    print("🔧 Final Icon Verification Test")
    print("=" * 50)
    
    # Test Frame
    test_frame = ctk.CTkFrame(root)
    test_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Test 1: Direct Icon Loading
    print("\n📋 Test 1: Direct Icon Loading")
    test_icons = ["businesswoman", "client"]
    test_sizes = [(24, 24), (32, 32), (34, 34)]
    
    for i, icon_name in enumerate(test_icons):
        for j, size in enumerate(test_sizes):
            row = i * len(test_sizes) + j
            
            icon_container = ctk.CTkFrame(test_frame)
            icon_container.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
            
            # Label für Icon-Info
            info_label = ctk.CTkLabel(icon_container, text=f"{icon_name} {size}")
            info_label.pack(side="left", padx=10)
            
            try:
                icon = mock_app.get_icon(icon_name, size)
                if icon:
                    print(f"✅ {icon_name} {size}: {type(icon).__name__}")
                    
                    icon_label = ctk.CTkLabel(icon_container, image=icon, text="")
                    icon_label.pack(side="left", padx=10)
                    
                    status_label = ctk.CTkLabel(icon_container, text="✅ Erfolgreich",
                                              text_color="green", font=ctk.CTkFont(size=10))
                    status_label.pack(side="left", padx=10)
                else:
                    print(f"❌ {icon_name} {size}: Failed to load")
                    error_label = ctk.CTkLabel(icon_container, text="❌ Fehler",
                                             text_color="red", font=ctk.CTkFont(size=10))
                    error_label.pack(side="left", padx=10)
            except Exception as e:
                print(f"💥 {icon_name} {size}: {e}")
                error_label = ctk.CTkLabel(icon_container, text=f"💥 {e}",
                                         text_color="red", font=ctk.CTkFont(size=10))
                error_label.pack(side="left", padx=10)
    
    # Test 2: Workflow Cards (simuliert)
    print("\n📋 Test 2: Workflow Card Icons")
    
    workflow_container = ctk.CTkFrame(test_frame)
    workflow_container.grid(row=10, column=0, columnspan=2, padx=10, pady=20, sticky="ew")
    
    workflow_title = ctk.CTkLabel(workflow_container, text="Workflow Card Icons Test",
                                 font=ctk.CTkFont(size=16, weight="bold"))
    workflow_title.pack(pady=10)
    
    workflows = [
        {"name": "Angebots-Analyzer Pro", "icon": "businesswoman", "size": (34, 34)},
        {"name": "Multi-File Checker", "icon": "client", "size": (34, 34)},
        {"name": "Smart Finalization", "icon": "businesswoman", "size": (34, 34)}
    ]
    
    for workflow in workflows:
        workflow_frame = ctk.CTkFrame(workflow_container)
        workflow_frame.pack(fill="x", padx=10, pady=5)
        
        try:
            workflow_icon = mock_app.get_icon(workflow["icon"], workflow["size"])
            if workflow_icon:
                icon_label = ctk.CTkLabel(workflow_frame, image=workflow_icon, text="")
                icon_label.pack(side="left", padx=10, pady=5)
                
                text_label = ctk.CTkLabel(workflow_frame, text=f'{workflow["name"]} (Icon: {workflow["icon"]})')
                text_label.pack(side="left", padx=10, pady=5)
                
                status_label = ctk.CTkLabel(workflow_frame, text="✅", text_color="green")
                status_label.pack(side="right", padx=10, pady=5)
                
                print(f"✅ Workflow '{workflow['name']}' Icon '{workflow['icon']}' erfolgreich")
            else:
                text_label = ctk.CTkLabel(workflow_frame, text=f'{workflow["name"]} (Icon: {workflow["icon"]})')
                text_label.pack(side="left", padx=10, pady=5)
                
                status_label = ctk.CTkLabel(workflow_frame, text="❌", text_color="red")
                status_label.pack(side="right", padx=10, pady=5)
                
                print(f"❌ Workflow '{workflow['name']}' Icon '{workflow['icon']}' fehlgeschlagen")
        except Exception as e:
            text_label = ctk.CTkLabel(workflow_frame, text=f'{workflow["name"]} (Error: {e})')
            text_label.pack(side="left", padx=10, pady=5)
            
            status_label = ctk.CTkLabel(workflow_frame, text="💥", text_color="red")
            status_label.pack(side="right", padx=10, pady=5)
            
            print(f"💥 Workflow '{workflow['name']}' Fehler: {e}")
    
    # Grid-Konfiguration
    test_frame.grid_columnconfigure(0, weight=1)
    test_frame.grid_columnconfigure(1, weight=1)
    
    print("\n" + "=" * 50)
    print("🎉 Final Icon Test UI gestartet")
    print("Überprüfen Sie visuell, ob die Customer-Icons korrekt angezeigt werden!")
    
    root.mainloop()

if __name__ == "__main__":
    test_final_icons()
