import os  # Hinzugefügt
import tkinter as tk
# import lite_nuclear_ctk_patch
import customtkinter as ctk
from PIL import Image
from file_operations import resource_path
from tooltip import Tooltip

def create_toolbar(parent, wizard_command, dashboard_command, complete_command, 
                   backup_command, restore_command, feedback_var, feedback_command):
    # Toolbar Frame
    toolbar_frame = ctk.CTkFrame(parent, height=40) # Consistent height

    # Icons (ensure these paths are correct or use your icon loading mechanism)
    # Placeholder icon names, replace with actual icon files if available
    icon_wizard = resource_path("icons/wizard_icon.png") 
    icon_dashboard = resource_path("icons/dashboard_icon.png")
    icon_complete = resource_path("icons/complete_icon.png")
    icon_feedback = resource_path("icons/feedback_icon.png")
    icon_backup = resource_path("icons/backup_icon.png") # New icon
    icon_restore = resource_path("icons/restore_icon.png") # New icon

    # Button styling
    btn_width = 36 
    btn_height = 36
    btn_fg_color = "white"
    # Hover color can be defined here or taken from a theme
    btn_hover_color = "#E0E0E0" # Light gray for hover

    # --- Toolbar Buttons ---
    # Project Wizard Button
    btn_wizard = ctk.CTkButton(toolbar_frame, text="", image=ctk.CTkImage(light_image=Image.open(icon_wizard), dark_image=Image.open(icon_wizard), size=(20,20)), 
                               width=btn_width, height=btn_height, fg_color=btn_fg_color, hover_color=btn_hover_color,
                               command=wizard_command)
    btn_wizard.pack(side=tk.LEFT, padx=3, pady=3)
    Tooltip(btn_wizard, "Projekt-Wizard öffnen")

    # Dashboard Button
    btn_dashboard = ctk.CTkButton(toolbar_frame, text="", image=ctk.CTkImage(light_image=Image.open(icon_dashboard), dark_image=Image.open(icon_dashboard), size=(20,20)), 
                                  width=btn_width, height=btn_height, fg_color=btn_fg_color, hover_color=btn_hover_color,
                                  command=dashboard_command)
    btn_dashboard.pack(side=tk.LEFT, padx=3, pady=3)
    Tooltip(btn_dashboard, "Zum Dashboard wechseln")

    # Mark Project as Completed Button
    btn_complete = ctk.CTkButton(toolbar_frame, text="", image=ctk.CTkImage(light_image=Image.open(icon_complete), dark_image=Image.open(icon_complete), size=(20,20)), 
                                 width=btn_width, height=btn_height, fg_color=btn_fg_color, hover_color=btn_hover_color,
                                 command=complete_command)
    btn_complete.pack(side=tk.LEFT, padx=3, pady=3)
    Tooltip(btn_complete, "Projekt als abgeschlossen markieren")

    # Backup Projects Button
    btn_backup = ctk.CTkButton(toolbar_frame, text="", image=ctk.CTkImage(light_image=Image.open(icon_backup), dark_image=Image.open(icon_backup), size=(20,20)) if os.path.exists(icon_backup) else None,
                               width=btn_width, height=btn_height, fg_color=btn_fg_color, hover_color=btn_hover_color,
                               command=backup_command)
    if not os.path.exists(icon_backup): btn_backup.configure(text="BU") # Fallback text
    btn_backup.pack(side=tk.LEFT, padx=3, pady=3)
    Tooltip(btn_backup, "Projektdaten sichern (Backup)")

    # Restore Projects Button
    btn_restore = ctk.CTkButton(toolbar_frame, text="", image=ctk.CTkImage(light_image=Image.open(icon_restore), dark_image=Image.open(icon_restore), size=(20,20)) if os.path.exists(icon_restore) else None,
                                width=btn_width, height=btn_height, fg_color=btn_fg_color, hover_color=btn_hover_color,
                                command=restore_command)
    if not os.path.exists(icon_restore): btn_restore.configure(text="RE") # Fallback text
    btn_restore.pack(side=tk.LEFT, padx=3, pady=3)
    Tooltip(btn_restore, "Projektdaten aus Backup wiederherstellen")


    # Feedback Mode Toggle Button (Example - on the right)
    # Ensure feedback_icon path is correct
    btn_feedback = ctk.CTkButton(toolbar_frame, text="", image=ctk.CTkImage(light_image=Image.open(icon_feedback), dark_image=Image.open(icon_feedback), size=(20,20)), 
                                 width=btn_width, height=btn_height, fg_color=btn_fg_color, hover_color=btn_hover_color,
                                 command=lambda: feedback_command(feedback_var.get()))
    btn_feedback.pack(side=tk.RIGHT, padx=3, pady=3)
    Tooltip(btn_feedback, "Feedback-Modus umschalten")

    return toolbar_frame
