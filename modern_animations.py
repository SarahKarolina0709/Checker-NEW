"""
Moderne Animationen für die Checker-App GUI
-----------------------------------------
Smooth transitions, hover effects, und moderne UI-Animationen für eine professionelle Benutzererfahrung.
"""

import tkinter as tk
import customtkinter as ctk
from typing import Callable, Optional, Union
import threading
import time
import math


class ModernAnimations:
    """Klasse für moderne UI-Animationen und Übergangseffekte"""
    
    @staticmethod
    def smooth_scale_animation(widget: ctk.CTkBaseClass, 
                             start_scale: float = 1.0, 
                             end_scale: float = 1.05, 
                             duration: float = 0.2,
                             callback: Optional[Callable] = None):
        """
        Sanfte Skalierungsanimation für Hover-Effekte
        
        Args:
            widget: Das zu animierende Widget
            start_scale: Anfangsskalierung (1.0 = normale Größe)
            end_scale: Endskalierung (1.05 = 5% größer)
            duration: Animationsdauer in Sekunden
            callback: Optional callback nach Animation
        """
        if not hasattr(widget, 'configure'):
            return
            
        def animate():
            try:
                steps = 20
                step_duration = duration / steps
                scale_diff = end_scale - start_scale
                
                for i in range(steps + 1):
                    progress = i / steps
                    # Easing function für sanfte Animation
                    eased_progress = 1 - math.cos(progress * math.pi / 2)
                    current_scale = start_scale + (scale_diff * eased_progress)
                    
                    # Widget-Skalierung anwenden (falls unterstützt)
                    if hasattr(widget, '_apply_widget_scaling'):
                        widget._apply_widget_scaling(current_scale)
                    
                    time.sleep(step_duration)
                
                if callback:
                    callback()
                    
            except Exception as e:
                print(f"Animation error: {e}")
        
        animation_thread = threading.Thread(target=animate, daemon=True)
        animation_thread.start()
    
    @staticmethod
    def color_fade_animation(widget: ctk.CTkBaseClass,
                           start_color: str,
                           end_color: str,
                           duration: float = 0.3,
                           property_name: str = 'fg_color'):
        """
        Sanfte Farbübergangsanimation
        
        Args:
            widget: Das zu animierende Widget
            start_color: Startfarbe (Hex)
            end_color: Endfarbe (Hex)
            duration: Animationsdauer
            property_name: CSS-Property zu animieren ('fg_color', 'text_color', etc.)
        """
        def hex_to_rgb(hex_color: str) -> tuple:
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        def rgb_to_hex(rgb: tuple) -> str:
            return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
        
        def animate():
            try:
                start_rgb = hex_to_rgb(start_color)
                end_rgb = hex_to_rgb(end_color)
                
                steps = 25
                step_duration = duration / steps
                
                for i in range(steps + 1):
                    progress = i / steps
                    # Easing für sanften Übergang
                    eased_progress = 1 - math.cos(progress * math.pi / 2)
                    
                    current_rgb = tuple(
                        int(start_rgb[j] + (end_rgb[j] - start_rgb[j]) * eased_progress)
                        for j in range(3)
                    )
                    
                    current_color = rgb_to_hex(current_rgb)
                    
                    # Color anwenden
                    widget.after(0, lambda c=current_color: widget.configure(**{property_name: c}))
                    
                    time.sleep(step_duration)
                    
            except Exception as e:
                print(f"Color animation error: {e}")
        
        animation_thread = threading.Thread(target=animate, daemon=True)
        animation_thread.start()
    
    @staticmethod
    def slide_in_animation(widget: ctk.CTkBaseClass,
                          direction: str = 'left',
                          duration: float = 0.4,
                          distance: int = 50):
        """
        Slide-in Animation für neue Elemente
        
        Args:
            widget: Das zu animierende Widget
            direction: Richtung ('left', 'right', 'top', 'bottom')
            duration: Animationsdauer
            distance: Slide-Distanz in Pixeln
        """
        def animate():
            try:
                steps = 30
                step_duration = duration / steps
                
                # Ursprungsposition ermitteln
                original_x = widget.winfo_x()
                original_y = widget.winfo_y()
                
                # Startposition basierend auf Richtung
                if direction == 'left':
                    start_x, start_y = original_x - distance, original_y
                elif direction == 'right':
                    start_x, start_y = original_x + distance, original_y
                elif direction == 'top':
                    start_x, start_y = original_x, original_y - distance
                else:  # bottom
                    start_x, start_y = original_x, original_y + distance
                
                for i in range(steps + 1):
                    progress = i / steps
                    # Easing function
                    eased_progress = 1 - math.pow(1 - progress, 3)
                    
                    current_x = start_x + (original_x - start_x) * eased_progress
                    current_y = start_y + (original_y - start_y) * eased_progress
                    
                    widget.after(0, lambda x=current_x, y=current_y: widget.place(x=x, y=y))
                    
                    time.sleep(step_duration)
                    
            except Exception as e:
                print(f"Slide animation error: {e}")
        
        animation_thread = threading.Thread(target=animate, daemon=True)
        animation_thread.start()
    
    @staticmethod
    def pulse_animation(widget: ctk.CTkBaseClass,
                       pulse_color: str,
                       original_color: str,
                       pulses: int = 2,
                       duration: float = 0.8):
        """
        Pulsierungseffekt für Aufmerksamkeit (z.B. bei Fehlern oder Erfolg)
        
        Args:
            widget: Das zu animierende Widget
            pulse_color: Farbe während des Pulses
            original_color: Ursprungsfarbe
            pulses: Anzahl der Pulse
            duration: Gesamtdauer
        """
        def animate():
            try:
                pulse_duration = duration / (pulses * 2)  # Hin und zurück
                
                for _ in range(pulses):
                    # Zu Pulse-Farbe
                    ModernAnimations.color_fade_animation(
                        widget, original_color, pulse_color, pulse_duration
                    )
                    time.sleep(pulse_duration)
                    
                    # Zurück zur ursprünglichen Farbe
                    ModernAnimations.color_fade_animation(
                        widget, pulse_color, original_color, pulse_duration
                    )
                    time.sleep(pulse_duration)
                    
            except Exception as e:
                print(f"Pulse animation error: {e}")
        
        animation_thread = threading.Thread(target=animate, daemon=True)
        animation_thread.start()
    
    @staticmethod
    def fade_in_animation(widget: ctk.CTkBaseClass, duration: float = 0.5, delay: float = 0.0):
        """
        Fade-In Animation für sanfte Widget-Einblendung
        """
        def animate():
            time.sleep(delay)
            try:
                steps = 30
                step_duration = duration / steps
                
                # Startwerte setzen
                widget.configure(state="disabled")
                
                for i in range(steps + 1):
                    progress = i / steps
                    alpha = progress
                    
                    # Simuliere Fade durch Farbintensität
                    if hasattr(widget, 'configure') and 'text_color' in widget.keys():
                        base_color = "#212529"
                        # Berechne Transparenz durch Farbmischung
                        alpha_hex = int(255 * alpha)
                        fade_color = f"#{alpha_hex:02x}{alpha_hex:02x}{alpha_hex:02x}"
                        widget.configure(text_color=fade_color)
                    
                    time.sleep(step_duration)
                
                widget.configure(state="normal")
                
            except Exception as e:
                print(f"Fade-in animation error: {e}")
        
        threading.Thread(target=animate, daemon=True).start()
    
    @staticmethod
    def slide_in_from_bottom(widget: ctk.CTkBaseClass, distance: int = 30, duration: float = 0.4):
        """
        Slide-In Animation von unten für neue Elemente
        """
        def animate():
            try:
                steps = 25
                step_duration = duration / steps
                step_distance = distance / steps
                
                # Simuliere Slide durch Padding-Änderung
                original_pady = widget.cget("pady") if "pady" in widget.keys() else 0
                
                for i in range(steps + 1):
                    progress = i / steps
                    # Easing out
                    eased_progress = 1 - (1 - progress) ** 3
                    current_offset = distance - (distance * eased_progress)
                    
                    if hasattr(widget, 'configure') and "pady" in widget.keys():
                        widget.configure(pady=(original_pady + int(current_offset), original_pady))
                    
                    time.sleep(step_duration)
                
            except Exception as e:
                print(f"Slide-in animation error: {e}")
        
        threading.Thread(target=animate, daemon=True).start()
    
    @staticmethod
    def pulse_attention(widget: ctk.CTkBaseClass, 
                       highlight_color: str = "#4FC3F7", 
                       cycles: int = 3, 
                       duration: float = 0.8):
        """
        Pulsierender Aufmerksamkeitseffekt für wichtige Elemente
        """
        def animate():
            try:
                original_color = widget.cget("fg_color") if "fg_color" in widget.keys() else "#FFFFFF"
                steps_per_cycle = 15
                cycle_duration = duration / cycles
                step_duration = cycle_duration / (steps_per_cycle * 2)
                
                for cycle in range(cycles):
                    # Pulse up
                    for i in range(steps_per_cycle):
                        progress = i / steps_per_cycle
                        # Smooth easing
                        alpha = math.sin(progress * math.pi / 2)
                        
                        if hasattr(widget, 'configure') and "fg_color" in widget.keys():
                            # Mische Farben für Pulse-Effekt
                            mixed_color = ModernAnimations._interpolate_colors(original_color, highlight_color, alpha)
                            widget.configure(fg_color=mixed_color)
                        
                        time.sleep(step_duration)
                    
                    # Pulse down
                    for i in range(steps_per_cycle):
                        progress = i / steps_per_cycle
                        alpha = 1 - math.sin(progress * math.pi / 2)
                        
                        if hasattr(widget, 'configure') and "fg_color" in widget.keys():
                            mixed_color = ModernAnimations._interpolate_colors(original_color, highlight_color, alpha)
                            widget.configure(fg_color=mixed_color)
                        
                        time.sleep(step_duration)
                
                # Zurück zur ursprünglichen Farbe
                if hasattr(widget, 'configure') and "fg_color" in widget.keys():
                    widget.configure(fg_color=original_color)
                    
            except Exception as e:
                print(f"Pulse animation error: {e}")
        
        threading.Thread(target=animate, daemon=True).start()
    
    @staticmethod
    def shake_animation(widget: ctk.CTkBaseClass, intensity: int = 5, duration: float = 0.5):
        """
        Shake-Animation für Fehler-Feedback
        """
        def animate():
            try:
                steps = 20
                step_duration = duration / steps
                
                for i in range(steps):
                    # Sinuswelle für Shake-Effekt
                    offset = math.sin(i * math.pi / 3) * intensity * (1 - i / steps)
                    
                    # Simuliere Shake durch Padding-Änderung
                    if hasattr(widget, 'configure') and "padx" in widget.keys():
                        original_padx = widget.cget("padx") if hasattr(widget, 'cget') else 0
                        widget.configure(padx=(original_padx + int(offset), original_padx))
                    
                    time.sleep(step_duration)
                
                # Zurück zur normalen Position
                if hasattr(widget, 'configure') and "padx" in widget.keys():
                    widget.configure(padx=original_padx)
                    
            except Exception as e:
                print(f"Shake animation error: {e}")
        
        threading.Thread(target=animate, daemon=True).start()
    
    @staticmethod
    def _interpolate_colors(color1: str, color2: str, factor: float) -> str:
        """
        Interpoliert zwischen zwei Hex-Farben
        """
        try:
            # Konvertiere Hex zu RGB
            def hex_to_rgb(hex_color):
                hex_color = hex_color.lstrip('#')
                return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            
            def rgb_to_hex(rgb):
                return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
            
            rgb1 = hex_to_rgb(color1)
            rgb2 = hex_to_rgb(color2)
            
            # Interpolation
            rgb_result = tuple(
                int(rgb1[i] + (rgb2[i] - rgb1[i]) * factor)
                for i in range(3)
            )
            
            return rgb_to_hex(rgb_result)
        except:
            return color1  # Fallback zur ersten Farbe


