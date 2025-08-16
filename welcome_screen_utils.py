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
from datetime import datetime
from pathlib import Path
import json
import os
import traceback
import calendar
import customtkinter as ctk

class WelcomeScreenUtils:
    """
    🛠️ UTILS MODULE
    Helper functions and utilities for the Welcome Screen
    """

    def __init__(self, parent_screen):
        self.parent = parent_screen

        # Toast system
        self.toast_notifications = []
        self.toast_container = None
        self.toast_counter = 0

        # Configuration
        self.config = {}
        self.config_file = "checker_config.json"

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

        print("✅ Utils Module initialized")

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
        """Show toast notification (design-system styled)"""
        try:
            if not self.toast_container:
                self._create_toast_container()

            # Respect configured default duration if not provided
            if duration is None or duration <= 0:
                duration = int(self.get_config_value('ui_settings.toast_duration', 3000) or 3000)

            # Create toast widget (handles list management + layout)
            toast = self._create_toast_widget(message, toast_type, duration)

            # Auto-remove after duration
            self.parent.after(duration, lambda: self._remove_toast(toast))

            print(f"Toast: {toast_type.upper()} - {message}")

        except Exception as e:
            print(f"❌ Toast error: {e}")
            # Fallback to console
            print(f"📢 {toast_type.upper()}: {message}")

    def _create_toast_container(self):
        """Create toast container (top-right)"""
        try:
            # Create toast container at top-right of parent
            self.toast_container = ctk.CTkFrame(self.parent,
                                               fg_color="transparent",
                                               corner_radius=0,
                                               width=370)

            # Position at top-right
            self.toast_container.place(relx=1.0, rely=0.0, anchor="ne", x=-20, y=80)

        except Exception as e:
            print(f"❌ Toast container error: {e}")

    def _create_toast_widget(self, message, toast_type, duration):
        """Create individual toast widget (card with accent bar) using place layout"""
        try:
            # Semantic accent color
            accent_map = {
                'info': self._safe_color('info'),
                'success': self._safe_color('success'),
                'warning': self._safe_color('warning'),
                'error': self._safe_color('error')
            }
            accent = accent_map.get(toast_type, self._safe_color('info'))

            # Colors
            bg_color = self._safe_color('surface_elevated', '#FFFFFF')
            text_primary = self._safe_color('gray_700', '#374151')
            text_secondary = self._safe_color('gray_500', '#6B7280')

            # Toast frame (card) managed via place inside toast_container
            toast_frame = ctk.CTkFrame(
                self.toast_container,
                fg_color=bg_color,
                corner_radius=8,
                border_width=1,
                border_color=self._safe_color('surface_border', '#E5E7EB')
            )

            # Left accent
            accent_bar = ctk.CTkFrame(toast_frame, fg_color=accent, width=5, corner_radius=8)
            accent_bar.pack(side="left", fill="y")

            # Content
            content_frame = ctk.CTkFrame(toast_frame, fg_color="transparent")
            content_frame.pack(side="left", fill="both", expand=True, padx=12, pady=10)

            # Message text
            message_label = ctk.CTkLabel(
                content_frame,
                text=message,
                font=ctk.CTkFont(*self._safe_font('body_sm')),
                text_color=text_primary,
                wraplength=260,
                anchor="w",
                justify="left"
            )
            message_label.pack(side="left", fill="both", expand=True)

            # Close as text-only button
            close_btn = ctk.CTkButton(
                content_frame,
                text="Schließen",
                command=lambda: self._remove_toast(toast_frame),
                font=ctk.CTkFont(*self._safe_font('button_sm')),
                fg_color="transparent",
                text_color=text_secondary,
                hover_color=self._safe_color('surface_hover', '#F3F4F6'),
                height=24,
                width=80,
                corner_radius=6,
            )
            close_btn.pack(side="right", padx=(8, 0))

            # Manage list and layout/animation
            self.toast_notifications.append(toast_frame)
            self._layout_toasts()
            self._animate_toast_in(toast_frame)

            return toast_frame

        except Exception as e:
            print(f"❌ Toast widget error: {e}")
            return None

    def _animate_toast_in(self, toast_widget):
        """Animate toast slide-in from the right using place x offset"""
        try:
            start_x = 300
            if toast_widget and toast_widget.winfo_exists():
                toast_widget.place_configure(x=start_x)

            def step(k=0):
                if not (toast_widget and toast_widget.winfo_exists()):
                    return
                x = max(0, start_x - 30 * k)
                toast_widget.place_configure(x=x)
                if x > 0:
                    self.parent.after(20, lambda: step(k + 1))

            step()

        except Exception as e:
            print(f"❌ Toast animation error: {e}")

    def _layout_toasts(self):
        """Place all active toasts in a vertical stack with uniform size and gap"""
        try:
            gap = 8
            height = 64
            width = 370

            # Clamp visible toasts (configurable, default 5)
            max_visible = self.get_config_value('ui_settings.max_visible_toasts', 5)
            try:
                max_visible = int(max_visible)
            except Exception:
                max_visible = 5

            # Remove oldest if exceeding max visible
            if len(self.toast_notifications) > max_visible:
                extras = self.toast_notifications[:-max_visible]
                for old in extras:
                    try:
                        if old and old.winfo_exists():
                            old.destroy()
                    except Exception:
                        pass
                self.toast_notifications = self.toast_notifications[-max_visible:]

            for i, t in enumerate(self.toast_notifications):
                if t and t.winfo_exists():
                    t.place(relx=0, rely=0, x=0, y=i * (height + gap), width=width, height=height)
        except Exception as e:
            print(f"❌ Toast layout error: {e}")

    def _remove_toast(self, toast_widget):
        """Remove toast notification"""
        try:
            if toast_widget in self.toast_notifications:
                self.toast_notifications.remove(toast_widget)

            if toast_widget and toast_widget.winfo_exists():
                toast_widget.destroy()

            # Re-layout remaining toasts
            self._layout_toasts()

        except Exception as e:
            print(f"❌ Toast removal error: {e}")
    

    # ===============================
    # CONFIGURATION MANAGEMENT
    # ===============================

    def _load_configuration(self):
        """⚙️ Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                print(f"✅ Configuration loaded: {len(self.config)} settings")
            else:
                self.config = self._get_default_configuration()
                self._save_configuration()
                print("✅ Default configuration created")
        except Exception as e:
            print(f"❌ Configuration load error: {e}")
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
                'compact_mode': False
            }
        }

    def _save_configuration(self):
        """💾 Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print("✅ Configuration saved")
        except Exception as e:
            print(f"❌ Configuration save error: {e}")

    def get_config_value(self, key_path, default=None):
        """🔑 Get configuration value by key path"""
        try:
            keys = key_path.split('.')
            value = self.config

            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return default

            return value
        except Exception:
            return default

    def set_config_value(self, key_path, value):
        """🔧 Set configuration value by key path"""
        try:
            keys = key_path.split('.')
            config_ref = self.config

            # Navigate to parent
            for key in keys[:-1]:
                if key not in config_ref:
                    config_ref[key] = {}
                config_ref = config_ref[key]

            # Set value
            config_ref[keys[-1]] = value

            # Save configuration
            self._save_configuration()

        except Exception as e:
            print(f"❌ Config set error: {e}")

    # ===============================
    # ANALYTICS & STATISTICS
    # ===============================

    def _load_analytics(self):
        """📊 Load analytics data"""
        try:
            analytics_file = "analytics.json"
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
                print("✅ Analytics data loaded")
            else:
                self._save_analytics()
                print("✅ Analytics data initialized")
        except Exception as e:
            print(f"❌ Analytics load error: {e}")

    def _save_analytics(self):
        """💾 Save analytics data"""
        try:
            analytics_file = "analytics.json"
            with open(analytics_file, 'w', encoding='utf-8') as f:
                json.dump(self.analytics_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Analytics save error: {e}")

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
            print(f"❌ Event tracking error: {e}")

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
            print(f"❌ File info error: {e}")
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
            allowed_set = {str(ext).lower() for ext in allowed}

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
        """📅 Extract date from project name"""
        try:
            import re
            # 1) YYYY-MM-DD -> normalize to YYYYMMDD
            m = re.search(r'(\d{4}-\d{2}-\d{2})', project_name)
            if m:
                datetime.strptime(m.group(1), '%Y-%m-%d')
                return m.group(1).replace('-', '')

            # 2) YYYY_MM_DD -> normalize via strptime
            m = re.search(r'(\d{4}_\d{2}_\d{2})', project_name)
            if m:
                dt = datetime.strptime(m.group(1), '%Y_%m_%d')
                return dt.strftime('%Y%m%d')

            # 3) Fallback: contiguous YYYYMMDD
            m = re.search(r'(\d{8})', project_name)
            if m:
                datetime.strptime(m.group(1), '%Y%m%d')
                return m.group(1)

            return None

        except Exception:
            return None

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
            print(f"❌ Window centering error: {e}")

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
            print(f"❌ Separator creation error: {e}")
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
            print(f"❌ Info card creation error: {e}")
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
            print(f"❌ ERROR in {context}: {error_message}")
            print(f"   Traceback: {error_traceback}")

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

            # Clear toast notifications
            self.toast_notifications.clear()

            print("✅ Utils cleanup completed")

        except Exception as e:
            print(f"❌ Cleanup error: {e}")

    # ===============================
    # PUBLIC UTILITY METHODS
    # ===============================

    def get_app_info(self):
        """ℹ️ Get application information"""
        return {
            'name': 'Checker Translation Quality Suite',
            'version': '2.0.0',
            'description': 'Professional Translation Quality Management',
            'config_file': self.config_file,
            'has_config': Path(self.config_file).exists(),
            'toast_count': len(self.toast_notifications)
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