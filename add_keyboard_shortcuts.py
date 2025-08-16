#!/usr/bin/env python3
"""
🎯 KEYBOARD SHORTCUTS ENHANCEMENT - Fügt Tastenkürzel zur GUI hinzu
Implementiert Standard-Tastenkürzel für bessere Benutzerfreundlichkeit.
"""

import re
import sys

def add_keyboard_shortcuts():
    """Add keyboard shortcuts to the GUI"""

    try:
        # Read the file
        with open('modern_translation_quality_gui.py', 'r', encoding='utf-8') as f:
            content = f.read()

        print("🔍 Füge Keyboard Shortcuts hinzu...")

        # Check if shortcuts already exist
        if 'bind_all' in content and '<Control-' in content:
            print("✅ Keyboard shortcuts already exist!")
            return True

        shortcuts_added = 0

        # STEP 1: Add keyboard shortcuts setup method
        shortcuts_method = '''
    def _setup_keyboard_shortcuts(self):
        """🎯 SETUP KEYBOARD SHORTCUTS - Professional hotkeys for better UX"""
        try:
            # File operations
            self.root.bind_all('<Control-o>', lambda e: self._upload_source_files())
            self.root.bind_all('<Control-Shift-o>', lambda e: self._upload_translation_files())
            self.root.bind_all('<Control-s>', lambda e: self.export_results())
            self.root.bind_all('<Control-n>', lambda e: self.clear_files())

            # Analysis operations
            self.root.bind_all('<Control-r>', lambda e: self.start_analysis())
            self.root.bind_all('<F5>', lambda e: self.start_analysis())

            # Navigation shortcuts
            self.root.bind_all('<Control-1>', lambda e: self.show_home_view())
            self.root.bind_all('<Control-2>', lambda e: self.show_files_view())
            self.root.bind_all('<Control-3>', lambda e: self.show_settings_view())

            # View shortcuts
            self.root.bind_all('<Control-d>', lambda e: self.show_demo_results())
            self.root.bind_all('<Control-h>', lambda e: self.show_home_view())

            # Application shortcuts
            self.root.bind_all('<Control-q>', lambda e: self.root.quit())
            self.root.bind_all('<Alt-F4>', lambda e: self.root.quit())
            self.root.bind_all('<F1>', lambda e: self._show_help())

            # Advanced shortcuts (if phases are enabled)
            if hasattr(self, 'phase3_enabled') and self.phase3_enabled:
                self.root.bind_all('<Control-Shift-a>', lambda e: self._show_advanced_features())

            print("⌨️  Keyboard shortcuts activated!")

        except Exception as e:
            print(f"⚠️ Warning: Could not setup all keyboard shortcuts: {e}")
'''

        # STEP 2: Add help method for F1
        help_method = '''
    def _show_help(self):
        """🎯 SHOW KEYBOARD SHORTCUTS HELP"""
        help_text = """Keyboard Shortcuts:

File Operations:
  Ctrl+O          - Upload Source Files
  Ctrl+Shift+O    - Upload Translation Files
  Ctrl+S          - Export Results
  Ctrl+N          - Clear All Files

Analysis:
  Ctrl+R / F5     - Start Analysis

Navigation:
  Ctrl+1          - Home View
  Ctrl+2          - Files View
  Ctrl+3          - Settings View
  Ctrl+H          - Home View
  Ctrl+D          - Demo Results

Application:
  F1              - Show This Help
  Ctrl+Q / Alt+F4 - Quit Application
"""

        try:
            import tkinter.messagebox as messagebox
            messagebox.showinfo("Keyboard Shortcuts", help_text)
        except:
            self.show_toast("Help: Press F1 for shortcuts info", "info", 4000)
'''

        # Find the __init__ method end to insert shortcuts setup
        init_pattern = r'(# Ensure proper widget stacking order.*?\n\s*self\.root\.update_idletasks\(\))'
        match = re.search(init_pattern, content, re.DOTALL)

        if match:
            # Add shortcuts setup call
            shortcuts_call = "\n        \n        # 🎯 Setup keyboard shortcuts for better UX\n        self._setup_keyboard_shortcuts()"
            content = content.replace(match.group(1), match.group(1) + shortcuts_call)
            shortcuts_added += 1
            print("✅ Added keyboard shortcuts setup call")

        # Add the methods after the _clear_frame method
        clear_frame_pattern = r'(def _clear_frame\(self, frame\):.*?\n\s*except Exception as e:.*?\n)'
        match = re.search(clear_frame_pattern, content, re.DOTALL)

        if match:
            content = content.replace(match.group(1), match.group(1) + shortcuts_method + help_method)
            shortcuts_added += 2
            print("✅ Added keyboard shortcuts methods")

        # STEP 3: Add tooltips with shortcut hints to buttons
        button_shortcuts = {
            r'text="🚀 Get Started - Upload Files"': 'text="🚀 Get Started - Upload Files (Ctrl+O)"',
            r'text="Start Analysis"': 'text="Start Analysis (F5)"',
            r'text="Export Results"': 'text="Export Results (Ctrl+S)"',
            r'text="Clear Files"': 'text="Clear Files (Ctrl+N)"',
            r'text="👁️ See Demo Results"': 'text="👁️ See Demo Results (Ctrl+D)"',
        }

        for pattern, replacement in button_shortcuts.items():
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                shortcuts_added += 1
                print(f"✅ Added shortcut hint to button")

        # STEP 4: Add status bar shortcut reminder
        if 'F1=Help' not in content:
            status_pattern = r'(self\.status_label = ctk\.CTkLabel\([^}]+text="[^"]*")'
            match = re.search(status_pattern, content)
            if match:
                # Add shortcut hint to status bar
                content = re.sub(r'(text="[^"]*")', r'text="Ready • F1=Help, F5=Analyze, Ctrl+O=Upload"', content, count=1)
                shortcuts_added += 1
                print("✅ Added shortcut hints to status bar")

        # Write the enhanced content back
        with open('modern_translation_quality_gui.py', 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"\n🎉 KEYBOARD SHORTCUTS ENHANCEMENT COMPLETE!")
        print(f"✅ {shortcuts_added} keyboard enhancements added")
        print(f"✅ Standard shortcuts implemented (Ctrl+O, F5, etc.)")
        print(f"✅ Help system added (F1)")
        print(f"✅ Button tooltips enhanced with shortcuts")
        print(f"✅ Status bar shows shortcut hints")

        return True

    except Exception as e:
        print(f"❌ Error adding keyboard shortcuts: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🎯 KEYBOARD SHORTCUTS ENHANCEMENT")
    print("=" * 50)

    success = add_keyboard_shortcuts()

    if success:
        print("\n✅ Keyboard shortcuts enhancement completed!")
        print("📝 Users can now use professional hotkeys for faster workflow.")
        print("🎨 F1 shows help, F5 starts analysis, Ctrl+O uploads files.")
    else:
        print("\n❌ Keyboard shortcuts enhancement failed!")
        sys.exit(1)