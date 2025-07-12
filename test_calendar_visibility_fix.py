#!/usr/bin/env python3
"""
Test für die Kalender-Sichtbarkeits-Reparatur
Verifiziert, dass der Kalender jetzt korrekt angezeigt wird
"""

import os
import sys
import customtkinter as ctk
from datetime import datetime, timedelta
import traceback
from tkinter import messagebox

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock the required modules
class MockUITheme:
    COLOR_PRIMARY = "#3B82F6"
    COLOR_SECONDARY = "#6B7280"
    COLOR_SUCCESS = "#10B981"
    COLOR_SUCCESS_HOVER = "#059669"
    COLOR_SURFACE = "#F8FAFC"
    COLOR_CARD = "#FFFFFF"
    COLOR_TEXT_PRIMARY = "#1F2937"
    COLOR_TEXT_SECONDARY = "#6B7280"
    COLOR_TEXT_ON_PRIMARY = "#FFFFFF"
    COLOR_PRIMARY_SURFACE = "#DBEAFE"
    COLOR_PRIMARY_HOVER = "#2563EB"
    COLOR_BG_SECONDARY = "#F1F5F9"
    COLOR_CONTAINER_CUSTOMER = "#EBF8FF"
    CONTAINER_STYLE_CUSTOMER = {"fg_color": "#FFFFFF", "corner_radius": 8}
    SPACING_L = 15
    SPACING_M = 10
    SPACING_XL = 20
    SPACING_XXL = 25
    FONT_FAMILY_UI = "Segoe UI"
    BUTTON_STYLE_PRIMARY = {"fg_color": "#3B82F6", "hover_color": "#2563EB"}
    BUTTON_STYLE_SECONDARY = {"fg_color": "#6B7280", "hover_color": "#4B5563"}
    INPUT_STYLE_MODERN = {"border_color": "#D1D5DB", "fg_color": "#FFFFFF"}
    CORNER_RADIUS = 8

class MockSectionHeaderMixin:
    def create_section_header(self, *args, **kwargs):
        header_frame = ctk.CTkFrame(kwargs.get('container', None))
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        return header_frame, None

class MockAnimationEngine:
    def fade_in(self, widget, duration=0.3):
        pass

class MockApp:
    def __init__(self):
        self.logger = MockLogger()
        self.kunden_manager = None
    
    def get_icon(self, icon_name, size=(30, 30)):
        return None

class MockLogger:
    def info(self, message):
        print(f"[INFO] {message}")
    
    def error(self, message):
        print(f"[ERROR] {message}")
        
    def warning(self, message):
        print(f"[WARNING] {message}")
    
    def debug(self, message):
        print(f"[DEBUG] {message}")

class MockWelcomeScreen:
    pass

# Mock the modules
sys.modules['ui_theme'] = type('MockModule', (), {'UITheme': MockUITheme})()
sys.modules['animation_engine'] = type('MockModule', (), {'animation_engine': MockAnimationEngine()})()

