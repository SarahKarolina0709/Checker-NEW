"""
Notification Center - Modern notification system with better error handling
Extracted from CheckerApp to improve modularity and user experience
"""

import customtkinter as ctk
import logging
from typing import List, Optional


class NotificationCenter:
    """Manages notifications and user feedback"""
    
    def __init__(self, app_instance):
        self.app = app_instance
        self.logger = logging.getLogger("NotificationCenter")
        self.notifications: List[ctk.CTkFrame] = []
        self.notification_container: Optional[ctk.CTkFrame] = None
        self._create_notification_system()
    
    def _create_notification_system(self):
        """Creates a modern notification system"""
        try:
            self.notification_container = ctk.CTkFrame(
                self.app.root,
                fg_color="transparent",
                bg_color="transparent"
            )
            # Initially hide container
            self.notification_container.place_forget()
            
        except Exception as e:
            self.logger.error(f"[NOTIFICATION] Error creating notification system: {e}")
    
    def show_notification(self, message: str, notification_type: str = "info", duration: int = 4000):
        """Shows a modern notification with auto-dismiss"""
        try:
            if not self.notification_container:
                self._create_notification_system()
            
            # Ensure container is visible
            self.notification_container.place(relx=1.0, rely=0.1, anchor="ne", x=-20, y=20)
            
            # Notification colors and icons
            colors = {
                "info": ("#3B82F6", "#60A5FA"),
                "success": ("#10B981", "#34D399"),
                "warning": ("#F59E0B", "#FBBF24"),
                "error": ("#EF4444", "#F87171")
            }
            
            icons = {
                "info": "ℹ️",
                "success": "✅",
                "warning": "⚠️",
                "error": "❌"
            }
            
            bg_color, text_color = colors.get(notification_type, colors["info"])
            icon = icons.get(notification_type, "ℹ️")
            
            # Create notification frame
            notification = ctk.CTkFrame(
                self.notification_container,
                fg_color=bg_color,
                corner_radius=8,
                border_width=1,
                border_color=text_color
            )
            
            # Add notification content
            content_frame = ctk.CTkFrame(notification, fg_color="transparent")
            content_frame.pack(fill="both", expand=True, padx=12, pady=8)
            
            # Icon and message
            message_label = ctk.CTkLabel(
                content_frame,
                text=f"{icon} {message}",
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                text_color="white",
                wraplength=300
            )
            message_label.pack(side="left", fill="both", expand=True)
            
            # Close button
            close_btn = ctk.CTkButton(
                content_frame,
                text="✕",
                width=20,
                height=20,
                corner_radius=10,
                fg_color="transparent",
                hover_color=("#F0F0F0", "#333333"),
                text_color="white",
                font=ctk.CTkFont(family="Segoe UI", size=10),
                command=lambda: self.hide_notification(notification)
            )
            close_btn.pack(side="right", padx=(8, 0))
            
            # Position notification
            y_offset = len(self.notifications) * 70
            notification.place(relx=0, rely=0, anchor="nw", y=y_offset)
            
            # Store notification reference
            self.notifications.append(notification)
            
            # Auto-hide after duration
            self.app.root.after(duration, lambda: self.hide_notification(notification))
            
            # Slide-in animation
            self._animate_notification_slide_in(notification)
            
        except Exception as e:
            self.logger.error(f"[NOTIFICATION] Error showing notification: {e}")
    
    def hide_notification(self, notification: ctk.CTkFrame):
        """Hides a notification with slide-out animation"""
        try:
            if notification in self.notifications:
                self.notifications.remove(notification)
                
                # Slide-out animation
                self._animate_notification_slide_out(notification)
                
                # Reposition remaining notifications
                for i, notif in enumerate(self.notifications):
                    notif.place(relx=0, rely=0, anchor="nw", y=i * 70)
                
                # Hide container if no notifications remain
                if not self.notifications:
                    self.notification_container.place_forget()
                    
        except Exception as e:
            self.logger.debug(f"[NOTIFICATION] Error hiding notification: {e}")
    
    def _animate_notification_slide_in(self, notification: ctk.CTkFrame, x_offset: int = 300):
        """Animates notification slide-in from right"""
        try:
            if x_offset > 0:
                notification.place(relx=1.0, rely=0, anchor="ne", x=x_offset)
                self.app.root.after(10, lambda: self._animate_notification_slide_in(notification, x_offset - 15))
            else:
                notification.place(relx=1.0, rely=0, anchor="ne", x=0)
        except Exception as e:
            pass
    
    def _animate_notification_slide_out(self, notification: ctk.CTkFrame, x_offset: int = 0):
        """Animates notification slide-out to right"""
        try:
            if x_offset < 300:
                notification.place(relx=1.0, rely=0, anchor="ne", x=x_offset)
                self.app.root.after(10, lambda: self._animate_notification_slide_out(notification, x_offset + 15))
            else:
                notification.destroy()
        except Exception as e:
            pass
    
    def clear_all_notifications(self):
        """Clears all notifications"""
        try:
            for notification in self.notifications.copy():
                self.hide_notification(notification)
        except Exception as e:
            self.logger.error(f"[NOTIFICATION] Error clearing notifications: {e}")
    
    def show_error_dialog(self, title: str, message: str, details: Optional[str] = None):
        """Shows a detailed error dialog for critical errors"""
        try:
            from tkinter import messagebox
            
            if details:
                full_message = f"{message}\n\nDetails: {details}"
            else:
                full_message = message
            
            messagebox.showerror(title, full_message)
            
            # Also show as notification for consistency
            self.show_notification(f"Fehler: {message}", "error", 6000)
            
        except Exception as e:
            self.logger.error(f"[NOTIFICATION] Error showing error dialog: {e}")
    
    def show_success_message(self, message: str, duration: int = 3000):
        """Shows a success message"""
        self.show_notification(message, "success", duration)
    
    def show_warning_message(self, message: str, duration: int = 4000):
        """Shows a warning message"""
        self.show_notification(message, "warning", duration)
    
    def show_info_message(self, message: str, duration: int = 3000):
        """Shows an info message"""
        self.show_notification(message, "info", duration)