class ModernHoverEffects:
    """Moderne Hover-Effekte für UI-Komponenten"""
    
    @staticmethod
    def apply_button_hover(button: ctk.CTkButton,
                          hover_color: str = "#0056b3",
                          original_color: str = "#0078D7",
                          scale_effect: bool = True):
        """
        Erweiterte Hover-Effekte für Buttons
        
        Args:
            button: Der Button
            hover_color: Farbe beim Hover
            original_color: Originalfarbe
            scale_effect: Ob Skalierungseffekt angewendet werden soll
        """
        def on_enter(event):
            ModernAnimations.color_fade_animation(
                button, original_color, hover_color, 0.2, 'fg_color'
            )
            if scale_effect:
                ModernAnimations.smooth_scale_animation(button, 1.0, 1.02, 0.2)
        
        def on_leave(event):
            ModernAnimations.color_fade_animation(
                button, hover_color, original_color, 0.2, 'fg_color'
            )
            if scale_effect:
                ModernAnimations.smooth_scale_animation(button, 1.02, 1.0, 0.2)
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
    
    @staticmethod
    def apply_card_hover(frame: ctk.CTkFrame,
                        hover_color: str = "#F0F8FF",
                        original_color: str = "#FFFFFF",
                        shadow_effect: bool = True):
        """
        Hover-Effekt für Card-artige Frames
        
        Args:
            frame: Das Frame-Widget
            hover_color: Hover-Hintergrundfarbe
            original_color: Original-Hintergrundfarbe
            shadow_effect: Ob Schatten-Effekt simuliert werden soll
        """
        def on_enter(event):
            ModernAnimations.color_fade_animation(
                frame, original_color, hover_color, 0.25, 'fg_color'
            )
            if shadow_effect:
                # Simulierter Schatten durch leichte Größenanpassung
                ModernAnimations.smooth_scale_animation(frame, 1.0, 1.005, 0.25)
        
        def on_leave(event):
            ModernAnimations.color_fade_animation(
                frame, hover_color, original_color, 0.25, 'fg_color'
            )
            if shadow_effect:
                ModernAnimations.smooth_scale_animation(frame, 1.005, 1.0, 0.25)
        
        frame.bind("<Enter>", on_enter)
        frame.bind("<Leave>", on_leave)


