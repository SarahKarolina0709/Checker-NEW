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
import json
import datetime
import logging
from typing import Dict, List, Optional, Any, Callable, Union


# =========================== TOAST NOTIFICATION SYSTEM ===========================

class ToastNotification:
    """Professional toast notification system (thread-safe wrapper, reflow)."""

    DEFAULT_FONT = ("Segoe UI", 12)

    def __init__(self, parent, position="top-right", duration=3000, max_width=360):
        self.parent = parent
        self.position = position
        self.default_duration = duration
        self.max_width = max_width
        self.active_toasts: list[tk.Toplevel] = []
        self.toast_spacing = 10
        self._timers: dict[int, list[str]] = {}
        # Styles (könnten später via Design-System Tokens ersetzt werden)
        self.toast_styles = {
            'success': {'bg_color': '#10B981', 'text_color': '#FFFFFF', 'border_color': '#059669'},
            'error':   {'bg_color': '#EF4444', 'text_color': '#FFFFFF', 'border_color': '#DC2626'},
            'warning': {'bg_color': '#F59E0B', 'text_color': '#FFFFFF', 'border_color': '#D97706'},
            # Vereinheitlichtes Info-Blau -> Brand Primary
            'info':    {'bg_color': '#1F4E79', 'text_color': '#FFFFFF', 'border_color': '#1A3F65'},
        }

    def _safe_after(self, widget, delay, fn):
        """Schedule a callback and track timer for later cancellation."""
        try:
            aid = widget.after(delay, fn)
            self._timers.setdefault(widget.winfo_id(), []).append(aid)
            return aid
        except Exception:
            return None

    def _cancel_timers(self, toast_window: tk.Toplevel):
        """Cancel all pending timers for a toast window."""
        try:
            for aid in self._timers.pop(toast_window.winfo_id(), []):
                try:
                    toast_window.after_cancel(aid)
                except Exception:
                    pass
        except Exception:
            pass

    def show_toast(self, message: str, toast_type: str = "info", duration: int = None):
        """Thread-sicherer Entry-Point – delegiert in Haupt-Thread."""
        if hasattr(self.parent, 'after'):
            return self.parent.after(0, lambda: self._show_toast_sync(message, toast_type, duration))
        return self._show_toast_sync(message, toast_type, duration)

    def _show_toast_sync(self, message: str, toast_type: str = "info", duration: int | None = None):
        duration = self.default_duration if duration is None else int(duration)
        style = self.toast_styles.get(toast_type, self.toast_styles['info'])

        tw = tk.Toplevel(self.parent)
        tw.wm_overrideredirect(True)
        try:
            tw.wm_attributes('-topmost', True)
        except Exception:
            pass
        try:
            tw.wm_attributes('-alpha', 0.0)
        except Exception:
            pass

        try:
            from design_system import get_color as _ds_get_color  # lazy import
            transparent = _ds_get_color('transparent') or 'transparent'
        except Exception:
            transparent = 'transparent'

        frame = ctk.CTkFrame(
            tw,
            fg_color=style['bg_color'],
            border_color=style['border_color'],
            border_width=1,
            corner_radius=8
        )
        frame.pack(padx=2, pady=2)

        inner = ctk.CTkFrame(frame, fg_color=transparent)
        inner.pack(padx=12, pady=8, fill="x")

        row = ctk.CTkFrame(inner, fg_color=transparent)
        row.pack(fill='x')

        msg = ctk.CTkLabel(
            row,
            text=message,
            font=ctk.CTkFont(family=self.DEFAULT_FONT[0], size=self.DEFAULT_FONT[1]),
            text_color=style['text_color'],
            wraplength=self.max_width
        )
        msg.pack(side='left', fill='x', expand=True)

        close = ctk.CTkLabel(
            row,
            text="×",
            font=ctk.CTkFont("Segoe UI", 14, "bold"),
            text_color=style['text_color']
        )
        close.pack(side='right', padx=(8, 0))

        def _close(_e=None):
            self._close_toast(tw)

        close.bind("<Button-1>", _close)
        close.bind("<Enter>", lambda _e: close.configure(text_color="#FFFFFF"))
        close.bind("<Leave>", lambda _e: close.configure(text_color=style['text_color']))
        tw.bind("<Escape>", _close)
        # Clean up timers when destroyed
        tw.bind("<Destroy>", lambda _e: self._cancel_timers(tw), add="+")

        self._position_toast(tw)
        self.active_toasts.append(tw)

        self._safe_after(tw, duration, lambda: self._close_toast(tw))
        self._animate_toast_in(tw)
        return tw

    def _anchor_rect(self):
        """Return anchor rectangle (x0,y0,w,h) using parent if mapped, else screen; clamped."""
        try:
            if self.parent.winfo_ismapped():
                pw, ph = self.parent.winfo_width(), self.parent.winfo_height()
                px, py = self.parent.winfo_rootx(), self.parent.winfo_rooty()
                if pw > 0 and ph > 0:
                    return max(0, px), max(0, py), pw, ph
        except Exception:
            pass
        return 0, 0, self.parent.winfo_screenwidth(), self.parent.winfo_screenheight()

    def _position_toast(self, tw: tk.Toplevel):
        """Position toast – bevorzugt relativ zum Parent (wenn sichtbar)."""
        tw.update_idletasks()
        x0, y0, w, h = self._anchor_rect()
        tw_w, tw_h = tw.winfo_reqwidth(), tw.winfo_reqheight()
        offset_y_stack = sum(t.winfo_reqheight() + self.toast_spacing for t in self.active_toasts)

        if self.position == "top-right":
            x = x0 + w - tw_w - 20
            y = y0 + 20 + offset_y_stack
        elif self.position == "top-left":
            x = x0 + 20
            y = y0 + 20 + offset_y_stack
        elif self.position == "bottom-right":
            x = x0 + w - tw_w - 20
            y = y0 + h - tw_h - 20 - offset_y_stack
        elif self.position == "bottom-left":
            x = x0 + 20
            y = y0 + h - tw_h - 20 - offset_y_stack
        else:
            x = x0 + (w - tw_w) // 2
            y = y0 + (h - tw_h) // 2 + offset_y_stack

        tw.wm_geometry(f"+{max(0, int(x))}+{max(0, int(y))}")

    def _animate_toast_in(self, tw: tk.Toplevel):
        """Animate toast appearance with timer tracking."""
        try:
            tw.wm_attributes('-alpha', 0.0)
        except Exception:
            return

        def fade(alpha=0.0):
            alpha += 0.1
            try:
                tw.wm_attributes('-alpha', min(alpha, 1.0))
            except Exception:
                return
            if alpha < 1.0:
                self._safe_after(tw, 50, lambda: fade(alpha))

        fade(0.0)

    def _close_toast(self, tw: tk.Toplevel):
        """Close toast (fade-out) und reflow verbleibende."""
        if tw not in self.active_toasts:
            return
        # Remove first so reflow reflects impending removal
        self.active_toasts = [t for t in self.active_toasts if t is not tw]

        def fade(alpha=1.0):
            alpha -= 0.1
            try:
                tw.wm_attributes('-alpha', max(alpha, 0.0))
            except Exception:
                alpha = 0.0
            if alpha > 0.0:
                self._safe_after(tw, 50, lambda: fade(alpha))
            else:
                try:
                    tw.destroy()
                finally:
                    # Reflow survivors
                    for t in self.active_toasts:
                        self._position_toast(t)
        fade(1.0)

    def clear_all_toasts(self):
        """Clear all active toasts (robust snapshot)."""
        for toast in list(self.active_toasts):
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

    def _norm(self, p: str) -> str:
        """Normalize path with user/vars expansion and absolute resolution."""
        return os.path.abspath(os.path.expanduser(os.path.expandvars(p)))

    def get_project_files(self, project_path: str, include_subdirs: bool = True,
                          max_files: int | None = None) -> Dict[str, List[str]]:
        """Get all project files organized by type with safety limits."""
        files = {'source': [], 'translation': [], 'other': []}
        base = self._norm(project_path)
        if not os.path.exists(base):
            return files

        try:
            counter = 0
            if include_subdirs:
                for root, _dirs, filenames in os.walk(base, onerror=lambda e: logging.debug(f"os.walk: {e}")):
                    for filename in filenames:
                        fp = self._norm(os.path.join(root, filename))
                        files[self._categorize_file(fp)].append(fp)
                        counter += 1
                        if max_files and counter >= max_files:
                            return files
            else:
                for filename in os.listdir(base):
                    fp = self._norm(os.path.join(base, filename))
                    if os.path.isfile(fp):
                        files[self._categorize_file(fp)].append(fp)
        except Exception as e:
            logging.error(f"Error reading project files: {e}", exc_info=True)
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
                'size_formatted': format_file_size(stat.st_size),
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

    def copy_file_to_project(self, source_path: str, project_path: str, category: str = 'source') -> str:
        """Copy file to project directory ensuring unique filename."""
        import shutil
        try:
            category_dir = os.path.join(project_path, category)
            os.makedirs(category_dir, exist_ok=True)
            filename = os.path.basename(source_path)
            dest_path = os.path.join(category_dir, filename)
            base, ext = os.path.splitext(filename)
            i = 1
            while os.path.exists(dest_path):
                dest_path = os.path.join(category_dir, f"{base}_{i}{ext}")
                i += 1
            shutil.copy2(source_path, dest_path)
            return dest_path
        except Exception as e:
            logging.error(f"Error copying file: {e}", exc_info=True)
            raise

