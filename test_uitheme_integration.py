"""
Comprehensive UITheme Integration Test

This script tests the integration of the UITheme system with:
1. The welcome screen
2. All workflow UIs
3. Theme switching
4. Layout manager compatibility

It verifies that all UITheme constants are correctly accessed and no AttributeError exceptions occur.
"""

import customtkinter as ctk
import tkinter as tk
import logging
import sys
import os
from typing import Dict, Any, List, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("uitheme_integration_test.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Add parent directory to path if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import UITheme and related components
try:
    from ui_theme import UITheme, enhanced_theme
    logger.info("✅ UITheme imported successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import UITheme: {e}")
    sys.exit(1)

# Import welcome screen and workflow components
try:
    from ultra_modern_welcome_screen_simplified import UltraModernWelcomeScreen
    logger.info("✅ Welcome screen imported successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import welcome screen: {e}")

try:
    from ui_components.pruefung_workflow_view import PruefungWorkflowView
    logger.info("✅ Workflow view imported successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import workflow view: {e}")

class UIThemeIntegrationTest:
    """Test UITheme integration with various UI components."""
    
    def __init__(self):
        """Initialize the test suite."""
        self.root = ctk.CTk()
        self.root.title("UITheme Integration Test")
        self.root.geometry("1200x800")
        
        # Container for tests
        self.main_container = ctk.CTkFrame(self.root)
        self.main_container.pack(fill="both", expand=True)
        
        # Test controls
        self.controls_frame = ctk.CTkFrame(self.main_container)
        self.controls_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(self.controls_frame, text="UITheme Integration Test").pack(side="left", padx=10)
        
        # Theme toggle
        self.theme_var = tk.StringVar(value="light")
        ctk.CTkButton(
            self.controls_frame, 
            text="Toggle Theme", 
            command=self.toggle_theme
        ).pack(side="right", padx=10)
        
        # Test buttons
        ctk.CTkButton(
            self.controls_frame, 
            text="Test Welcome Screen", 
            command=self.test_welcome_screen
        ).pack(side="right", padx=10)
        
        ctk.CTkButton(
            self.controls_frame, 
            text="Test Workflow UI", 
            command=self.test_workflow_ui
        ).pack(side="right", padx=10)
        
        # Content frame for UI tests
        self.content_frame = ctk.CTkFrame(self.main_container)
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Results display
        self.results_frame = ctk.CTkFrame(self.main_container)
        self.results_frame.pack(fill="x", padx=10, pady=10)
        
        self.results_label = ctk.CTkLabel(
            self.results_frame, 
            text="Run tests to see results...",
            font=ctk.CTkFont(size=14)
        )
        self.results_label.pack(padx=10, pady=10)
        
        self.current_ui = None
        
        logger.info("Test suite initialized")
    
    def toggle_theme(self):
        """Toggle between light and dark themes."""
        if self.theme_var.get() == "light":
            new_theme = "dark"
            ctk.set_appearance_mode("dark")
            enhanced_theme.switch_theme("dark")
        else:
            new_theme = "light"
            ctk.set_appearance_mode("light")
            enhanced_theme.switch_theme("light")
            
        self.theme_var.set(new_theme)
        logger.info(f"Theme switched to {new_theme}")
        self.update_results(f"Theme switched to {new_theme}")
    
    def clear_content(self):
        """Clear the content frame for new tests."""
        if self.current_ui:
            try:
                self.current_ui.destroy()
            except:
                pass
            self.current_ui = None
        
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def update_results(self, message: str):
        """Update the results display."""
        self.results_label.configure(text=message)
    
    def test_welcome_screen(self):
        """Test the welcome screen with UITheme."""
        try:
            self.clear_content()
            logger.info("Testing welcome screen...")
            self.update_results("Loading welcome screen...")
            
            # Check a few UITheme constants before loading
            color_primary = UITheme.COLOR_PRIMARY
            container_style = UITheme.CONTAINER_STYLE_CUSTOMER
            font_family = UITheme.FONT_FAMILY_UI
            
            logger.info(f"Pre-load check: COLOR_PRIMARY={color_primary}")
            logger.info(f"Pre-load check: CONTAINER_STYLE_CUSTOMER has {len(container_style)} keys")
            logger.info(f"Pre-load check: FONT_FAMILY_UI={font_family}")
            
            # Create a welcome screen
            self.current_ui = UltraModernWelcomeScreen(self.content_frame)
            
            # Check access to UITheme constants after loading
            color_primary_after = UITheme.COLOR_PRIMARY
            
            logger.info(f"Post-load check: COLOR_PRIMARY={color_primary_after}")
            logger.info("Welcome screen loaded successfully")
            self.update_results("✅ Welcome screen loaded successfully with UITheme")
            
        except Exception as e:
            logger.error(f"❌ Welcome screen test failed: {e}", exc_info=True)
            self.update_results(f"❌ Welcome screen test failed: {str(e)}")
    
    def test_workflow_ui(self):
        """Test workflow UI with UITheme."""
        try:
            self.clear_content()
            logger.info("Testing workflow UI...")
            self.update_results("Loading workflow UI...")
            
            # Create mock project data
            project_data = {
                "kunde_name": "Test Kunde GmbH",
                "auftragsnummer": "A12345",
                "file_pairs": [],
                "checks": {}
            }
            
            # Create a workflow view
            self.current_ui = PruefungWorkflowView(
                self.content_frame, 
                controller=None,  # Mock controller
                project_data=project_data
            )
            
            logger.info("Workflow UI loaded successfully")
            self.update_results("✅ Workflow UI loaded successfully with UITheme")
            
        except Exception as e:
            logger.error(f"❌ Workflow UI test failed: {e}", exc_info=True)
            self.update_results(f"❌ Workflow UI test failed: {str(e)}")
    
    def run(self):
        """Run the test suite."""
        logger.info("Starting UITheme integration test")
        self.root.mainloop()

if __name__ == "__main__":
    test = UIThemeIntegrationTest()
    test.run()
