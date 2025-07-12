#!/usr/bin/env python3
"""
Test für das neue horizontale Scroll-Layout
"""
import customtkinter as ctk
from ui_theme import UITheme

class HorizontalScrollTest:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Horizontal Scroll Layout Test")
        self.root.geometry("1600x900")
        
        # Light mode
        ctk.set_appearance_mode("Light")
        
        self.create_test_layout()
        
    def create_test_layout(self):
        """Teste das neue horizontale Scroll-Layout"""
        
        # Main container
        main_container = ctk.CTkFrame(self.root, fg_color="#FAFBFC")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header = ctk.CTkLabel(
            main_container,
            text="Horizontal Scroll Layout Test",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        header.pack(pady=(20, 20))
        
        # Horizontaler Scroll-Bereich mit optimierter Konfiguration
        scroll_wrapper = ctk.CTkFrame(main_container, fg_color="transparent")
        scroll_wrapper.pack(fill="both", expand=True, pady=(0, 20))
        
        scrollable_frame = ctk.CTkScrollableFrame(
            scroll_wrapper,
            orientation="horizontal",
            fg_color="transparent",
            scrollbar_button_color="#C0C0C0",
            scrollbar_button_hover_color="#A0A0A0",
            height=600  # Feste Höhe für den Scroll-Bereich
        )
        scrollable_frame.pack(fill="both", expand=True)
        
        # Container für die drei Abschnitte
        content_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        content_frame.pack(fill="y", padx=10, pady=10)
        
        # Test Container 1 - Customer
        customer_container = ctk.CTkFrame(
            content_frame,
            **UITheme.CONTAINER_STYLE_CUSTOMER
        )
        customer_container.pack(side="left", fill="y", padx=(0, 10))
        
        ctk.CTkLabel(
            customer_container,
            text="Customer Container\nBreite: 400px\nHorizontal scrollbar",
            font=ctk.CTkFont(size=14, weight="bold"),
            justify="center"
        ).pack(pady=20)
        
        # Füge Testinhalt hinzu
        for i in range(15):
            ctk.CTkLabel(
                customer_container,
                text=f"Customer Item {i+1}",
                font=ctk.CTkFont(size=11)
            ).pack(pady=1)
        
        # Test Container 2 - Upload
        upload_container = ctk.CTkFrame(
            content_frame,
            **UITheme.CONTAINER_STYLE_UPLOAD
        )
        upload_container.pack(side="left", fill="y", padx=(5, 5))
        
        ctk.CTkLabel(
            upload_container,
            text="Upload Container\nMit festgelegter Breite\nund scrollbarem Layout",
            font=ctk.CTkFont(size=16, weight="bold"),
            justify="center"
        ).pack(pady=20)
        
        # Füge Testinhalt hinzu
        for i in range(10):
            ctk.CTkLabel(
                upload_container,
                text=f"Upload Item {i+1}",
                font=ctk.CTkFont(size=12)
            ).pack(pady=2)
        
        # Test Container 3 - Workflow
        workflow_container = ctk.CTkFrame(
            content_frame,
            **UITheme.CONTAINER_STYLE_WORKFLOW
        )
        workflow_container.pack(side="left", fill="both", expand=True, padx=(10, 0))
        
        ctk.CTkLabel(
            workflow_container,
            text="Workflow Container\nMit festgelegter Breite\nund scrollbarem Layout",
            font=ctk.CTkFont(size=16, weight="bold"),
            justify="center"
        ).pack(pady=20)
        
        # Füge Testinhalt hinzu
        for i in range(10):
            ctk.CTkLabel(
                workflow_container,
                text=f"Workflow Item {i+1}",
                font=ctk.CTkFont(size=12)
            ).pack(pady=2)
                
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    test = HorizontalScrollTest()
    test.run()