# ------------------------------------------------------------
# PUBLIC UTILITY HELPERS (Single Source of Truth)
# ------------------------------------------------------------
def format_file_size(size_bytes: int) -> str:
    """Zentrale Dateigrößen-Formatierung (TB+ Support, konsistente Rundung)."""
    try:
        if size_bytes is None or size_bytes < 0:
            return "Unknown"
        if size_bytes == 0:
            return "0 B"
        units = ["B", "KB", "MB", "GB", "TB", "PB"]
        import math
        i = min(int(math.floor(math.log(size_bytes, 1024))), len(units) - 1)
        s = size_bytes / (1024 ** i)
        fmt = f"{s:.0f}" if i <= 1 else f"{s:.1f}"
        return f"{fmt} {units[i]}"
    except Exception:
        return "Unknown"

def is_backup_filename(name: str) -> bool:
    """Erkennt Backup/alte Datei-Namen (Single Source für Backup-Filter) mit geringer False-Positive-Rate."""
    try:
        import re
        n = name.lower()
        if re.search(r'(?:^|[\W_])(backup|original|before|alt|copy|deprecated)(?:$|[\W_])', n):
            return True
        if n.endswith('.bak') or '.backup_' in n:
            return True
        return False
    except Exception:
        return False

    # (Fehlerhafte Einrückung für copy_file_to_project entfernt – Methode ist jetzt Teil von FileManager)

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
        """Save current UI state to file (atomic write)."""
        try:
            tmp = f"{self.config_file}.tmp"
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
            os.replace(tmp, self.config_file)
        except Exception as e:
            logging.error(f"Failed to save UI state: {e}", exc_info=True)

    def get_window_geometry(self) -> str:
        """Get saved window geometry (mit Offscreen-Schutz)."""
        w = self.state['window']
        x = max(0, int(w.get('x', 0)))
        y = max(0, int(w.get('y', 0)))
        return f"{w['width']}x{w['height']}+{x}+{y}"

    def save_window_geometry(self, window):
        """Save current window geometry (off-screen safe, tolerate unmapped)."""
        try:
            if not window.winfo_ismapped():
                return
            geometry = window.winfo_geometry()  # "WxH+X+Y"
            import re
            m = re.match(r'(\d+)x(\d+)\+(-?\d+)\+(-?\d+)', geometry)
            if not m:
                return
            w, h, x, y = map(int, m.groups())
            sw, sh = window.winfo_screenwidth(), window.winfo_screenheight()
            x = max(0, min(x, max(0, sw - w)))
            y = max(0, min(y, max(0, sh - h)))
            self.state['window'] = {'width': w, 'height': h, 'x': x, 'y': y}
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

    def search_file_content(self, file_path: str, query: str,
                            max_bytes: int = 5_000_000,
                            word_boundary: bool = False,
                            max_matches: int = 500) -> Dict[str, Any]:
        """Search for query within file content with safeguards and options."""
        res = {'file_path': file_path, 'query': query, 'matches': [], 'total_matches': 0}
        try:
            try:
                if os.path.getsize(file_path) > max_bytes:
                    res['error'] = 'File too large for inline search'
                    return res
            except Exception:
                pass

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
                out = self._find_text_matches(content, query, word_boundary=word_boundary, max_matches=max_matches)
                res.update(out)
        except Exception as e:
            res['error'] = str(e)
        return res

    def _find_text_matches(self, content: str, query: str,
                           word_boundary: bool = False, max_matches: int = 500) -> Dict[str, Any]:
        """Find matches with optional word boundaries and a cap."""
        import re
        pat = r'\b{}\b'.format(re.escape(query)) if word_boundary else re.escape(query)
        rx = re.compile(pat, re.IGNORECASE)

        matches = []
        for ln, line in enumerate(content.splitlines(), 1):
            for m in rx.finditer(line):
                matches.append({
                    'line_number': ln,
                    'position': m.start(),
                    'context': line[max(0, m.start()-50): m.end()+50],
                    'matched_text': m.group()
                })
                if len(matches) >= max_matches:
                    break
            if len(matches) >= max_matches:
                break
        return {'matches': matches, 'total_matches': len(matches)}

    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            import PyPDF2
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
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
            return '\n'.join(p.text for p in doc.paragraphs if p.text)
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
        """Validate file path with clearer error mapping and normalization."""
        res = {'valid': False, 'exists': False, 'readable': False,
               'supported_format': False, 'error': None, 'file_info': {}}
        try:
            if not path or not path.strip():
                res['error'] = "File path is empty"; return res
            p = os.path.abspath(os.path.expanduser(path))
            if not os.path.exists(p):
                res['error'] = "File does not exist"; return res
            if not os.path.isfile(p):
                res['error'] = "Path is not a file"; return res
            res['exists'] = True
            try:
                with open(p, 'rb') as f:
                    f.read(1)
                res['readable'] = True
            except PermissionError:
                res['error'] = "Permission denied"; return res
            except Exception as e:
                res['error'] = f"File is not readable: {e}"; return res
            fm = FileManager()
            if not fm.is_supported_file(p):
                res['error'] = "File format not supported"; return res
            res['supported_format'] = True
            res['file_info'] = fm.get_file_info(p)
            res['valid'] = True
        except Exception as e:
            res['error'] = str(e)
            logging.exception("validate_file_path exception")
        return res

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
        """Save configuration to file (atomic write)."""
        try:
            tmp = f"{self.config_file}.tmp"
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            os.replace(tmp, self.config_file)
        except Exception as e:
            logging.error(f"Failed to save config: {e}", exc_info=True)

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
        """Ensure all required directories exist (expand user/vars)."""
        paths = self.get('paths', {})
        for _k, raw in paths.items():
            try:
                p = os.path.abspath(os.path.expanduser(os.path.expandvars(raw)))
                os.makedirs(p, exist_ok=True)
                logging.debug("Ensured directory exists: %s", p)
            except Exception as e:
                logging.error("Failed to create directory %r: %s", raw, e)

    def get_log_level(self) -> int:
        """Get logging level based on debug mode"""
        debug_mode = self.get('app.debug_mode', False)
        return logging.DEBUG if debug_mode else logging.INFO

# Explicit exports for clarity
__all__ = [
    "ToastNotification", "FileManager", "UIStateManager",
    "SearchFilter", "ValidationUtils", "ConfigManager",
    "format_file_size", "is_backup_filename",
]