"""
GUI smoke tests for CheckerApp.
Tests that GUI components instantiate without errors.
"""

import sys
import unittest
import threading
import time
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock
import tkinter as tk

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import required modules
import customtkinter as ctk

# Test imports with fallbacks
try:
    from view_stack import ViewStack, EnhancedViewStack
    VIEWSTACK_AVAILABLE = True
except ImportError:
    VIEWSTACK_AVAILABLE = False

try:
    from ui_theme import UITheme, ColorScheme
    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False

try:
    from base_ui_components import BaseUIComponents
    UI_COMPONENTS_AVAILABLE = True
except ImportError:
    UI_COMPONENTS_AVAILABLE = False


class TestGUISmoke(unittest.TestCase):
    """Smoke tests for GUI components."""
    
    @classmethod
    def setUpClass(cls):
        """Set up GUI testing environment."""
        # Configure CustomTkinter for testing
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Create root window for testing
        cls.root = ctk.CTk()
        cls.root.withdraw()  # Hide window during tests
        cls.root.title("Test Root")
        cls.root.geometry("800x600")
        
        # Disable DPI scaling for consistent testing
        cls.root.tk.call('tk', 'scaling', 1.0)
        
        # Store original methods for restoration
        cls.original_after = cls.root.after
        cls.original_after_idle = cls.root.after_idle
    
    @classmethod
    def tearDownClass(cls):
        """Clean up GUI testing environment."""
        try:
            cls.root.destroy()
        except:
            pass
    
    def setUp(self):
        """Set up each test."""
        self.test_container = ctk.CTkFrame(self.root)
        self.test_container.pack(fill='both', expand=True)
        
        # Mock potentially problematic methods
        self.root.after = MagicMock()
        self.root.after_idle = MagicMock()
    
    def tearDown(self):
        """Clean up after each test."""
        try:
            # Restore original methods
            self.root.after = self.original_after
            self.root.after_idle = self.original_after_idle
            
            self.test_container.destroy()
        except:
            pass
    
    def test_basic_widgets_creation(self):
        """Test basic CustomTkinter widgets can be created."""
        # Test Frame
        frame = ctk.CTkFrame(self.test_container)
        self.assertIsInstance(frame, ctk.CTkFrame)
        
        # Test Label
        label = ctk.CTkLabel(frame, text="Test Label")
        self.assertIsInstance(label, ctk.CTkLabel)
        
        # Test Button
        button = ctk.CTkButton(frame, text="Test Button")
        self.assertIsInstance(button, ctk.CTkButton)
        
        # Test Entry
        entry = ctk.CTkEntry(frame, placeholder_text="Test Entry")
        self.assertIsInstance(entry, ctk.CTkEntry)
        
        # Test pack layout
        frame.pack(fill='both', expand=True)
        label.pack(pady=5)
        button.pack(pady=5)
        entry.pack(pady=5)
        
        # Update to process layout
        self.root.update_idletasks()
        
        # Verify widgets exist
        self.assertEqual(len(frame.winfo_children()), 3)
    
    def test_scrollable_frame_creation(self):
        """Test ScrollableFrame creation."""
        scrollable = ctk.CTkScrollableFrame(self.test_container)
        self.assertIsInstance(scrollable, ctk.CTkScrollableFrame)
        
        # Add content to scrollable frame
        for i in range(10):
            label = ctk.CTkLabel(scrollable, text=f"Item {i}")
            label.pack(pady=2)
        
        scrollable.pack(fill='both', expand=True)
        self.root.update_idletasks()
        
        # Verify scrollable frame has content
        self.assertEqual(len(scrollable.winfo_children()), 10)
    
    def test_tabview_creation(self):
        """Test TabView creation."""
        tabview = ctk.CTkTabview(self.test_container)
        self.assertIsInstance(tabview, ctk.CTkTabview)
        
        # Add tabs
        tab1 = tabview.add("Tab 1")
        tab2 = tabview.add("Tab 2")
        
        # Add content to tabs
        label1 = ctk.CTkLabel(tab1, text="Content 1")
        label1.pack()
        
        label2 = ctk.CTkLabel(tab2, text="Content 2")
        label2.pack()
        
        tabview.pack(fill='both', expand=True)
        self.root.update_idletasks()
        
        # Verify tabs exist
        self.assertEqual(len(tabview._tab_dict), 2)
    
    def test_complex_layout_creation(self):
        """Test complex layout with multiple containers."""
        # Create main container
        main_frame = ctk.CTkFrame(self.test_container)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create header
        header_frame = ctk.CTkFrame(main_frame)
        header_frame.pack(fill='x', pady=(0, 10))
        
        title_label = ctk.CTkLabel(header_frame, text="Test Application", 
                                 font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=10)
        
        # Create content area with grid
        content_frame = ctk.CTkFrame(main_frame)
        content_frame.pack(fill='both', expand=True)
        
        # Configure grid
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        
        # Left panel
        left_panel = ctk.CTkFrame(content_frame)
        left_panel.grid(row=0, column=0, sticky='nsew', padx=(0, 5))
        
        # Right panel
        right_panel = ctk.CTkFrame(content_frame)
        right_panel.grid(row=0, column=1, sticky='nsew', padx=(5, 0))
        
        # Add content to panels
        for i in range(3):
            ctk.CTkButton(left_panel, text=f"Button {i}").pack(pady=5)
            ctk.CTkEntry(right_panel, placeholder_text=f"Entry {i}").pack(pady=5)
        
        self.root.update_idletasks()
        
        # Verify layout structure
        self.assertEqual(len(main_frame.winfo_children()), 2)  # header + content
        self.assertEqual(len(content_frame.winfo_children()), 2)  # left + right
        self.assertEqual(len(left_panel.winfo_children()), 3)  # 3 buttons
        self.assertEqual(len(right_panel.winfo_children()), 3)  # 3 entries
    
    def test_widget_configuration(self):
        """Test widget configuration options."""
        # Test Frame configuration
        frame = ctk.CTkFrame(self.test_container, 
                           corner_radius=10, 
                           border_width=2)
        frame.pack(fill='both', expand=True)
        
        # Test Label configuration
        label = ctk.CTkLabel(frame,
                           text="Configured Label",
                           font=ctk.CTkFont(size=16, weight="bold"),
                           text_color="blue")
        label.pack(pady=10)
        
        # Test Button configuration
        button = ctk.CTkButton(frame,
                             text="Configured Button",
                             width=200,
                             height=40,
                             corner_radius=20,
                             command=lambda: None)
        button.pack(pady=10)
        
        self.root.update_idletasks()
        
        # Verify widgets are configured
        self.assertIsNotNone(frame.cget('corner_radius'))
        self.assertIsNotNone(label.cget('text'))
        self.assertIsNotNone(button.cget('width'))
    
    def test_event_binding(self):
        """Test event binding on widgets."""
        button_clicked = False
        entry_text = ""
        
        def on_button_click():
            nonlocal button_clicked
            button_clicked = True
        
        def on_entry_change(event=None):
            nonlocal entry_text
            entry_text = entry.get()
        
        button = ctk.CTkButton(self.test_container, 
                             text="Click Me", 
                             command=on_button_click)
        button.pack(pady=10)
        
        entry = ctk.CTkEntry(self.test_container, 
                           placeholder_text="Type here")
        entry.pack(pady=10)
        entry.bind('<KeyRelease>', on_entry_change)
        
        self.root.update_idletasks()
        
        # Simulate button click
        button.invoke()
        self.assertTrue(button_clicked)
        
        # Simulate entry input
        entry.insert(0, "test")
        entry.event_generate('<KeyRelease>')
        self.root.update_idletasks()
        self.assertEqual(entry_text, "test")
    
    def test_widget_state_management(self):
        """Test widget state management."""
        button = ctk.CTkButton(self.test_container, text="State Test")
        button.pack(pady=10)
        
        entry = ctk.CTkEntry(self.test_container, placeholder_text="State Test")
        entry.pack(pady=10)
        
        # Test initial state
        self.assertEqual(button.cget('state'), 'normal')
        
        # Test disabled state
        button.configure(state='disabled')
        self.assertEqual(button.cget('state'), 'disabled')
        
        # Test re-enabled state
        button.configure(state='normal')
        self.assertEqual(button.cget('state'), 'normal')
        
        # Test entry state
        entry.configure(state='readonly')
        self.assertEqual(entry.cget('state'), 'readonly')
    
    @unittest.skipUnless(VIEWSTACK_AVAILABLE, "ViewStack not available")
    def test_viewstack_instantiation(self):
        """Test ViewStack can be instantiated without errors."""
        # Test basic ViewStack
        viewstack = ViewStack(self.test_container)
        self.assertIsInstance(viewstack, ViewStack)
        
        # Test adding views
        test_frame1 = ctk.CTkFrame(viewstack)
        test_frame2 = ctk.CTkFrame(viewstack)
        
        viewstack.add('view1', test_frame1)
        viewstack.add('view2', test_frame2)
        
        # Test switching views
        result = viewstack.show('view1')
        self.assertTrue(result)
        
        result = viewstack.show('view2')
        self.assertTrue(result)
        
        # Test EnhancedViewStack
        enhanced_viewstack = EnhancedViewStack(self.test_container)
        self.assertIsInstance(enhanced_viewstack, EnhancedViewStack)
        
        # Test with callbacks
        callback_called = []
        def on_show_callback(prev_view):
            callback_called.append(f"show_{prev_view}")
        
        def on_hide_callback():
            callback_called.append("hide")
        
        enhanced_viewstack.add('test_view', test_frame1, 
                              on_show=on_show_callback, 
                              on_hide=on_hide_callback)
        
        enhanced_viewstack.show('test_view')
        self.assertIn('show_None', callback_called)

    @unittest.skipUnless(THEME_AVAILABLE, "UI Theme not available")
    def test_ui_theme_instantiation(self):
        """Test UITheme can be instantiated and used."""
        # Test UITheme creation
        theme = UITheme()
        self.assertIsInstance(theme, UITheme)
        
        # Test color retrieval
        try:
            primary_color = theme.get_color('primary')
            self.assertIsInstance(primary_color, str)
            self.assertTrue(primary_color.startswith('#'))
        except Exception as e:
            self.fail(f"UITheme color retrieval failed: {e}")
        
        # Test color tuple retrieval
        try:
            color_tuple = theme.get_color_tuple('primary')
            self.assertIsInstance(color_tuple, tuple)
            self.assertEqual(len(color_tuple), 2)
        except Exception as e:
            self.fail(f"UITheme color tuple retrieval failed: {e}")

    @unittest.skipUnless(UI_COMPONENTS_AVAILABLE, "Base UI Components not available")
    def test_base_ui_components(self):
        """Test BaseUIComponents can be instantiated."""
        try:
            # Mock theme if needed
            mock_theme = MagicMock()
            mock_theme.get_color.return_value = "#000000"
            mock_theme.get_color_tuple.return_value = ("#000000", "#FFFFFF")
            
            with patch('base_ui_components.UITheme', return_value=mock_theme):
                components = BaseUIComponents()
                self.assertIsInstance(components, BaseUIComponents)
        except Exception as e:
            self.fail(f"BaseUIComponents instantiation failed: {e}")

    def test_complex_layout_scenarios(self):
        """Test complex layout scenarios that might cause issues."""
        # Test deeply nested layout
        level1 = ctk.CTkFrame(self.test_container)
        level1.pack(fill='both', expand=True)
        
        level2 = ctk.CTkFrame(level1)
        level2.pack(fill='both', expand=True, padx=5, pady=5)
        
        level3 = ctk.CTkFrame(level2)
        level3.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Add widgets to deepest level
        for i in range(5):
            widget = ctk.CTkLabel(level3, text=f"Deep Widget {i}")
            widget.pack(pady=2)
        
        self.root.update_idletasks()
        
        # Verify nested structure
        self.assertEqual(len(level3.winfo_children()), 5)

    def test_widget_error_handling(self):
        """Test widget creation with invalid parameters."""
        # Test widget with invalid color
        try:
            frame = ctk.CTkFrame(self.test_container, fg_color="invalid_color")
            # Should not crash, CustomTkinter should handle gracefully
            frame.pack()
            self.root.update_idletasks()
        except Exception as e:
            # If it does raise an exception, that's also acceptable
            self.assertIsInstance(e, (ValueError, tk.TclError))

    def test_widget_state_changes(self):
        """Test widget state changes don't cause crashes."""
        button = ctk.CTkButton(self.test_container, text="Test Button")
        entry = ctk.CTkEntry(self.test_container, placeholder_text="Test Entry")
        
        button.pack(pady=5)
        entry.pack(pady=5)
        
        # Test state changes
        button.configure(state='disabled')
        self.assertEqual(button.cget('state'), 'disabled')
        
        # Test re-enabled state
        button.configure(state='normal')
        self.assertEqual(button.cget('state'), 'normal')
        
        # Test entry state
        entry.configure(state='readonly')
        self.assertEqual(entry.cget('state'), 'readonly')

    def test_theme_switching(self):
        """Test theme switching functionality."""
        # Create widgets with different themes
        light_frame = ctk.CTkFrame(self.test_container)
        light_frame.pack(fill='x', pady=5)
        
        # Switch to dark theme
        ctk.set_appearance_mode("dark")
        
        dark_frame = ctk.CTkFrame(self.test_container)
        dark_frame.pack(fill='x', pady=5)
        
        # Switch back to light theme
        ctk.set_appearance_mode("light")
        
        self.root.update_idletasks()
        
        # Verify frames exist (theme switching should not break widgets)
        self.assertEqual(len(self.test_container.winfo_children()), 2)

    def test_memory_cleanup(self):
        """Test that widget creation/destruction doesn't leak memory."""
        import gc
        
        # Create many widgets
        widgets = []
        for i in range(100):
            widget = ctk.CTkLabel(self.test_container, text=f"Widget {i}")
            widgets.append(widget)
            widget.pack()
        
        self.root.update_idletasks()
        
        # Destroy all widgets
        for widget in widgets:
            widget.destroy()
        
        # Force garbage collection
        gc.collect()
        
        # Verify widgets are cleaned up
        self.assertEqual(len(self.test_container.winfo_children()), 0)

    def test_checker_app_instantiation(self):
        """Test CheckerApp main class can be instantiated (smoke test)."""
        # Mock dependencies to avoid full app startup
        with patch('checker_app.logging') as mock_logging, \
             patch('checker_app.os.path.exists', return_value=True), \
             patch('checker_app.json.load', return_value={}), \
             patch('checker_app.UITheme') as mock_theme, \
             patch('checker_app.StructuredLogger') as mock_logger:
            
            # Setup mocks
            mock_theme.return_value = MagicMock()
            mock_logger.return_value = MagicMock()
            
            try:
                # Import and instantiate CheckerApp
                from checker_app import CheckerApp
                
                # Create a minimal test instance
                app = CheckerApp()
                self.assertIsInstance(app, CheckerApp)
                
                # Test that root window was created
                self.assertIsNotNone(app.root)
                
                # Clean up
                app.root.destroy()
                
            except Exception as e:
                self.fail(f"CheckerApp instantiation failed: {e}")

    def test_workflow_stub_creation(self):
        """Test that workflow stubs can be created."""
        # Mock workflow router
        with patch('app_managers.WorkflowRouter') as mock_router:
            mock_instance = MagicMock()
            mock_router.return_value = mock_instance
            
            # Test stub creation method
            try:
                from app_managers import WorkflowRouter
                router = WorkflowRouter(MagicMock())
                router.workflow_container = self.test_container
                
                # Test stub creation
                router._create_stub_workflow('test_workflow', 'Test Workflow')
                
                # Verify stub was created
                self.assertIn('test_workflow', router.workflows)
                
            except Exception as e:
                self.fail(f"Workflow stub creation failed: {e}")

    def test_animation_safe_operations(self):
        """Test that animation-related operations don't crash."""
        # Test progressbar animation
        progressbar = ctk.CTkProgressBar(self.test_container)
        progressbar.pack(pady=10)
        
        # Test value changes (simulating animation)
        for value in [0.0, 0.25, 0.5, 0.75, 1.0]:
            progressbar.set(value)
            self.root.update_idletasks()
        
        # Test button hover simulation
        button = ctk.CTkButton(self.test_container, text="Hover Test")
        button.pack(pady=10)
        
        # Simulate hover events
        button.event_generate('<Enter>')
        self.root.update_idletasks()
        
        button.event_generate('<Leave>')
        self.root.update_idletasks()


if __name__ == '__main__':
    unittest.main()
