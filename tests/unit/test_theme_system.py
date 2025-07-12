"""
Unit tests for the theme system.
Tests pure Python logic without GUI dependencies.
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Test imports with fallbacks
try:
    from ui_theme import UITheme, ColorScheme, WorkflowColorScheme
    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False


class TestThemeSystem(unittest.TestCase):
    """Unit tests for theme system logic."""
    
    @unittest.skipUnless(THEME_AVAILABLE, "UI Theme not available")
    def test_color_scheme_creation(self):
        """Test ColorScheme dataclass creation."""
        # Test basic color scheme
        scheme = ColorScheme(
            background="#FFFFFF",
            surface="#F5F5F5",
            card="#FAFAFA",
            border="#E0E0E0",
            primary="#007ACC",
            primary_hover="#005A9E",
            primary_container="#E3F2FD",
            primary_surface="#F3F9FF",
            text_primary="#212121",
            text_secondary="#757575",
            text_on_primary="#FFFFFF",
            text_on_dark="#FFFFFF",
            success="#4CAF50",
            success_hover="#45A049",
            danger="#F44336",
            danger_hover="#D32F2F",
            warning="#FF9800",
            info="#2196F3",
            info_hover="#1976D2",
            secondary="#9C27B0",
            secondary_hover="#7B1FA2",
            accent="#FF5722",
            accent_hover="#E64A19",
            icon="#424242",
            icon_light="#757575",
            icon_accent="#FF5722",
            icon_danger="#F44336",
            icon_success="#4CAF50",
            icon_warning="#FF9800",
            menu_icon="#424242",
            menu_hover="#E0E0E0",
            header_icon="#424242",
            control_hover="#E0E0E0",
            danger_surface="#FFEBEE",
            info_surface="#E3F2FD",
            success_surface="#E8F5E8",
            warning_surface="#FFF3E0"
        )
        
        # Test immutability
        self.assertIsInstance(scheme, ColorScheme)
        with self.assertRaises(AttributeError):
            scheme.background = "#000000"
        
        # Test field access
        self.assertEqual(scheme.background, "#FFFFFF")
        self.assertEqual(scheme.primary, "#007ACC")
        self.assertEqual(scheme.success, "#4CAF50")

    @unittest.skipUnless(THEME_AVAILABLE, "UI Theme not available")
    def test_workflow_color_scheme(self):
        """Test WorkflowColorScheme dataclass."""
        workflow_scheme = WorkflowColorScheme(
            primary="#007ACC",
            hover="#005A9E",
            light="#E3F2FD",
            icon_bg="#F3F9FF",
            shadow="#00000020",
            glow="#007ACC40"
        )
        
        self.assertIsInstance(workflow_scheme, WorkflowColorScheme)
        self.assertEqual(workflow_scheme.primary, "#007ACC")
        self.assertEqual(workflow_scheme.hover, "#005A9E")
        self.assertEqual(workflow_scheme.shadow, "#00000020")
        self.assertEqual(workflow_scheme.glow, "#007ACC40")

    @unittest.skipUnless(THEME_AVAILABLE, "UI Theme not available")
    def test_ui_theme_color_retrieval(self):
        """Test UITheme color retrieval methods."""
        theme = UITheme()
        
        # Test basic color retrieval
        color = theme.get_color('primary')
        self.assertIsInstance(color, str)
        self.assertTrue(color.startswith('#'))
        
        # Test color tuple retrieval
        color_tuple = theme.get_theme_tuple('primary')
        self.assertIsInstance(color_tuple, tuple)
        self.assertEqual(len(color_tuple), 2)
        
        # Test invalid color name handling
        try:
            invalid_color = theme.get_color('invalid_color')
            # If no exception, check it returns a default or None
            self.assertTrue(invalid_color is None or isinstance(invalid_color, str))
        except (KeyError, AttributeError):
            # Either exception is acceptable for invalid color names
            pass

    @unittest.skipUnless(THEME_AVAILABLE, "UI Theme not available")
    def test_workflow_color_schemes(self):
        """Test workflow-specific color schemes."""
        theme = UITheme()
        
        # Test workflow color retrieval
        workflow_colors = theme.get_workflow_colors('angebots_workflow')
        self.assertIsInstance(workflow_colors, dict)
        self.assertIn('primary', workflow_colors)
        self.assertIn('hover', workflow_colors)
        
        # Test different workflows
        workflows = ['angebots_workflow', 'pruefung_workflow', 'finalisierung_workflow']
        for workflow in workflows:
            colors = theme.get_workflow_colors(workflow)
            self.assertIsInstance(colors, dict)
            self.assertTrue(len(colors) > 0)

    @unittest.skipUnless(THEME_AVAILABLE, "UI Theme not available")
    def test_theme_mode_switching(self):
        """Test light/dark mode switching."""
        theme = UITheme()
        
        # Test light mode
        light_color = theme.get_color('background', mode='light')
        self.assertIsInstance(light_color, str)
        
        # Test dark mode
        dark_color = theme.get_color('background', mode='dark')
        self.assertIsInstance(dark_color, str)
        
        # Colors should be different
        self.assertNotEqual(light_color, dark_color)

    @unittest.skipUnless(THEME_AVAILABLE, "UI Theme not available")
    def test_theme_consistency(self):
        """Test theme consistency and color validation."""
        theme = UITheme()
        
        # Test all required colors are present
        required_colors = [
            'background', 'surface', 'card', 'border',
            'primary', 'primary_hover', 'text_primary',
            'success', 'danger', 'warning', 'info'
        ]
        
        for color_name in required_colors:
            color = theme.get_color(color_name)
            self.assertIsInstance(color, str)
            self.assertTrue(color.startswith('#'))
            self.assertEqual(len(color), 7)  # #RRGGBB format

    def test_color_validation(self):
        """Test color format validation."""
        # Test valid hex colors
        valid_colors = ["#000000", "#FFFFFF", "#FF0000", "#00FF00", "#0000FF"]
        for color in valid_colors:
            self.assertTrue(self._is_valid_hex_color(color))
        
        # Test invalid hex colors
        invalid_colors = ["000000", "#GG0000", "#FF", "#FFFFFFF", "red"]
        for color in invalid_colors:
            self.assertFalse(self._is_valid_hex_color(color))

    def _is_valid_hex_color(self, color: str) -> bool:
        """Helper method to validate hex color format."""
        if not isinstance(color, str):
            return False
        if not color.startswith('#'):
            return False
        if len(color) != 7:
            return False
        try:
            int(color[1:], 16)
            return True
        except ValueError:
            return False


if __name__ == '__main__':
    unittest.main()
