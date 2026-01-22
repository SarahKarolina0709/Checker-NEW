#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🛠️ WELCOME SCREEN - UTILS MODULE
===============================

Utility-Funktionen und Helper-Methoden für das Welcome Screen.
Extrahiert aus der ursprünglich 493 KB großen welcome_screen.py für bessere Performance.

Enthält:
- Toast Notifications
- Configuration Management
- File Operations
- Calendar Functions
- Statistics & Analytics
- UI Helper Functions
"""
from datetime import datetime, date, timedelta
from pathlib import Path
import json
import os
import traceback
import calendar
import customtkinter as ctk
import re
from typing import Any, Dict, List, Optional, Tuple

# Neues zentrales Setup
from config_manager import ConfigManager
from logging_setup import setup_logger
from paths import CONFIG_FILE, ANALYTICS_FILE

# Optional Repository-Integration (Recent Projects)
try:
    from repositories.recent_projects_repository import RecentProjectsRepository
except Exception:
    RecentProjectsRepository = None  # type: ignore

class ToastManager:
    """Zentraler Toast-Manager für modulübergreifende Nutzung.
    Verantwortlich für Erstellung, Layout und Entfernung von Toast-Benachrichtigungen.
    """

    def __init__(self, host, get_color, get_font, get_config_value):
        # Host ist typischerweise der WelcomeScreen (benötigt .after und als Parent für Frames)
        self.host = host
        self.get_color = get_color
        self.get_font = get_font
        self.get_config_value = get_config_value

        self._container = None
        self._toasts = []

    # Public API
    def show(self, message: str, toast_type: str = "info", duration: Optional[int] = 3000):
        try:
            if not self._container:
                self._create_container()

            if duration is None or int(duration) <= 0:
                duration = int(self.get_config_value('ui_settings.toast_duration', 3000) or 3000)

            toast = self._create_toast_widget(message, toast_type, duration)
            # Auto-Remove
            self.host.after(duration, lambda: self.remove(toast))
            return toast
        except Exception:
            # Leiser Fallback ohne Abbruch
            try:
                print(f"📢 {toast_type.upper()}: {message}")
            except Exception:
                pass
            return None

    def show_info(self, message: str, duration: Optional[int] = 3000):
        return self.show(message, 'info', duration)

    def show_success(self, message: str, duration: Optional[int] = 3000):
        return self.show(message, 'success', duration)

    def show_warning(self, message: str, duration: Optional[int] = 3000):
        return self.show(message, 'warning', duration)

    def show_error(self, message: str, duration: Optional[int] = 3000):
        return self.show(message, 'error', duration)

    @property
    def count(self) -> int:
        return len(self._toasts)

    def clear(self):
        try:
            for t in list(self._toasts):
                try:
                    if t and t.winfo_exists():
                        t.destroy()
                except Exception:
                    pass
            self._toasts.clear()
        except Exception:
            pass

    # Internal helpers
    def _create_container(self):
        try:
            self._container = ctk.CTkFrame(self.host, fg_color="transparent", corner_radius=0, width=370)
            self._container.place(relx=1.0, rely=0.0, anchor="ne", x=-20, y=80)
        except Exception as e:
            print(f"❌ Toast container error: {e}")

    def _create_toast_widget(self, message: str, toast_type: str, duration: int):
        try:
            accent_map = {
                'info': self.get_color('info'),
                'success': self.get_color('success'),
                'warning': self.get_color('warning'),
                'error': self.get_color('error')
            }
            accent = accent_map.get(toast_type, self.get_color('info'))

            bg_color = self.get_color('surface_elevated', '#FFFFFF')
            text_primary = self.get_color('gray_700', '#374151')
            text_secondary = self.get_color('gray_500', '#6B7280')

            toast_frame = ctk.CTkFrame(
                self._container,
                fg_color=bg_color,
                corner_radius=8,
                border_width=1,
                border_color=self.get_color('surface_border', '#E5E7EB')
            )

            accent_bar = ctk.CTkFrame(toast_frame, fg_color=accent, width=5, corner_radius=8)
            accent_bar.pack(side="left", fill="y")

            content_frame = ctk.CTkFrame(toast_frame, fg_color="transparent")
            content_frame.pack(side="left", fill="both", expand=True, padx=12, pady=10)

            message_label = ctk.CTkLabel(
                content_frame,
                text=message,
                font=ctk.CTkFont(*self.get_font('body_sm')),
                text_color=text_primary,
                wraplength=260,
                anchor="w",
                justify="left"
            )
            message_label.pack(side="left", fill="both", expand=True)

            close_btn = ctk.CTkButton(
                content_frame,
                text="Schließen",
                command=lambda: self.remove(toast_frame),
                font=ctk.CTkFont(*self.get_font('button_sm')),
                fg_color="transparent",
                text_color=text_secondary,
                hover_color=self.get_color('surface_hover', '#F3F4F6'),
                height=24,
                width=80,
                corner_radius=6,
            )
            close_btn.pack(side="right", padx=(8, 0))

            self._toasts.append(toast_frame)
            self._layout()
            self._animate_in(toast_frame)
            return toast_frame
        except Exception as e:
            print(f"❌ Toast widget error: {e}")
            return None

    def _animate_in(self, toast_widget):
        try:
            if not self.get_config_value('ui_settings.animation_enabled', True):
                if toast_widget and toast_widget.winfo_exists():
                    toast_widget.place_configure(x=0)
                return

            start_x = 300
            if toast_widget and toast_widget.winfo_exists():
                toast_widget.place_configure(x=start_x)

            def step(k=0):
                if not (toast_widget and toast_widget.winfo_exists()):
                    return
                x = max(0, start_x - 30 * k)
                toast_widget.place_configure(x=x)
                if x > 0:
                    self.host.after(20, lambda: step(k + 1))

            step()
        except Exception as e:
            print(f"❌ Toast animation error: {e}")

    def _layout(self):
        try:
            gap = 8
            height = 64
            width = 370

            max_visible = self.get_config_value('ui_settings.max_visible_toasts', 5)
            try:
                max_visible = int(max_visible)
            except Exception:
                max_visible = 5

            if len(self._toasts) > max_visible:
                extras = self._toasts[:-max_visible]
                for old in extras:
                    try:
                        if old and old.winfo_exists():
                            old.destroy()
                    except Exception:
                        pass
                self._toasts = self._toasts[-max_visible:]

            for i, t in enumerate(self._toasts):
                if t and t.winfo_exists():
                    t.place(relx=0, rely=0, x=0, y=i * (height + gap), width=width, height=height)
        except Exception as e:
            print(f"❌ Toast layout error: {e}")

    def remove(self, toast_widget):
        try:
            if toast_widget in self._toasts:
                self._toasts.remove(toast_widget)
            if toast_widget and toast_widget.winfo_exists():
                toast_widget.destroy()
            self._layout()
        except Exception as e:
            print(f"❌ Toast removal error: {e}")

class WelcomeScreenUtils:
    """
    🛠️ UTILS MODULE
    Helper functions and utilities for the Welcome Screen
    """

    def __init__(self, parent_screen):
        self.parent = parent_screen

        # Logger (global, RotatingFile)
        self.logger = setup_logger("checker")

        # Toast system (zentraler Manager)
        self.toast_manager = ToastManager(
            host=self.parent,
            get_color=self._safe_color,
            get_font=self._safe_font,
            get_config_value=self.get_config_value,
        )

        # Configuration über zentralen Manager (Defaults: config.json, Overrides: checker_config.json)
        self.config_manager = ConfigManager()
        self.config = {}
        self.config_file = CONFIG_FILE

        # Analytics
        self.analytics_data = {
            'app_starts': 0,
            'uploads_count': 0,
            'customers_created': 0,
            'errors_count': 0,
            'last_activity': None,
            '_unsaved_events': 0,
        }

        # Initialize
        self._load_configuration()
        self._load_analytics()

        try:
            self.logger.info("✅ Utils Module initialized")
        except Exception:
            pass

        # Attach frequently used calendar helpers to host (backward compatibility)
        try:
            for _name in (
                '_weekday_headers_de',
                '_format_month_year_de',
                'format_date_label',
                'get_calendar_view_model',
                'prev_month',
                'next_month',
            ):
                if not hasattr(self.parent, _name):
                    setattr(self.parent, _name, getattr(self, _name))
        except Exception:
            pass

    # ===============================
    # TOAST NOTIFICATION SYSTEM
    # ===============================

    def _safe_color(self, key, default="#333333"):
        """Safe color access with default fallback"""
        try:
            if hasattr(self.parent, 'get_color'):
                return self.parent.get_color(key)
        except Exception:
            pass
        return default

    def _safe_font(self, key, default=("Arial", 12)):
        """Safe font access with default fallback"""
        try:
            if hasattr(self.parent, 'get_font'):
                return self.parent.get_font(key)
        except Exception:
            pass
        return default

    def show_toast(self, message, toast_type="info", duration=3000):
        """Show toast notification (delegiert an ToastManager)"""
        try:
            self.toast_manager.show(message, toast_type, duration)
            try:
                self.logger.info(f"Toast: {toast_type.upper()} - {message}")
            except Exception:
                pass
        except Exception as e:
            print(f"❌ Toast error: {e}")
            try:
                print(f"📢 {toast_type.upper()}: {message}")
            except Exception:
                pass

    def _create_toast_container(self):
        """(Kompatibilität) Delegiert an ToastManager."""
        self.toast_manager._create_container()

    def _create_toast_widget(self, message, toast_type, duration):
        """(Kompatibilität) Delegiert an ToastManager."""
        return self.toast_manager._create_toast_widget(message, toast_type, duration)

    def _animate_toast_in(self, toast_widget):
        """(Kompatibilität) Delegiert an ToastManager."""
        self.toast_manager._animate_in(toast_widget)

    def _layout_toasts(self):
        """(Kompatibilität) Delegiert an ToastManager."""
        self.toast_manager._layout()

    def _remove_toast(self, toast_widget):
        """(Kompatibilität) Delegiert an ToastManager."""
        self.toast_manager.remove(toast_widget)
    

    # ===============================
    # CONFIGURATION MANAGEMENT
    # ===============================

    def _load_configuration(self):
        """⚙️ Load configuration from file"""
        try:
            # Merge: ConfigManager (overrides) + lokale Minimal-Defaults für utils-spezifische Keys
            self.config = self.config_manager._overrides or {}
            if not self.config:
                # Initialisiere mit Defaults dieser Utils (klein, unabhängig vom globalen config.json)
                self.config = self._get_default_configuration()
                self._save_configuration()
            self.logger.info(f"✅ Configuration loaded: {len(self.config)} settings")
        except Exception as e:
            try:
                self.logger.error(f"❌ Configuration load error: {e}")
            except Exception:
                pass
            self.config = self._get_default_configuration()

    def _get_default_configuration(self):
        """⚙️ Get default configuration"""
        return {
            'app_settings': {
                'theme': 'light',
                'auto_save': True,
                'auto_save_interval': 300,  # 5 minutes
                'language': 'de'
            },
            'upload_settings': {
                'max_file_size_mb': 50,
                'allowed_extensions': ['.pdf', '.txt', '.docx', '.xlsx'],
                'auto_validate': True
            },
            'customer_settings': {
                'auto_create_folders': True,
                'recent_customers_limit': 10
            },
            'ui_settings': {
                'toast_duration': 3000,
                'animation_enabled': True,
                'compact_mode': False,
                'max_visible_toasts': 5,
            }
        }

    def _save_configuration(self):
        """💾 Save configuration to file"""
        try:
            # Schreibe ausschließlich über ConfigManager, um zentrale Kapselung zu garantieren
            # Vollständige Überschreibung der Overrides
            self.config_manager._overrides = self.config
            ok = self.config_manager.save()
            if ok:
                self.logger.info("✅ Configuration saved")
            else:
                self.logger.error("❌ Configuration save failed")
        except Exception as e:
            try:
                self.logger.error(f"❌ Configuration save error: {e}")
            except Exception:
                pass

    def get_config_value(self, key_path, default=None):
        """🔑 Get configuration value by key path"""
        try:
            # Erst aus lokalen Utils-Overrides, fallback zu globalem ConfigManager
            keys = key_path.split('.')
            value: Any = self.config
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    value = None
                    break
            if value is None:
                return self.config_manager.get(key_path, default)
            return value
        except Exception:
            return self.config_manager.get(key_path, default)

    def set_config_value(self, key_path, value):
        """🔧 Set configuration value by key path"""
        try:
            keys = key_path.split('.')
            config_ref = self.config
            for key in keys[:-1]:
                if key not in config_ref or not isinstance(config_ref[key], dict):
                    config_ref[key] = {}
                config_ref = config_ref[key]
            config_ref[keys[-1]] = value
            self._save_configuration()
        except Exception as e:
            try:
                self.logger.error(f"❌ Config set error: {e}")
            except Exception:
                pass

    # ===============================
    # ANALYTICS & STATISTICS
    # ===============================

    def _load_analytics(self):
        """📊 Load analytics data"""
        try:
            analytics_file = ANALYTICS_FILE
            if os.path.exists(analytics_file):
                with open(analytics_file, 'r', encoding='utf-8') as f:
                    self.analytics_data = json.load(f)
                # Ensure required keys exist for backward compatibility
                for k, v in {
                    'app_starts': 0,
                    'uploads_count': 0,
                    'customers_created': 0,
                    'errors_count': 0,
                    'last_activity': None,
                    '_unsaved_events': 0,
                }.items():
                    if k not in self.analytics_data:
                        self.analytics_data[k] = v
                try:
                    self.logger.info("✅ Analytics data loaded")
                except Exception:
                    pass
            else:
                self._save_analytics()
                try:
                    self.logger.info("✅ Analytics data initialized")
                except Exception:
                    pass
        except Exception as e:
            try:
                self.logger.error(f"❌ Analytics load error: {e}")
            except Exception:
                pass

    def _save_analytics(self):
        """💾 Save analytics data"""
        try:
            analytics_file = ANALYTICS_FILE
            with open(analytics_file, 'w', encoding='utf-8') as f:
                json.dump(self.analytics_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            try:
                self.logger.error(f"❌ Analytics save error: {e}")
            except Exception:
                pass

    def track_event(self, event_type, data=None):
        """📈 Track analytics event with generic counter and periodic persistence"""
        try:
            # Increase known integer counters only
            if event_type in self.analytics_data and isinstance(self.analytics_data[event_type], int):
                self.analytics_data[event_type] += 1

            # Update activity timestamp
            self.analytics_data['last_activity'] = datetime.now().isoformat()

            # Generic unsaved events counter
            self.analytics_data['_unsaved_events'] = self.analytics_data.get('_unsaved_events', 0) + 1

            # Persist every N events (default 5)
            if self.analytics_data['_unsaved_events'] >= 5:
                self._save_analytics()
                self.analytics_data['_unsaved_events'] = 0

        except Exception as e:
            try:
                self.logger.error(f"❌ Event tracking error: {e}")
            except Exception:
                pass

    def get_analytics_summary(self):
        """📊 Get analytics summary"""
        return {
            'app_usage': {
                'total_starts': self.analytics_data.get('app_starts', 0),
                'total_uploads': self.analytics_data.get('uploads_count', 0),
                'customers_created': self.analytics_data.get('customers_created', 0),
                'errors_logged': self.analytics_data.get('errors_count', 0),
                'last_activity': self.analytics_data.get('last_activity', 'Never')
            }
        }

    # ===============================
    # PUBLIC EN-STYLED ALIASES (non-breaking)
    # ===============================

    # ---- stats_* API ----
    def stats_track_event(self, event_type: str, data: Optional[Dict[str, Any]] = None) -> None:
        """stats: Track an analytics event (alias of track_event)."""
        self.track_event(event_type, data)

    def stats_get_summary(self) -> Dict[str, Dict[str, Any]]:
        """stats: Return aggregated analytics summary (alias of get_analytics_summary)."""
        return self.get_analytics_summary()

    # ---- toast_* API ----
    def toast_show(self, message: str, toast_type: str = "info", duration: Optional[int] = 3000) -> None:
        """toast: Show a toast via central ToastManager (alias of show_toast)."""
        self.show_toast(message, toast_type, duration)

    def toast_clear(self) -> None:
        """toast: Clear all active toasts if manager available."""
        try:
            if getattr(self, 'toast_manager', None):
                self.toast_manager.clear()
        except Exception:
            pass

    # ---- customer_* API ----
    def customer_get_all(self) -> List[Dict[str, Any]]:
        """customer: Liste aller Kunden aus dem Host (Falls vorhanden), sonst leere Liste."""
        try:
            data = getattr(self.parent, 'customers_data', None)
            return list(data) if isinstance(data, list) else []
        except Exception:
            return []

    def customer_get_favorites(self) -> List[Any]:
        """customer: Favoriten-Liste des Hosts, falls vorhanden."""
        try:
            fav = getattr(self.parent, 'favorite_customers', None)
            return list(fav) if isinstance(fav, list) else []
        except Exception:
            return []

    def customer_exists(self, name: str) -> bool:
        """customer: Prüft, ob ein Kunde mit Namen existiert (case-insensitive)."""
        try:
            name_l = (name or '').strip().lower()
            for c in self.customer_get_all():
                if (c.get('name') or '').strip().lower() == name_l:
                    return True
            return False
        except Exception:
            return False

    def customer_base_path(self) -> str:
        """customer: Basis-Pfad der Projekte (vom Host), sonst 'projects'."""
        try:
            return str(getattr(self.parent, 'projects_base_path', 'projects'))
        except Exception:
            return 'projects'

    # ===============================
    # FILE OPERATIONS
    # ===============================

    def get_file_info(self, file_path):
        """📄 Get comprehensive file information"""
        try:
            path_obj = Path(file_path)

            if not path_obj.exists():
                return None

            stat = path_obj.stat()

            return {
                'path': str(file_path),
                'name': path_obj.name,
                'stem': path_obj.stem,
                'suffix': path_obj.suffix,
                'size_bytes': stat.st_size,
                'size_kb': round(stat.st_size / 1024, 2),
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'is_file': path_obj.is_file(),
                'is_dir': path_obj.is_dir()
            }

        except Exception as e:
            try:
                self.logger.error(f"❌ File info error: {e}")
            except Exception:
                pass
            return None

    def format_file_size(self, size_bytes):
        """📐 Format file size in human-readable format"""
        try:
            if size_bytes < 1024:
                return f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.1f} KB"
            elif size_bytes < 1024 * 1024 * 1024:
                return f"{size_bytes / (1024 * 1024):.1f} MB"
            else:
                return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
        except Exception:
            return "Unknown"

    def validate_file_path(self, file_path):
        """✅ Validate file path using config-bound size limit and allowed extensions"""
        try:
            path_obj = Path(file_path)

            exists = path_obj.exists()
            is_file = path_obj.is_file() if exists else False

            # Prepare config values with safe fallbacks
            max_mb = self.get_config_value('upload_settings.max_file_size_mb', 50)
            try:
                max_mb = int(max_mb)
            except Exception:
                max_mb = 50

            allowed = self.get_config_value('upload_settings.allowed_extensions', ['.pdf', '.txt', '.docx', '.xlsx'])
            if not isinstance(allowed, (list, tuple, set)):
                allowed = ['.pdf', '.txt', '.docx', '.xlsx']
            # Normalisieren & auf bekannte Endungen begrenzen (duplikatfrei)
            def _normalize_ext_list(items):
                known = {'.pdf', '.txt', '.docx', '.xlsx', '.doc', '.rtf', '.odt', '.xls', '.pptx', '.ppt'}
                seen = set()
                out = []
                for it in items:
                    s = str(it).strip().lower()
                    if not s:
                        continue
                    if not s.startswith('.'):
                        s = f'.{s}'
                    if s in seen:
                        continue
                    if s in known:
                        seen.add(s)
                        out.append(s)
                return out
            allowed_norm = _normalize_ext_list(list(allowed))
            allowed_set = set(allowed_norm) if allowed_norm else {'.pdf', '.txt', '.docx', '.xlsx'}

            ext = path_obj.suffix.lower() if exists else ''

            # Early return if path invalid
            if not (exists and is_file):
                return {
                    'valid': False,
                    'exists': exists,
                    'is_file': is_file,
                    'readable': False,
                    'size_ok': False,
                    'ext_ok': False,
                    'ext': ext,
                    'limit_mb': max_mb
                }

            size = path_obj.stat().st_size
            readable = os.access(file_path, os.R_OK)
            size_ok = size < (max_mb * 1024 * 1024)
            ext_ok = (ext in allowed_set) if allowed_set else True

            return {
                'valid': readable and size_ok and ext_ok,
                'exists': True,
                'is_file': True,
                'readable': readable,
                'size_ok': size_ok,
                'ext_ok': ext_ok,
                'ext': ext,
                'limit_mb': max_mb
            }

        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }

    # ===============================
    # CALENDAR FUNCTIONS
    # ===============================

    def get_calendar_data(self, year=None, month=None):
        """📅 Get calendar data for given year/month"""
        try:
            if year is None:
                year = datetime.now().year
            if month is None:
                month = datetime.now().month

            # Get calendar matrix
            cal = calendar.monthcalendar(year, month)

            # Get month name
            month_name = calendar.month_name[month]

            return {
                'year': year,
                'month': month,
                'month_name': month_name,
                'calendar_matrix': cal,
                'days_in_month': calendar.monthrange(year, month)[1],
                'first_weekday': calendar.monthrange(year, month)[0]
            }

        except Exception as e:
            print(f"❌ Calendar data error: {e}")
            return None

    # ---- calendar_* API (EN aliases) ----
    def calendar_get_view_model(self, year: Optional[int] = None, month: Optional[int] = None,
                                firstweekday: int = 0, country: str = 'DE',
                                bundesland: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """calendar: Get a UI-friendly calendar view model (alias of get_calendar_view_model).

        Returns a dict with keys: year, month, month_name, weeks[{week_number, days[...]}], weekday_headers.
        """
        return self.get_calendar_view_model(year, month, firstweekday, country, bundesland)

    def get_project_dates(self):
        """📊 Get project dates for calendar integration"""
        try:
            project_dates = {}
            base_path = Path(self.parent.projects_base_path)

            if not base_path.exists():
                return project_dates

            # Scan for project directories
            for customer_dir in base_path.iterdir():
                if customer_dir.is_dir():
                    for project_dir in customer_dir.iterdir():
                        if project_dir.is_dir():
                            # Extract date from project name (if follows naming convention)
                            date_str = self._extract_date_from_project_name(project_dir.name)
                            if date_str:
                                if date_str not in project_dates:
                                    project_dates[date_str] = []

                                project_dates[date_str].append({
                                    'customer': customer_dir.name,
                                    'project': project_dir.name,
                                    'path': str(project_dir)
                                })

            return project_dates

        except Exception as e:
            print(f"❌ Project dates error: {e}")
            return {}

    def _extract_date_from_project_name(self, project_name):
        """📅 Extract date from project name (supports multiple formats)."""
        try:
            # 1) YYYY-MM-DD
            m = re.search(r'(\d{4}-\d{2}-\d{2})', project_name)
            if m:
                datetime.strptime(m.group(1), '%Y-%m-%d')
                return m.group(1).replace('-', '')

            # 2) YYYY_MM_DD
            m = re.search(r'(\d{4}_\d{2}_\d{2})', project_name)
            if m:
                dt = datetime.strptime(m.group(1), '%Y_%m_%d')
                return dt.strftime('%Y%m%d')

            # 3) DD.MM.YYYY (german style)
            m = re.search(r'(\d{2}\.\d{2}\.\d{4})', project_name)
            if m:
                dt = datetime.strptime(m.group(1), '%d.%m.%Y')
                return dt.strftime('%Y%m%d')

            # 4) DD_MM_YYYY
            m = re.search(r'(\d{2}_\d{2}_\d{4})', project_name)
            if m:
                dt = datetime.strptime(m.group(1), '%d_%m_%Y')
                return dt.strftime('%Y%m%d')

            # 5) Fallback: contiguous YYYYMMDD
            m = re.search(r'(\d{8})', project_name)
            if m:
                datetime.strptime(m.group(1), '%Y%m%d')
                return m.group(1)

            return None

        except Exception:
            return None

    # ===============================
    # ENHANCED CALENDAR (DE) HELPERS
    # ===============================

    def _weekday_headers_de(self, firstweekday: int = 0):
        """Gibt deutsche Wochentagskürzel in gewünschter Reihenfolge zurück.
        firstweekday: 0=Mo .. 6=So (wie calendar.Calendar)"""
        try:
            headers = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']
            firstweekday = int(firstweekday) if 0 <= int(firstweekday) <= 6 else 0
            return headers[firstweekday:] + headers[:firstweekday]
        except Exception:
            return ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']

    def _format_month_year_de(self, dt):
        """Formatiert Monat Jahr auf Deutsch, z. B. 'August 2025'."""
        try:
            if isinstance(dt, (datetime, date)):
                y, m = dt.year, dt.month
            else:
                return str(dt)
            months = [
                '', 'Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
                'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'
            ]
            return f"{months[m]} {y}"
        except Exception:
            return ""

    def format_date_label(self, yyyymmdd: str):
        """Gibt 'So, 17.08.2025' zurück (robust ohne locale)."""
        try:
            dt = datetime.strptime(yyyymmdd, '%Y%m%d')
            weekdays = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']
            wd = weekdays[calendar.weekday(dt.year, dt.month, dt.day)]
            return f"{wd}, {dt.day:02d}.{dt.month:02d}.{dt.year}"
        except Exception:
            return yyyymmdd

    def _easter_sunday(self, year: int) -> date:
        """Berechnet Ostersonntag (Gregorian, Anonymous-Algorithmus)."""
        a = year % 19
        b = year // 100
        c = year % 100
        d = b // 4
        e = b % 4
        f = (b + 8) // 25
        g = (b - f + 1) // 3
        h = (19 * a + b - d - g + 15) % 30
        i = c // 4
        k = c % 4
        l = (32 + 2 * e + 2 * i - h - k) % 7
        m = (a + 11 * h + 22 * l) // 451
        month = (h + l - 7 * m + 114) // 31
        day = ((h + l - 7 * m + 114) % 31) + 1
        return date(year, month, day)

    def _get_de_holidays(self, year: int, bundesland: str | None = None):
        """Deutsche Feiertage. Optional: bundeslandspezifische Ergänzungen.
        Rückgabe: {YYYYMMDD: Name}
        bundesland: zwei- bis drei-stelliger Code, z. B. 'BY', 'BW', 'BE', 'NW', 'SN', ...
        """
        try:
            def fmt(d: date):
                return d.strftime('%Y%m%d')

            # Bundesweite und bewegliche
            holidays = {
                fmt(date(year, 1, 1)): "Neujahr",
                fmt(date(year, 5, 1)): "Tag der Arbeit",
                fmt(date(year, 10, 3)): "Tag der Deutschen Einheit",
                fmt(date(year, 12, 25)): "1. Weihnachtstag",
                fmt(date(year, 12, 26)): "2. Weihnachtstag",
            }

            easter = self._easter_sunday(year)
            holidays.update({
                fmt(easter - timedelta(days=2)): "Karfreitag",
                fmt(easter + timedelta(days=1)): "Ostermontag",
                fmt(easter + timedelta(days=39)): "Christi Himmelfahrt",
                fmt(easter + timedelta(days=50)): "Pfingstmontag",
            })

            # Fronleichnam (regional)
            if bundesland and bundesland.upper() in {"BW", "BY", "HE", "NW", "RP", "SL"}:
                holidays[fmt(easter + timedelta(days=60))] = "Fronleichnam"

            # Feste regionale
            bl = (bundesland or "").upper()
            if bl in {"BW", "BY", "ST"}:  # Heilige Drei Könige
                holidays[fmt(date(year, 1, 6))] = "Heilige Drei Könige"
            if bl in {"SL", "BY"}:  # Mariä Himmelfahrt (BY nur in Teilen – hier vereinfacht)
                holidays[fmt(date(year, 8, 15))] = "Mariä Himmelfahrt"
            if bl in {"BW", "BY", "NW", "RP", "SL"}:  # Allerheiligen
                holidays[fmt(date(year, 11, 1))] = "Allerheiligen"
            if bl in {"BB"}:  # Reformationstag ist in BB auch, aber bundesweit in vielen Ländern – unten allgemein
                pass

            # Reformationstag (weit verbreitet regional)
            if bl in {"BB", "MV", "SN", "ST", "TH", "SH", "HB", "NI", "HH"}:
                holidays[fmt(date(year, 10, 31))] = "Reformationstag"

            # Internationaler Frauentag (Berlin, Mecklenburg‑Vorpommern)
            if bl in {"BE", "MV"}:
                holidays[fmt(date(year, 3, 8))] = "Internationaler Frauentag"

            # Buß- und Bettag (Sachsen) – Mittwoch vor dem 23. November
            if bl in {"SN"}:
                # Finde Mittwoch (weekday=2) vor dem 23.11.
                d = date(year, 11, 22)
                while d.weekday() != 2:
                    d -= timedelta(days=1)
                holidays[fmt(d)] = "Buß- und Bettag"

            return holidays
        except Exception:
            return {}

    # ===============================
    # PROJECT INDEX & VIEW-MODEL
    # ===============================

    def index_projects(self, force: bool = False):
        """Erstellt/aktualisiert einen Projekt-Index nach Datum (YYYYMMDD)."""
        try:
            base_path = Path(getattr(self.parent, 'projects_base_path', 'Checker_Projekte'))

            if hasattr(self, '_project_index') and not force:
                return self._project_index

            dates = {}
            if base_path.exists():
                for customer_dir in base_path.iterdir():
                    if not customer_dir.is_dir():
                        continue
                    for project_dir in customer_dir.iterdir():
                        if project_dir.is_dir():
                            ds = self._extract_date_from_project_name(project_dir.name)
                            if not ds:
                                continue
                            dates.setdefault(ds, []).append({
                                'customer': customer_dir.name,
                                'project': project_dir.name,
                                'path': str(project_dir)
                            })
            self._project_index = {'ts': datetime.now().timestamp(), 'dates': dates}
            return self._project_index
        except Exception as e:
            print(f"❌ Project index error: {e}")
            self._project_index = {'ts': datetime.now().timestamp(), 'dates': {}}
            return self._project_index

    def calendar_index_projects(self, force: bool = False) -> Dict[str, Any]:
        """calendar: Build or return cached project index (alias of index_projects)."""
        return self.index_projects(force)

    def get_day_projects(self, yyyymmdd: str):
        """Projekte eines bestimmten Tages (YYYYMMDD)."""
        try:
            idx = self.index_projects()['dates']
            return idx.get(yyyymmdd, [])
        except Exception:
            return []

    def calendar_get_day_projects(self, yyyymmdd: str) -> List[Dict[str, Any]]:
        """calendar: Return project items for a given day (YYYYMMDD)."""
        return self.get_day_projects(yyyymmdd)

    def get_month_projects_summary(self, year: int = None, month: int = None):
        """Aggregiert Projektanzahlen pro Tag für einen Monat."""
        try:
            if year is None or month is None:
                now = datetime.now()
                year = year or now.year
                month = month or now.month
            idx = self.index_projects()['dates']
            counts = {}
            for d, items in idx.items():
                if len(d) == 8 and int(d[:4]) == year and int(d[4:6]) == month:
                    counts[d] = len(items)
            return counts
        except Exception:
            return {}

    # ---- Day details helpers (centralized) ----
    def calendar_get_day_details(self, year: int, month: int, day: int) -> Dict[str, Any]:
        """Liefert Details für einen Tag: Projekte mit Datei-Infos (falls verfügbar) und Summen.

        Hinweise:
        - Nutzt indexierte Projekte. Datei-Counts/Summen werden best-effort berechnet
          (nur wenn Pfade auflösbar sind und Dateien existieren).
        - Konsistenter Rückgabe-Shape für Dialoge/Views.

        Returns dict with keys: date, projects[List], total_files, total_size
        """
        try:
            ds = f"{int(year):04d}{int(month):02d}{int(day):02d}"
            projects = []
            total_files = 0
            total_size = 0
            for it in self.get_day_projects(ds):
                p = dict(it)
                p_path = Path(p.get('path') or '')
                files = []
                p_size = 0
                try:
                    if p_path.exists() and p_path.is_dir():
                        for child in p_path.iterdir():
                            if child.is_file():
                                sz = child.stat().st_size
                                files.append({
                                    'name': child.name,
                                    'path': str(child),
                                    'size': sz,
                                    'modified': child.stat().st_mtime,
                                })
                                p_size += sz
                except Exception:
                    pass
                p['files'] = files
                p['file_count'] = len(files)
                p['total_size'] = p_size
                projects.append(p)
                total_files += len(files)
                total_size += p_size
            return {
                'date': ds,
                'projects': projects,
                'total_files': total_files,
                'total_size': total_size,
            }
        except Exception:
            return {'date': f"{year:04d}{month:02d}{day:02d}", 'projects': [], 'total_files': 0, 'total_size': 0}

    def calendar_get_month_summary(self, year: Optional[int] = None, month: Optional[int] = None) -> Dict[str, int]:
        """calendar: Return counts per day (YYYYMMDD -> count) for the month (alias)."""
        return self.get_month_projects_summary(year, month) or {}

    def get_calendar_view_model(self, year: int = None, month: int = None, firstweekday: int = 0, country: str = 'DE', bundesland: str | None = None):
        """Liefert ein UI‑taugliches View‑Model mit Wochen und Tages-Metadaten."""
        try:
            if year is None or month is None:
                now = datetime.now()
                year = year or now.year
                month = month or now.month

            cal = calendar.Calendar(firstweekday=firstweekday)
            # Konfigurierbares Bundesland (Config > Host-Attribut > Parameter)
            if bundesland is None:
                bundesland = self.get_config_value('calendar_settings.bundesland', getattr(self.parent, 'calendar_bundesland', None))
            holidays = self._get_de_holidays(year, bundesland) if country == 'DE' else {}
            counts = self.get_month_projects_summary(year, month)

            weeks = []
            for week in cal.monthdatescalendar(year, month):
                days = []
                for d in week:
                    ds = d.strftime('%Y%m%d')
                    wd = d.weekday()  # 0=Mo..6=So
                    days.append({
                        'date': ds,
                        'day': d.day,
                        'in_month': d.month == month,
                        'is_today': (d == date.today()),
                        'weekday': wd,
                        'is_weekend': (wd >= 5),
                        'project_count': counts.get(ds, 0),
                        'holiday': holidays.get(ds)
                    })
                week_num = week[0].isocalendar()[1]
                weeks.append({'week_number': week_num, 'days': days})

            return {
                'year': year,
                'month': month,
                'weeks': weeks,
                'month_name': calendar.month_name[month],
                'weekday_headers': self._weekday_headers_de(firstweekday)
            }
        except Exception as e:
            print(f"❌ Calendar view model error: {e}")
            return None

    # ===============================
    # NAVIGATION & UTILITIES
    # ===============================

    def prev_month(self, year: int, month: int):
        """Gibt (year, month) des Vormonats zurück."""
        try:
            if month == 1:
                return (year - 1, 12)
            return (year, month - 1)
        except Exception:
            return (year, month)

    def next_month(self, year: int, month: int):
        """Gibt (year, month) des Folgemonats zurück."""
        try:
            if month == 12:
                return (year + 1, 1)
            return (year, month + 1)
        except Exception:
            return (year, month)

    def calendar_prev_month(self, year: int, month: int) -> Tuple[int, int]:
        """calendar: Previous month (alias of prev_month)."""
        return self.prev_month(year, month)

    def calendar_next_month(self, year: int, month: int) -> Tuple[int, int]:
        """calendar: Next month (alias of next_month)."""
        return self.next_month(year, month)

    def add_months(self, year: int, month: int, delta: int):
        """Verschiebt (year, month) um delta Monate."""
        try:
            total = (year * 12 + (month - 1)) + delta
            y, m0 = divmod(total, 12)
            return (y, m0 + 1)
        except Exception:
            return (year, month)

    def get_week_numbers(self, year: int, month: int, firstweekday: int = 0):
        """Week-Nummern der Kalenderzeilen (ISO) für einen Monat."""
        try:
            cal = calendar.Calendar(firstweekday=firstweekday)
            weeks = cal.monthdatescalendar(year, month)
            return [w[0].isocalendar()[1] for w in weeks]
        except Exception:
            return []

    # ===============================
    # DAY SUMMARY & SEARCH
    # ===============================

    def _group_files_by_type(self, items):
        """Hilfsfunktion: gruppiert Projekt-Items nach Dateityp anhand Projektnamen."""
        result = {'pdf': 0, 'docx': 0, 'txt': 0, 'xlsx': 0, 'other': 0}
        try:
            for it in items or []:
                name = (it.get('project') or '').lower()
                if '.pdf' in name:
                    result['pdf'] += 1
                elif '.docx' in name:
                    result['docx'] += 1
                elif '.txt' in name:
                    result['txt'] += 1
                elif '.xlsx' in name:
                    result['xlsx'] += 1
                else:
                    result['other'] += 1
        except Exception:
            pass
        return result

    def get_day_summary(self, yyyymmdd: str):
        """Aggregierte Infos zu einem Tag: Projekte, Count, Typ-Verteilung, Kundenliste."""
        try:
            items = list(self.get_day_projects(yyyymmdd))
            customers = sorted({it.get('customer') for it in items if it.get('customer')})
            by_type = self._group_files_by_type(items)
            return {
                'date': yyyymmdd,
                'count': len(items),
                'projects': items,
                'customers': customers,
                'by_type': by_type,
            }
        except Exception:
            return {'date': yyyymmdd, 'count': 0, 'projects': [], 'customers': [], 'by_type': {}}

    def calendar_get_day_summary(self, yyyymmdd: str) -> Dict[str, Any]:
        """calendar: Aggregated information for a given day (alias of get_day_summary)."""
        return self.get_day_summary(yyyymmdd)

    def search_projects(self, term: str, case_insensitive: bool = True):
        """Sucht in Projekt-/Kundennamen und liefert Matches + Datumsmenge zum Hervorheben."""
        try:
            if not term:
                return {'dates': set(), 'matches': []}
            needle = term.lower() if case_insensitive else term
            idx = self.index_projects()['dates']
            dates = set()
            matches = []
            for ds, items in idx.items():
                for it in items:
                    text = f"{it.get('customer','')} {it.get('project','')}"
                    hay = text.lower() if case_insensitive else text
                    if needle in hay:
                        dates.add(ds)
                        matches.append({'date': ds, **it})
            return {'dates': dates, 'matches': matches}
        except Exception:
            return {'dates': set(), 'matches': []}

    # ===============================
    # UI HELPER FUNCTIONS
    # ===============================

    def center_window(self, window, width=800, height=600):
        """🎯 Center window on screen"""
        try:
            # Get screen dimensions
            screen_width = window.winfo_screenwidth()
            screen_height = window.winfo_screenheight()

            # Calculate position
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2

            # Set geometry
            window.geometry(f"{width}x{height}+{x}+{y}")

        except Exception as e:
            try:
                self.logger.error(f"❌ Window centering error: {e}")
            except Exception:
                pass

    def create_separator(self, parent, orientation="horizontal"):
        """📏 Create UI separator"""
        try:
            get_color = self._safe_color
            if orientation == "horizontal":
                separator = ctk.CTkFrame(parent,
                                        height=1,
                                        fg_color=get_color('surface_border', '#E5E7EB'))
                separator.pack(fill="x", padx=20, pady=10)
            else:
                separator = ctk.CTkFrame(parent,
                                        width=1,
                                        fg_color=get_color('surface_border', '#E5E7EB'))
                separator.pack(fill="y", padx=10, pady=20)

            return separator

        except Exception as e:
            try:
                self.logger.error(f"❌ Separator creation error: {e}")
            except Exception:
                pass
            return None

    def create_info_card(self, parent, title, content, width=300):
        """📋 Create information card"""
        try:
            get_color = self._safe_color
            get_font = self._safe_font
            card = ctk.CTkFrame(parent,
                               fg_color=get_color('surface', '#FFFFFF'),
                               corner_radius=8,
                               border_width=1,
                               border_color=get_color('surface_border', '#E5E7EB'),
                               width=width)

            # Title
            title_label = ctk.CTkLabel(card,
                                      text=title,
                                      font=ctk.CTkFont(*get_font('heading_md')),
                                      text_color=get_color('gray_700', '#374151'))
            title_label.pack(pady=(16, 8))

            # Content
            content_label = ctk.CTkLabel(card,
                                        text=content,
                                        font=ctk.CTkFont(*get_font('body_md')),
                                        text_color=get_color('gray_500', '#6B7280'),
                                        wraplength=width-40)
            content_label.pack(pady=(0, 16), padx=20)

            return card

        except Exception as e:
            try:
                self.logger.error(f"❌ Info card creation error: {e}")
            except Exception:
                pass
            return None

    # ===============================
    # ERROR HANDLING
    # ===============================

    def handle_error(self, error, context="Unknown"):
        """🚨 Handle and log errors"""
        try:
            error_message = str(error)
            error_traceback = traceback.format_exc()

            # Log error
            try:
                self.logger.error(f"❌ ERROR in {context}: {error_message}\n{error_traceback}")
            except Exception:
                pass

            # Track error in analytics
            self.track_event('errors_count')
            # Persist immediately for critical events
            try:
                self._save_analytics()
            except Exception:
                pass

            # Show user-friendly error message
            self.show_toast(f"Fehler in {context}: {error_message}", "error")

            # Return error info for debugging
            return {
                'error': error_message,
                'context': context,
                'traceback': error_traceback,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            print(f"❌ Error in error handler: {e}")
            return None

    # ===============================
    # CLEANUP FUNCTIONS
    # ===============================

    def cleanup_on_exit(self):
        """🧹 Cleanup when exiting application"""
        try:
            # Save analytics
            self._save_analytics()

            # Save configuration
            self._save_configuration()

            # Clear toast notifications (zentral)
            try:
                self.toast_manager.clear()
            except Exception:
                pass

            try:
                self.logger.info("✅ Utils cleanup completed")
            except Exception:
                pass

        except Exception as e:
            print(f"❌ Cleanup error: {e}")

    # ===============================
    # PUBLIC UTILITY METHODS
    # ===============================

    # ---- Recent Projects I/O (zentral) ----
    def recent_projects_load(self, file_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lädt kürzliche Projekte robust. Nutzt RecentProjectsRepository, falls verfügbar.

        Args:
            file_path: Optionaler Pfad zu einer spezifischen JSON-Datei. Wird ignoriert,
                       wenn ein Repository vorhanden ist und ohne Pfad aufgerufen wird.

        Returns:
            Liste der Projekte (leer bei Fehlern)
        """
        # Repository bevorzugen, wenn vorhanden und kein expliziter Dateipfad gesetzt ist
        try:
            if RecentProjectsRepository and not file_path:
                repo = RecentProjectsRepository()
                items = repo.load()
                try:
                    self.logger.info(f"✅ {len(items)} kürzliche Projekte geladen (Repo)")
                except Exception:
                    pass
                return items
        except Exception:
            # Fallback auf Datei-basiertes Laden
            pass
        try:
            if not file_path:
                return []
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if isinstance(data, list):
                    try:
                        self.logger.info(f"✅ {len(data)} kürzliche Projekte geladen")
                    except Exception:
                        pass
                    return data
            return []
        except Exception as e:
            try:
                self.logger.error(f"⚠️ Fehler beim Laden kürzlicher Projekte: {e}")
            except Exception:
                pass
            return []

    def recent_projects_save(self, file_path: Optional[str], items: List[Dict[str, Any]]) -> bool:
        """Speichert kürzliche Projekte robust. Nutzt Repository, falls vorhanden.

        Args:
            file_path: Optionaler Pfad (nur genutzt, wenn kein Repo vorhanden oder explizit gewünscht)
            items: Zu speichernde Liste
        """
        # Repository bevorzugen, wenn vorhanden und kein expliziter Dateipfad gesetzt ist
        try:
            if RecentProjectsRepository and not file_path:
                repo = RecentProjectsRepository()
                return repo.save(items or [])
        except Exception:
            pass
        try:
            if not file_path:
                return False
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(items or [], f, ensure_ascii=False, indent=4)
            try:
                self.logger.info("✅ Kürzliche Projekte gespeichert")
            except Exception:
                pass
            return True
        except Exception as e:
            try:
                self.logger.error(f"⚠️ Fehler beim Speichern kürzlicher Projekte: {e}")
            except Exception:
                pass
            return False

    def recent_projects_repo_add(self, project: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fügt ein Projekt via Repository hinzu, falls verfügbar; sonst no-op.

        Returns die aktualisierte Liste (Repository) oder eine Liste mit dem einen Eintrag.
        """
        try:
            if RecentProjectsRepository:
                repo = RecentProjectsRepository()
                return repo.add(project)
        except Exception:
            pass
        return [project]

    # ---- Auto-Save Timer Management (zentral) ----
    def auto_save_start(self, callback=None, interval_ms: Optional[int] = None):
        """Startet/neuplant einen Auto-Save Timer über den Host (.after).

        - callback: Callable ohne Parameter (z. B. self.parent._auto_save_data)
        - interval_ms: Override; sonst Config 'app_settings.auto_save_interval' (Sekunden) * 1000
        - Rückgabe: Job-ID (zum Abbrechen)
        """
        try:
            host = getattr(self, 'parent', None)
            if not host or not hasattr(host, 'after'):
                return None
            # existierenden Timer abbrechen
            job_attr = '_auto_save_job'
            try:
                old_job = getattr(self, job_attr, None)
                if old_job:
                    host.after_cancel(old_job)
            except Exception:
                pass
            if interval_ms is None:
                seconds = self.get_config_value('app_settings.auto_save_interval', 300) or 300
                try:
                    seconds = int(seconds)
                except Exception:
                    seconds = 300
                interval_ms = max(1, seconds) * 1000
            # Fallback-Callback: keine Aktion
            if callback is None:
                callback = lambda: None
            job_id = host.after(interval_ms, callback)
            setattr(self, job_attr, job_id)
            try:
                self.logger.info(f"✅ Auto-Save Timer gestartet ({int(interval_ms/1000)}s)")
            except Exception:
                pass
            return job_id
        except Exception as e:
            try:
                self.logger.error(f"⚠️ Auto-Save Timer Fehler: {e}")
            except Exception:
                pass
            return None

    def auto_save_cancel(self):
        """Bricht den Auto-Save Timer ab (falls aktiv)."""
        try:
            host = getattr(self, 'parent', None)
            job_id = getattr(self, '_auto_save_job', None)
            if host and job_id:
                try:
                    host.after_cancel(job_id)
                except Exception:
                    pass
                setattr(self, '_auto_save_job', None)
                try:
                    self.logger.info("✅ Auto-Save Timer gestoppt")
                except Exception:
                    pass
                return True
            return False
        except Exception:
            return False

    # ---- Toast Hide/Cleanup (zentral) ----
    def hide_toast_widget(self, toast_widget, container=None, alpha_step: float = 0.1, delay_ms: int = 50):
        """Versteckt/entfernt einen Toast-Widget sicher mit optionalem Fade-Out.

        - container: Optionaler Container; wird versteckt, wenn leer
        - nutzt Host.after für die Animation
        """
        try:
            host = getattr(self, 'parent', None)
            if not (toast_widget and host and hasattr(host, 'after')):
                # Fallback: direkt zerstören
                try:
                    if toast_widget and toast_widget.winfo_exists():
                        toast_widget.destroy()
                except Exception:
                    pass
                return True

            current_alpha = 1.0

            def _fade():
                nonlocal current_alpha
                try:
                    if not toast_widget or not toast_widget.winfo_exists():
                        return
                    current_alpha -= float(alpha_step)
                    if current_alpha <= 0:
                        try:
                            toast_widget.destroy()
                        except Exception:
                            pass
                        # Container-Cleanup
                        try:
                            cont = container or getattr(self.parent, 'toast_container', None)
                            if cont and cont.winfo_exists():
                                if not cont.winfo_children():
                                    cont.place_forget()
                                    self.parent.update_idletasks()
                        except Exception:
                            pass
                    else:
                        # Optionale Alpha-Anpassung auslassen (CTk-Farben unterstützen keine Alpha)
                        host.after(int(delay_ms), _fade)
                except Exception:
                    # Letzter Fallback: zerstören
                    try:
                        if toast_widget and toast_widget.winfo_exists():
                            toast_widget.destroy()
                    except Exception:
                        pass

            _fade()
            return True
        except Exception:
            return False

    def get_app_info(self):
        """ℹ️ Get application information"""
        return {
            'name': 'Checker Translation Quality Suite',
            'version': '2.0.0',
            'description': 'Professional Translation Quality Management',
            'config_file': self.config_file,
            'has_config': Path(self.config_file).exists(),
            'toast_count': getattr(self.toast_manager, 'count', 0)
        }

    def export_user_data(self, export_path=None):
        """📦 Export user data for backup"""
        try:
            if export_path is None:
                export_path = f"checker_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            export_data = {
                'config': self.config,
                'analytics': self.analytics_data,
                'export_timestamp': datetime.now().isoformat(),
                'app_info': self.get_app_info()
            }

            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            self.show_toast(f"Backup erstellt: {export_path}", "success")
            return export_path

        except Exception as e:
            self.handle_error(e, "Data Export")
            return None

if __name__ == "__main__":
    print("🛠️ Utils Module - Testing not implemented")
    print("    Use as part of WelcomeScreen application")