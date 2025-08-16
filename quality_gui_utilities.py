"""
🔧 QUALITY GUI - UTILITY FUNCTIONS MODULE
===========================================

Dieses Modul enthält alle Utility-Funktionen und Helper-Methoden für die
Translation Quality Checker Anwendung.

MODUL-STRUKTUR:
- Toast Notification System: Erweiterte Benachrichtigungen
- File Management Utilities: Datei-Operationen
- UI State Management: Zustandsverwaltung
- Configuration Helpers: Konfigurations-Utilities
- Search & Filter Functions: Such- und Filter-Funktionen
- Validation Utilities: Eingabe-Validierung
- Theme & Styling Helpers: Design-Utilities

VERWENDUNG:
    from quality_gui_utilities import ToastNotification, FileManager, UIStateManager

    toast = ToastNotification(parent)
    toast.show_toast("Nachricht", "success")

    # File Manager nutzen
    fm = FileManager()
    files = fm.get_project_files(project_path)

    # UI State verwalten
    state = UIStateManager()
    state.save_window_geometry(window)

ABHÄNGIGKEITEN:
- customtkinter (ctk)
- tkinter (tk)
- os, json, datetime
- logging

DATEI-ZUGEHÖRIGKEIT:
- Ursprung: modern_translation_quality_gui.py (Zeilen 1769-3400)
- Kategorie: Utilities & Helper Functions
- Zweck: Wiederverwendbare Hilfsfunktionen
"""
import os


import customtkinter as ctk
import tkinter as tk
import os
import json
import datetime
import logging
from typing import Dict, List, Optional, Any, Callable, Union


# =========================== TOAST NOTIFICATION SYSTEM ===========================

class ToastNotification:
    """Professional toast notification system with multiple styles and animations"""

    def __init__(self, parent, position="top-right", duration=3000):
        self.parent = parent
        self.position = position
        self.default_duration = duration
        self.active_toasts = []
        self.toast_spacing = 10

        # Toast styles
        self.toast_styles = {
            'success': {
                'bg_color': '#10B981',
                'text_color': '#FFFFFF',
                'border_color': '#059669',
                'icon': '✅'
            },
            'error': {
                'bg_color': '#EF4444',
                'text_color': '#FFFFFF',
                'border_color': '#DC2626',
                'icon': '❌'
            },
            'warning': {
                'bg_color': '#F59E0B',
                'text_color': '#FFFFFF',
                'border_color': '#D97706',
                'icon': '⚠️'
            },
            'info': {
                'bg_color': '#3B82F6',
                'text_color': '#FFFFFF',
                'border_color': '#2563EB',
                'icon': 'ℹ️'
            }
        }

    def show_toast(self, message: str, toast_type: str = "info", duration: int = None):
        """Show toast notification with specified type and duration"""
        if duration is None:
            duration = self.default_duration

        style = self.toast_styles.get(toast_type, self.toast_styles['info'])

        # Create toast window
        toast_window = tk.Toplevel(self.parent)
        toast_window.wm_overrideredirect(True)
        toast_window.wm_attributes('-topmost', True)

        # Toast frame
        toast_frame = ctk.CTkFrame(
            toast_window,
            fg_color=style['bg_color'],
            border_color=style['border_color'],
            border_width=1,
            corner_radius=8
        )
        toast_frame.pack(padx=2, pady=2)

        # Message container
        message_frame = ctk.CTkFrame(toast_frame, fg_color='transparent')
        message_frame.pack(padx=12, pady=8)

        # Icon and message
        content_frame = ctk.CTkFrame(message_frame, fg_color='transparent')
        content_frame.pack(fill='x')

        # Icon (removed per NO ICONS POLICY)

        # Message text
        message_label = ctk.CTkLabel(
            content_frame,
            text=message,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=style['text_color'],
            wraplength=300
        )
        message_label.pack(side='left', fill='x', expand=True)

        # Close button
        close_button = ctk.CTkButton(
            content_frame,
            text="×",
            width=20,
            height=20,
            corner_radius=10,
            fg_color='transparent',
            text_color=style['text_color'],
            hover_color='rgba(255,255,255,0.1)',
            command=lambda: self._close_toast(toast_window)
        )
        close_button.pack(side='right', padx=(8, 0))

        # Position toast
        self._position_toast(toast_window)

        # Add to active toasts
        self.active_toasts.append(toast_window)

        # Auto-close after duration
        toast_window.after(duration, lambda: self._close_toast(toast_window))

        # Fade-in animation
        self._animate_toast_in(toast_window)

        return toast_window

    def _position_toast(self, toast_window):
        """Position toast based on configured position"""
        toast_window.update_idletasks()

        # Get screen dimensions
        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()

        # Get toast dimensions
        toast_width = toast_window.winfo_reqwidth()
        toast_height = toast_window.winfo_reqheight()

        # Calculate position offset for multiple toasts
        offset_y = len(self.active_toasts) * (toast_height + self.toast_spacing)

        # Position based on preference
        if self.position == "top-right":
            x = screen_width - toast_width - 20
            y = 20 + offset_y
        elif self.position == "top-left":
            x = 20
            y = 20 + offset_y
        elif self.position == "bottom-right":
            x = screen_width - toast_width - 20
            y = screen_height - toast_height - 20 - offset_y
        elif self.position == "bottom-left":
            x = 20
            y = screen_height - toast_height - 20 - offset_y
        else:  # center
            x = (screen_width - toast_width) // 2
            y = (screen_height - toast_height) // 2 + offset_y

        toast_window.wm_geometry(f"+{x}+{y}")

    def _animate_toast_in(self, toast_window):
        """Animate toast appearance"""
        toast_window.wm_attributes('-alpha', 0.0)

        def fade_in(alpha=0.0):
            alpha += 0.1
            if alpha <= 1.0:
                toast_window.wm_attributes('-alpha', alpha)
                toast_window.after(50, lambda: fade_in(alpha))

        fade_in()

    def _close_toast(self, toast_window):
        """Close toast with fade-out animation"""
        if toast_window in self.active_toasts:
            self.active_toasts.remove(toast_window)

        def fade_out(alpha=1.0):
            alpha -= 0.1
            if alpha >= 0.0:
                toast_window.wm_attributes('-alpha', alpha)
                toast_window.after(50, lambda: fade_out(alpha))
            else:
                toast_window.destroy()

        fade_out()

    def clear_all_toasts(self):
        """Clear all active toasts"""
        for toast in self.active_toasts.copy():
            self._close_toast(toast)

