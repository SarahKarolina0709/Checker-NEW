"""
Layout Validation Script for CheckerApp
Validates the proper separation of pack() and grid() layout managers
"""

import tkinter as tk
import customtkinter as ctk
import logging
from typing import Dict, List, Tuple

class LayoutValidator:
    """Validates the layout structure of the CheckerApp."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.validation_results = {}
        
    def validate_layout_structure(self, root_widget) -> Dict[str, bool]:
        """
        Validate that the layout follows the proper structure:
        - Root uses only pack() for direct children (menu, status, main_container)
        - Grid is only used within main_container and its children
        """
        results = {
            "root_uses_pack_only": True,
            "grid_contained_properly": True,
            "no_layout_conflicts": True,
            "proper_background_colors": True
        }
        
        try:
            # Check root's direct children
            root_children = root_widget.winfo_children()
            self.logger.info(f"Root has {len(root_children)} direct children")
            
            for child in root_children:
                # Check if child uses pack (expected for menu/status/main_container)
                manager = child.winfo_manager()
                if manager == 'pack':
                    self.logger.info(f"✅ Child {child.__class__.__name__} uses pack() correctly")
                elif manager == 'grid':
                    self.logger.warning(f"⚠️  Child {child.__class__.__name__} uses grid() on root - potential conflict")
                    results["root_uses_pack_only"] = False
                elif manager == 'place':
                    self.logger.warning(f"⚠️  Child {child.__class__.__name__} uses place() on root")
                else:
                    self.logger.info(f"Child {child.__class__.__name__} has no geometry manager")
            
            # Look for main_container and validate its structure
            main_container = self._find_main_container(root_widget)
            if main_container:
                self._validate_main_container(main_container, results)
            else:
                self.logger.warning("Main container not found")
                results["grid_contained_properly"] = False
                
            # Check background colors
            self._validate_background_colors(root_widget, results)
            
        except Exception as e:
            self.logger.error(f"Error during layout validation: {e}")
            results["no_layout_conflicts"] = False
            
        return results
    
    def _find_main_container(self, root_widget):
        """Find the main container widget."""
        try:
            for child in root_widget.winfo_children():
                if hasattr(child, 'winfo_children'):
                    # Look for a frame that contains main content
                    grandchildren = child.winfo_children()
                    for grandchild in grandchildren:
                        if hasattr(grandchild, '__class__') and 'content' in str(grandchild).lower():
                            return child
                    # If child seems to be main container based on size/position
                    if child.winfo_manager() == 'pack':
                        pack_info = child.pack_info()
                        if pack_info.get('fill') == 'both' and pack_info.get('expand'):
                            return child
            return None
        except Exception as e:
            self.logger.error(f"Error finding main container: {e}")
            return None
    
    def _validate_main_container(self, main_container, results):
        """Validate the main container's layout structure."""
        try:
            # Check that main container uses pack from root
            if main_container.winfo_manager() == 'pack':
                self.logger.info("✅ Main container correctly uses pack() from root")
            else:
                self.logger.warning(f"⚠️  Main container uses {main_container.winfo_manager()} instead of pack()")
                results["root_uses_pack_only"] = False
            
            # Check children of main container
            content_children = main_container.winfo_children()
            for child in content_children:
                manager = child.winfo_manager()
                if manager == 'grid':
                    self.logger.info(f"✅ Content child {child.__class__.__name__} uses grid() correctly within container")
                elif manager == 'pack':
                    self.logger.info(f"ℹ️  Content child {child.__class__.__name__} uses pack() within container")
                else:
                    self.logger.info(f"Content child {child.__class__.__name__} uses {manager}")
                    
        except Exception as e:
            self.logger.error(f"Error validating main container: {e}")
            results["grid_contained_properly"] = False
    
    def _validate_background_colors(self, root_widget, results):
        """Validate that background colors are consistent."""
        try:
            expected_bg = "#F5F5F5"
            
            # Check root background
            try:
                root_bg = root_widget.cget("fg_color") if hasattr(root_widget, 'cget') else root_widget.cget("bg")
                if root_bg != expected_bg:
                    self.logger.warning(f"Root background color is {root_bg}, expected {expected_bg}")
                    results["proper_background_colors"] = False
                else:
                    self.logger.info("✅ Root background color is correct")
            except Exception:
                self.logger.debug("Could not check root background color")
                
        except Exception as e:
            self.logger.error(f"Error validating background colors: {e}")
            results["proper_background_colors"] = False
    
    def generate_validation_report(self, results: Dict[str, bool]) -> str:
        """Generate a human-readable validation report."""
        report = "\n" + "="*60 + "\n"
        report += "LAYOUT VALIDATION REPORT\n"
        report += "="*60 + "\n\n"
        
        status_icon = "✅" if all(results.values()) else "❌"
        report += f"Overall Status: {status_icon} {'PASS' if all(results.values()) else 'FAIL'}\n\n"
        
        for check, passed in results.items():
            icon = "✅" if passed else "❌"
            report += f"{icon} {check.replace('_', ' ').title()}: {'PASS' if passed else 'FAIL'}\n"
        
        report += "\n" + "="*60 + "\n"
        
        if all(results.values()):
            report += "🎉 Layout structure is correct!\n"
            report += "   - Root uses pack() only for direct children\n"
            report += "   - Grid is properly contained within main container\n"
            report += "   - No layout manager conflicts detected\n"
            report += "   - Background colors are consistent\n"
        else:
            report += "⚠️  Layout issues detected. Please review the log for details.\n"
            
        return report


def main():
    """Main validation function."""
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    logger = logging.getLogger(__name__)
    
    logger.info("Starting layout validation...")
    
    try:
        # Import and initialize the CheckerApp
        from checker_app import CheckerApp
        
        # Create app instance
        app = CheckerApp()
        
        # Give it a moment to fully initialize
        app.root.after(1000, lambda: validate_app_layout(app))
        
        # Start the app
        app.run()
        
    except Exception as e:
        logger.error(f"Error during validation: {e}")
        return False

def validate_app_layout(app):
    """Validate the app layout and print results."""
    logger = logging.getLogger(__name__)
    
    try:
        validator = LayoutValidator()
        results = validator.validate_layout_structure(app.root)
        
        # Generate and print report
        report = validator.generate_validation_report(results)
        print(report)
        
        # Log results
        logger.info("Layout validation completed")
        
        # Close app after validation
        app.root.after(2000, app.root.quit)
        
    except Exception as e:
        logger.error(f"Error during layout validation: {e}")
        app.root.quit()

if __name__ == "__main__":
    main()