def test_calendar_visibility_fix():
    """Test die Kalender-Sichtbarkeits-Reparatur"""
    
    def toggle_and_check():
        """Toggle Kalender und überprüfe Sichtbarkeit"""
        try:
            print("\n" + "="*50)
            print("🔄 TOGGLING CALENDAR...")
            
            # Toggle calendar
            customer_section.toggle_calendar()
            
            # Force update
            app.update_idletasks()
            
            # Check visibility
            calendar_visible = customer_section.calendar_visible
            print(f"✅ Calendar visible state: {calendar_visible}")
            
            if hasattr(customer_section, 'calendar_content'):
                try:
                    height = customer_section.calendar_content.winfo_height()
                    width = customer_section.calendar_content.winfo_width()
                    mapped = customer_section.calendar_content.winfo_ismapped()
                    viewable = customer_section.calendar_content.winfo_viewable()
                    
                    print(f"📏 Calendar dimensions: {width}x{height}")
                    print(f"🗺️  Calendar mapped: {mapped}")
                    print(f"👁️  Calendar viewable: {viewable}")
                    
                    if height > 0 and width > 0 and mapped and calendar_visible:
                        print("🎉 SUCCESS: Calendar is properly visible!")
                        messagebox.showinfo("Test Erfolgreich", 
                                          f"Kalender ist jetzt sichtbar!\n"
                                          f"Größe: {width}x{height}\n"
                                          f"Status: Sichtbar und funktional")
                    else:
                        print("⚠️  ISSUE: Calendar has problems with visibility")
                        
                except Exception as e:
                    print(f"❌ Error checking calendar properties: {e}")
            
            # Test day click
            if customer_section.calendar_visible:
                print("\n🖱️  Testing day click functionality...")
                try:
                    customer_section.on_day_click(datetime.now().day)
                    print("✅ Day click test successful!")
                except Exception as e:
                    print(f"❌ Day click test failed: {e}")
            
        except Exception as e:
            print(f"❌ Error in toggle test: {e}")
            traceback.print_exc()
    
    def test_grid_configuration():
        """Test die Grid-Konfiguration"""
        print("\n🔍 CHECKING GRID CONFIGURATION...")
        
        try:
            # Check self grid configuration
            self_row_weight = customer_section.grid_rowconfigure(0)['weight']
            print(f"✅ Self row weight: {self_row_weight}")
            
            # Check main_content grid configuration
            if hasattr(customer_section, 'main_content'):
                main_row_weight = customer_section.main_content.grid_rowconfigure(1)['weight']
                print(f"✅ Main content row 1 weight: {main_row_weight}")
            
            # Check parent container weights
            parent_widgets = []
            widget = customer_section
            for i in range(3):  # Check 3 levels up
                try:
                    parent = widget.master
                    if parent:
                        parent_widgets.append(parent.__class__.__name__)
                        widget = parent
                    else:
                        break
                except:
                    break
            
            print(f"📋 Widget hierarchy: {' -> '.join(parent_widgets)}")
            
        except Exception as e:
            print(f"❌ Error checking grid configuration: {e}")
    
    print("🧪 Calendar Visibility Fix Test")
    print("=" * 50)
    
    # Create test app
    app = ctk.CTk()
    app.title("Calendar Visibility Fix Test")
    app.geometry("900x700")
    
    # Create mock objects
    mock_app = MockApp()
    mock_welcome_screen = MockWelcomeScreen()
    
    # Import the actual class
    from welcome_screen_components.customer_section_with_calendar import CustomerSectionWithCalendar
    
    # Create the customer section
    customer_section = CustomerSectionWithCalendar(
        master=app,
        app=mock_app,
        welcome_screen=mock_welcome_screen
    )
    customer_section.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Initial grid configuration test
    test_grid_configuration()
    
    # Control panel
    control_frame = ctk.CTkFrame(app)
    control_frame.pack(side="bottom", fill="x", padx=20, pady=10)
    
    # Test buttons
    toggle_btn = ctk.CTkButton(
        control_frame,
        text="🔄 Toggle Calendar & Check",
        command=toggle_and_check,
        height=40,
        width=200
    )
    toggle_btn.pack(side="left", padx=10, pady=10)
    
    grid_btn = ctk.CTkButton(
        control_frame,
        text="🔍 Check Grid Config",
        command=test_grid_configuration,
        height=40,
        width=200
    )
    grid_btn.pack(side="left", padx=10, pady=10)
    
    # Info label
    info_label = ctk.CTkLabel(
        control_frame,
        text="Klicken Sie 'Toggle Calendar' um den Kalender ein/auszublenden und die Reparatur zu testen.",
        font=ctk.CTkFont(size=11)
    )
    info_label.pack(side="right", padx=10, pady=10)
    
    print("\n📋 Test Instructions:")
    print("1. Klicken Sie 'Toggle Calendar & Check' um den Kalender anzuzeigen")
    print("2. Der Kalender sollte jetzt sichtbar sein mit korrekter Größe")
    print("3. Sie können auf Kalendertage klicken um Upload-Details zu sehen")
    print("4. Verwenden Sie 'Check Grid Config' um die Konfiguration zu überprüfen")
    
    # Start the app
    app.mainloop()

if __name__ == "__main__":
    test_calendar_visibility_fix()