class LoadingAnimations:
    """Moderne Loading-Animationen"""
    
    @staticmethod
    def create_spinner(parent: ctk.CTkFrame, size: int = 30) -> ctk.CTkLabel:
        """
        Erstellt einen modernen Spinner für Loading-States
        
        Args:
            parent: Parent-Widget
            size: Größe des Spinners
            
        Returns:
            CTkLabel mit Spinner-Animation
        """
        spinner_label = ctk.CTkLabel(
            parent,
            text="⟳",
            font=ctk.CTkFont(size=size),
            text_color="#0078D7"
        )
        
        def rotate_spinner():
            """Rotiert den Spinner kontinuierlich"""
            rotation_chars = ["⟳", "⟲", "⟳", "⟲"]
            char_index = 0
            
            def update():
                nonlocal char_index
                if spinner_label.winfo_exists():
                    spinner_label.configure(text=rotation_chars[char_index])
                    char_index = (char_index + 1) % len(rotation_chars)
                    spinner_label.after(200, update)
            
            update()
        
        rotate_spinner()
        return spinner_label
    
    @staticmethod
    def create_progress_dots(parent: ctk.CTkFrame) -> ctk.CTkLabel:
        """
        Erstellt animierte Fortschrittspunkte (...)
        
        Args:
            parent: Parent-Widget
            
        Returns:
            CTkLabel mit Punkt-Animation
        """
        dots_label = ctk.CTkLabel(
            parent,
            text="",
            font=ctk.CTkFont(size=16),
            text_color="#6C757D"
        )
        
        def animate_dots():
            """Animiert die Fortschrittspunkte"""
            dots_states = ["", ".", "..", "..."]
            state_index = 0
            
            def update():
                nonlocal state_index
                if dots_label.winfo_exists():
                    dots_label.configure(text=dots_states[state_index])
                    state_index = (state_index + 1) % len(dots_states)
                    dots_label.after(500, update)
            
            update()
        
        animate_dots()
        return dots_label