# =========================== FILE MANAGEMENT UTILITIES ===========================

class FileManager:
    """Comprehensive file management utilities for project operations"""

    def __init__(self):
        self.supported_formats = {
            '.pdf': 'PDF Document',
            '.docx': 'Word Document',
            '.doc': 'Word Document (Legacy)',
            '.txt': 'Text File',
            '.rtf': 'Rich Text Format',
            '.odt': 'OpenDocument Text'
        }

    def get_project_files(self, project_path: str, include_subdirs: bool = True) -> Dict[str, List[str]]:
        """Get all project files organized by type"""
        files = {
            'source': [],
            'translation': [],
            'other': []
        }

        if not os.path.exists(project_path):
            return files

        try:
            if include_subdirs:
                for root, dirs, filenames in os.walk(project_path):
                    for filename in filenames:
                        file_path = os.path.join(root, filename)
                        file_category = self._categorize_file(file_path)
                        files[file_category].append(file_path)
            else:
                for filename in os.listdir(project_path):
                    file_path = os.path.join(project_path, filename)
                    if os.path.isfile(file_path):
                        file_category = self._categorize_file(file_path)
                        files[file_category].append(file_path)
        except Exception as e:
            logging.error(f"Error reading project files: {e}")

        return files

    def _categorize_file(self, file_path: str) -> str:
        """Categorize file based on path and name patterns"""
        filename = os.path.basename(file_path).lower()

        # Check if it's a supported format
        if not any(filename.endswith(ext) for ext in self.supported_formats.keys()):
            return 'other'

        # Categorize based on naming patterns
        if any(keyword in filename for keyword in ['translation', 'translated', 'target', 'übersetzung']):
            return 'translation'
        elif any(keyword in filename for keyword in ['source', 'original', 'quell', 'ausgangsdatei']):
            return 'source'
        else:
            # Default categorization based on directory structure
            path_lower = file_path.lower()
            if any(keyword in path_lower for keyword in ['translation', 'target', 'übersetzung']):
                return 'translation'
            else:
                return 'source'

    def is_supported_file(self, file_path: str) -> bool:
        """Check if file format is supported"""
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.supported_formats

    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get comprehensive file information"""
        try:
            stat = os.stat(file_path)
            return {
                'name': os.path.basename(file_path),
                'path': file_path,
                'size': stat.st_size,
                'size_formatted': self._format_file_size(stat.st_size),
                'modified': datetime.datetime.fromtimestamp(stat.st_mtime),
                'extension': os.path.splitext(file_path)[1].lower(),
                'type': self.supported_formats.get(os.path.splitext(file_path)[1].lower(), 'Unknown'),
                'exists': True
            }
        except Exception as e:
            return {
                'name': os.path.basename(file_path),
                'path': file_path,
                'error': str(e),
                'exists': False
            }

    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"

        size_names = ["B", "KB", "MB", "GB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"

    def copy_file_to_project(self, source_path: str, project_path: str, category: str = 'source') -> str:
        """Copy file to project directory with proper organization"""
        try:
            # Create category directory if needed
            category_dir = os.path.join(project_path, category)
            os.makedirs(category_dir, exist_ok=True)

            # Generate unique filename if needed
            filename = os.path.basename(source_path)
            dest_path = os.path.join(category_dir, filename)

            counter = 1
            base_name, ext = os.path.splitext(filename)
            while os.path.exists(dest_path):
                new_filename = f"{base_name}_{counter}{ext}"
                dest_path = os.path.join(category_dir, new_filename)
                counter += 1

            # Copy file
            import shutil
            shutil.copy2(source_path, dest_path)
            return dest_path

        except Exception as e:
            logging.error(f"Error copying file: {e}")
            raise

# =========================== UI STATE MANAGEMENT ===========================

class UIStateManager:
    """Manage UI state, preferences and window configurations"""

    def __init__(self, config_file: str = "ui_state.json"):
        self.config_file = config_file
        self.state = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        """Load UI state from configuration file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logging.warning(f"Failed to load UI state: {e}")

        # Return default state
        return {
            'window': {
                'width': 1400,
                'height': 900,
                'x': 100,
                'y': 100
            },
            'preferences': {
                'theme': 'light',
                'language': 'en',
                'auto_save': True,
                'toast_position': 'top-right'
            },
            'recent_projects': [],
            'ui_elements': {}
        }

    def save_state(self):
        """Save current UI state to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Failed to save UI state: {e}")

    def get_window_geometry(self) -> str:
        """Get saved window geometry"""
        w = self.state['window']
        return f"{w['width']}x{w['height']}+{w['x']}+{w['y']}"

    def save_window_geometry(self, window):
        """Save current window geometry"""
        try:
            geometry = window.winfo_geometry()
            # Parse geometry string: "widthxheight+x+y"
            import re
            match = re.match(r'(\d+)x(\d+)\+(\d+)\+(\d+)', geometry)
            if match:
                width, height, x, y = map(int, match.groups())
                self.state['window'] = {
                    'width': width,
                    'height': height,
                    'x': x,
                    'y': y
                }
                self.save_state()
        except Exception as e:
            logging.warning(f"Failed to save window geometry: {e}")

    def get_preference(self, key: str, default=None):
        """Get user preference value"""
        return self.state['preferences'].get(key, default)

    def set_preference(self, key: str, value):
        """Set user preference value"""
        self.state['preferences'][key] = value
        self.save_state()

    def add_recent_project(self, project_path: str):
        """Add project to recent projects list"""
        recent = self.state['recent_projects']

        # Remove if already exists
        if project_path in recent:
            recent.remove(project_path)

        # Add to beginning
        recent.insert(0, project_path)

        # Keep only last 10
        self.state['recent_projects'] = recent[:10]
        self.save_state()

    def get_recent_projects(self) -> List[str]:
        """Get list of recent projects"""
        # Filter out non-existent paths
        existing_projects = [p for p in self.state['recent_projects'] if os.path.exists(p)]

        # Update state if some were removed
        if len(existing_projects) != len(self.state['recent_projects']):
            self.state['recent_projects'] = existing_projects
            self.save_state()

        return existing_projects

    def save_ui_element_state(self, element_id: str, state_data: Dict[str, Any]):
        """Save state for specific UI element"""
        self.state['ui_elements'][element_id] = state_data
        self.save_state()

    def get_ui_element_state(self, element_id: str) -> Dict[str, Any]:
        """Get saved state for UI element"""
        return self.state['ui_elements'].get(element_id, {})

# =========================== SEARCH AND FILTER UTILITIES ===========================

class SearchFilter:
    """Advanced search and filter functionality for file lists and content"""

    def __init__(self):
        self.search_history = []
        self.max_history = 20

    def filter_files(self, files: List[str], query: str, criteria: List[str] = None) -> List[str]:
        """Filter file list based on search query and criteria"""
        if not query:
            return files

        query_lower = query.lower()
        filtered_files = []

        criteria = criteria or ['filename', 'path', 'extension']

        for file_path in files:
            filename = os.path.basename(file_path).lower()
            path_lower = file_path.lower()
            ext_lower = os.path.splitext(file_path)[1].lower()

            match = False

            if 'filename' in criteria and query_lower in filename:
                match = True
            elif 'path' in criteria and query_lower in path_lower:
                match = True
            elif 'extension' in criteria and query_lower in ext_lower:
                match = True

            if match:
                filtered_files.append(file_path)

        # Add to search history
        self._add_to_history(query)

        return filtered_files

    def search_file_content(self, file_path: str, query: str) -> Dict[str, Any]:
        """Search for query within file content"""
        results = {
            'file_path': file_path,
            'query': query,
            'matches': [],
            'total_matches': 0
        }

        try:
            # Determine file type and read accordingly
            ext = os.path.splitext(file_path)[1].lower()

            if ext == '.pdf':
                content = self._extract_pdf_text(file_path)
            elif ext in ['.docx', '.doc']:
                content = self._extract_word_text(file_path)
            else:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

            if content:
                results.update(self._find_text_matches(content, query))

        except Exception as e:
            results['error'] = str(e)

        return results

    def _find_text_matches(self, content: str, query: str) -> Dict[str, Any]:
        """Find all matches of query in text content"""
        import re

        matches = []
        query_pattern = re.compile(re.escape(query), re.IGNORECASE)

        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            line_matches = list(query_pattern.finditer(line))
            for match in line_matches:
                context_start = max(0, match.start() - 50)
                context_end = min(len(line), match.end() + 50)
                context = line[context_start:context_end]

                matches.append({
                    'line_number': line_num,
                    'position': match.start(),
                    'context': context,
                    'matched_text': match.group()
                })

        return {
            'matches': matches,
            'total_matches': len(matches)
        }

    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            import PyPDF2
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                return text
        except ImportError:
            logging.warning("PyPDF2 not available for PDF text extraction")
            return ""
        except Exception as e:
            logging.error(f"Error extracting PDF text: {e}")
            return ""

    def _extract_word_text(self, file_path: str) -> str:
        """Extract text from Word document"""
        try:
            import docx
            doc = docx.Document(file_path)
            return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        except ImportError:
            logging.warning("python-docx not available for Word text extraction")
            return ""
        except Exception as e:
            logging.error(f"Error extracting Word text: {e}")
            return ""

    def _add_to_history(self, query: str):
        """Add search query to history"""
        if query and query not in self.search_history:
            self.search_history.insert(0, query)
            self.search_history = self.search_history[:self.max_history]

    def get_search_history(self) -> List[str]:
        """Get search history"""
        return self.search_history.copy()

    def clear_search_history(self):
        """Clear search history"""
        self.search_history.clear()

# =========================== VALIDATION UTILITIES ===========================

class ValidationUtils:
    """Input validation and data verification utilities"""

    @staticmethod
    def validate_file_path(path: str) -> Dict[str, Any]:
        """Validate file path and return detailed info"""
        result = {
            'valid': False,
            'exists': False,
            'readable': False,
            'supported_format': False,
            'error': None,
            'file_info': {}
        }

        try:
            # Check if path is provided
            if not path or not path.strip():
                result['error'] = "File path is empty"
                return result

            # Check if file exists
            if not os.path.exists(path):
                result['error'] = "File does not exist"
                return result

            result['exists'] = True

            # Check if it's a file (not directory)
            if not os.path.isfile(path):
                result['error'] = "Path is not a file"
                return result

            # Check if readable
            try:
                with open(path, 'rb') as f:
                    f.read(1)
                result['readable'] = True
            except:
                result['error'] = "File is not readable"
                return result

            # Check format support
            fm = FileManager()
            if fm.is_supported_file(path):
                result['supported_format'] = True
                result['file_info'] = fm.get_file_info(path)
            else:
                result['error'] = "File format not supported"
                return result

            result['valid'] = True

        except Exception as e:
            result['error'] = str(e)

        return result

    @staticmethod
    def validate_project_name(name: str) -> Dict[str, Any]:
        """Validate project name"""
        result = {
            'valid': False,
            'error': None,
            'suggestions': []
        }

        if not name or not name.strip():
            result['error'] = "Project name cannot be empty"
            return result

        name = name.strip()

        # Check length
        if len(name) < 3:
            result['error'] = "Project name must be at least 3 characters"
            return result

        if len(name) > 100:
            result['error'] = "Project name must be less than 100 characters"
            return result

        # Check for invalid characters
        import re
        if not re.match(r'^[a-zA-Z0-9\s\-_\.]+$', name):
            result['error'] = "Project name contains invalid characters"
            result['suggestions'] = ["Use only letters, numbers, spaces, hyphens, underscores, and dots"]
            return result

        # Check for reserved names
        reserved_names = ['con', 'prn', 'aux', 'nul', 'com1', 'com2', 'com3', 'com4', 'com5', 'com6', 'com7', 'com8', 'com9', 'lpt1', 'lpt2', 'lpt3', 'lpt4', 'lpt5', 'lpt6', 'lpt7', 'lpt8', 'lpt9']
        if name.lower() in reserved_names:
            result['error'] = "Project name is a reserved system name"
            return result

        result['valid'] = True
        return result

    @staticmethod
    def validate_customer_name(name: str) -> Dict[str, Any]:
        """Validate customer name"""
        result = {
            'valid': False,
            'error': None,
            'formatted_name': None
        }

        if not name or not name.strip():
            result['error'] = "Customer name cannot be empty"
            return result

        name = name.strip()

        # Check length
        if len(name) < 2:
            result['error'] = "Customer name must be at least 2 characters"
            return result

        if len(name) > 200:
            result['error'] = "Customer name must be less than 200 characters"
            return result

        # Format name (capitalize words)
        formatted_name = ' '.join(word.capitalize() for word in name.split())

        result['valid'] = True
        result['formatted_name'] = formatted_name
        return result

# =========================== CONFIGURATION HELPERS ===========================

class ConfigManager:
    """Configuration management and settings utilities"""

    def __init__(self, config_file: str = "checker_config.json"):
        self.config_file = config_file
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logging.warning(f"Failed to load config: {e}")

        # Return default configuration
        return {
            'app': {
                'name': 'Translation Quality Checker',
                'version': '1.0.0',
                'debug_mode': False
            },
            'ui': {
                'theme': 'light',
                'language': 'en',
                'font_size': 12,
                'toast_duration': 3000,
                'auto_save_interval': 300
            },
            'analysis': {
                'max_file_size_mb': 100,
                'supported_formats': ['.pdf', '.docx', '.doc', '.txt', '.rtf'],
                'batch_size': 10,
                'timeout_seconds': 300
            },
            'paths': {
                'projects_root': 'projects',
                'temp_dir': 'temp',
                'logs_dir': 'logs',
                'backups_dir': 'backups'
            }
        }

    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Failed to save config: {e}")

    def get(self, key_path: str, default=None):
        """Get configuration value using dot notation"""
        keys = key_path.split('.')
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def set(self, key_path: str, value):
        """Set configuration value using dot notation"""
        keys = key_path.split('.')
        config = self.config

        # Navigate to parent
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        # Set value
        config[keys[-1]] = value
        self.save_config()

    def ensure_directories(self):
        """Ensure all required directories exist"""
        paths = self.get('paths', {})
        for dir_key, dir_path in paths.items():
            try:
                os.makedirs(dir_path, exist_ok=True)
            except Exception as e:
                logging.error(f"Failed to create directory {dir_path}: {e}")

    def get_log_level(self) -> int:
        """Get logging level based on debug mode"""
        debug_mode = self.get('app.debug_mode', False)
        return logging.DEBUG if debug_mode else logging.INFO