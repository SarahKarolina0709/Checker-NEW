#!/usr/bin/env python3
"""
Test für das korrigierte vertikale Scroll-Layout
"""
import customtkinter as ctk
from ui_theme import UITheme

class VerticalScrollTest:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Vertikales Scroll Layout Test")
        self.root.geometry("1400x900")
        
        # Light mode
        ctk.set_appearance_mode("Light")
        
        self.create_test_layout()
        
    def create_test_layout(self):
        """Teste das vertikale Scroll-Layout"""
        
        # Main container
        main_container = ctk.CTkFrame(self.root, fg_color="#FAFBFC")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header = ctk.CTkLabel(
            main_container,
            text="Vertikales Scroll Layout Test - Drei Container nebeneinander",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        header.pack(pady=(20, 20))
        
        # Content frame für drei Spalten
        content_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Grid-Konfiguration für drei gleichmäßige Spalten
        content_frame.grid_columnconfigure(0, weight=1, minsize=400)  
        content_frame.grid_columnconfigure(1, weight=1, minsize=400)  
        content_frame.grid_columnconfigure(2, weight=1, minsize=400)  
        content_frame.grid_rowconfigure(0, weight=1)
        
        # Test Container 1 - Customer (ohne Scrolling)
        customer_container = ctk.CTkFrame(
            content_frame,
            **UITheme.CONTAINER_STYLE_CUSTOMER
        )
        customer_container.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        customer_container.grid_propagate(False)
        
        ctk.CTkLabel(
            customer_container,
            text="Customer Container\nHöhe: 600px\nOhne Scrolling (noch)",
            font=ctk.CTkFont(size=14, weight="bold"),
            justify="center"
        ).pack(pady=20)
        
        # Füge viel Testinhalt hinzu
        for i in range(20):
            ctk.CTkLabel(
                customer_container,
                text=f"Customer Item {i+1}",
                font=ctk.CTkFont(size=11)
            ).pack(pady=1)
        
        # Test Container 2 - Upload (mit Scrolling)
        upload_container = ctk.CTkFrame(
            content_frame,
            **UITheme.CONTAINER_STYLE_UPLOAD
        )
        upload_container.grid(row=0, column=1, sticky="nsew", padx=(5, 5))
        upload_container.grid_propagate(False)
        upload_container.grid_rowconfigure(1, weight=1)
        upload_container.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            upload_container,
            text="Upload Container\nHöhe: 600px\nMit vertikalem Scrolling",
            font=ctk.CTkFont(size=14, weight="bold"),
            justify="center"
        ).pack(pady=10)
        
        # Scrollbarer Bereich für Upload-Inhalte
        upload_scroll = ctk.CTkScrollableFrame(
            upload_container,
            fg_color="transparent"
        )
        upload_scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        # Füge viel Testinhalt hinzu
        for i in range(25):
            ctk.CTkLabel(
                upload_scroll,
                text=f"Upload Item {i+1} - Dieser kann gescrollt werden",
                font=ctk.CTkFont(size=11)
            ).pack(pady=2, fill="x")
        
        # Test Container 3 - Workflow (mit Scrolling)
        workflow_container = ctk.CTkFrame(
            content_frame,
            **UITheme.CONTAINER_STYLE_WORKFLOW
        )
        workflow_container.grid(row=0, column=2, sticky="nsew", padx=(10, 0))
        workflow_container.grid_propagate(False)
        workflow_container.grid_rowconfigure(1, weight=1)
        workflow_container.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            workflow_container,
            text="Workflow Container\nHöhe: 600px\nMit vertikalem Scrolling",
            font=ctk.CTkFont(size=14, weight="bold"),
            justify="center"
        ).pack(pady=10)
        
        # Scrollbarer Bereich für Workflow-Inhalte
        workflow_scroll = ctk.CTkScrollableFrame(
            workflow_container,
            fg_color="transparent"
        )
        workflow_scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        # Füge viel Testinhalt hinzu
        for i in range(20):
            workflow_button = ctk.CTkButton(
                workflow_scroll,
                text=f"Workflow {i+1}",
                font=ctk.CTkFont(size=11),
                height=30
            )
            workflow_button.pack(pady=2, fill="x", padx=5)
                
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    test = VerticalScrollTest()
    test.run()
