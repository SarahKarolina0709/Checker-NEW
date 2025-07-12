"""
Erweiterte visuelle Effekte für die Checker-App GUI
--------------------------------------------------
Moderne Glasmorphismus-Effekte, Farbverläufe und erweiterte Animationen
für eine noch professionellere Benutzeroberfläche.
"""

import tkinter as tk
import customtkinter as ctk
from typing import List, Tuple, Optional, Callable
import threading
import time
import math
import colorsys
from PIL import Image, ImageTk, ImageDraw, ImageFilter
import os

from ui_theme import UITheme
from modern_animations import ModernAnimations


class GlassmorphismEffect:
    """
    Glasmorphismus-Effekte für moderne UI-Komponenten
    """
    
    @staticmethod
    def apply_glass_effect(widget: ctk.CTkFrame, 
                          blur_radius: int = 10,
                          opacity: float = 0.7,
                          background_color: str = "#FFFFFF"):
        """
        Wendet einen Glasmorphismus-Effekt auf ein Widget an
        
        Args:
            widget: Das Widget, auf das der Effekt angewendet wird
            blur_radius: Blur-Radius für den Glaseffekt
            opacity: Transparenz (0.0 - 1.0)
            background_color: Hintergrundfarbe
        """
        try:
            # Simuliere Glaseffekt durch mehrschichtige Transparenz
            glass_color = GlassmorphismEffect._adjust_color_opacity(
                background_color, opacity
            )
            
            widget.configure(
                fg_color=glass_color,
                border_width=1,
                border_color=UITheme.COLOR_BORDER + "80"  # Semi-transparent border
            )
            
            # Füge subtilen Schatten hinzu
            GlassmorphismEffect._add_shadow_effect(widget)
            
        except Exception as e:
            print(f"Glasmorphismus-Effekt Fehler: {e}")
    
    @staticmethod
    def _adjust_color_opacity(color: str, opacity: float) -> str:
        """
        Passt die Transparenz einer Farbe an
        """
        try:
            # Konvertiere Hex zu RGB
            color = color.lstrip('#')
            r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
            
            # Simuliere Transparenz durch Farbmischung mit Weiß
            white_factor = 1 - opacity
            r = int(r * opacity + 255 * white_factor)
            g = int(g * opacity + 255 * white_factor)
            b = int(b * opacity + 255 * white_factor)
            
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return color
    
    @staticmethod
    def _add_shadow_effect(widget: ctk.CTkFrame):
        """
        Fügt einen subtilen Schatten-Effekt hinzu
        """
        try:
            # Simuliere Schatten durch einen dunklen Rahmen
            shadow_color = UITheme.COLOR_SHADOW_LIGHT
            
            # Erstelle ein Shadow-Frame hinter dem Widget
            parent = widget.master
            shadow_frame = ctk.CTkFrame(
                parent,
                fg_color=shadow_color,
                corner_radius=widget.cget("corner_radius"),
                width=widget.cget("width") + 4,
                height=widget.cget("height") + 4
            )
            
            # Positioniere Shadow-Frame hinter dem Widget
            shadow_frame.place(
                x=widget.winfo_x() + 2,
                y=widget.winfo_y() + 2
            )
            
            # Widget nach vorne bringen
            widget.lift()
            
        except Exception as e:
            print(f"Schatten-Effekt Fehler: {e}")


class GradientEffects:
    """
    Farbverlauf-Effekte für moderne UI-Komponenten
    """
    
    @staticmethod
    def create_gradient_frame(parent, 
                            colors: List[str], 
                            width: int = 300, 
                            height: int = 200,
                            direction: str = "horizontal") -> ctk.CTkFrame:
        """
        Erstellt einen Frame mit Farbverlauf-Hintergrund
        
        Args:
            parent: Parent-Widget
            colors: Liste von Farben für den Verlauf
            width: Breite des Frames
            height: Höhe des Frames
            direction: Richtung des Verlaufs ("horizontal", "vertical", "diagonal")
        
        Returns:
            CTkFrame mit Farbverlauf
        """
        try:
            # Erstelle Gradient-Image
            gradient_image = GradientEffects._create_gradient_image(
                colors, width, height, direction
            )
            
            # Konvertiere zu CTkImage
            gradient_ctk_image = ctk.CTkImage(
                light_image=gradient_image,
                dark_image=gradient_image,
                size=(width, height)
            )
            
            # Erstelle Frame mit Gradient-Hintergrund
            gradient_frame = ctk.CTkFrame(
                parent,
                width=width,
                height=height,
                fg_color="transparent"
            )
            
            # Füge Gradient als Label hinzu
            gradient_label = ctk.CTkLabel(
                gradient_frame,
                image=gradient_ctk_image,
                text=""
            )
            gradient_label.place(x=0, y=0, relwidth=1, relheight=1)
            
            return gradient_frame
            
        except Exception as e:
            print(f"Gradient-Frame Fehler: {e}")
            # Fallback: Normaler Frame
            return ctk.CTkFrame(parent, width=width, height=height)
    
    @staticmethod
    def _create_gradient_image(colors: List[str], 
                             width: int, 
                             height: int, 
                             direction: str) -> Image.Image:
        """
        Erstellt ein Gradient-Image
        """
        try:
            # Erstelle neues Image
            image = Image.new('RGB', (width, height))
            draw = ImageDraw.Draw(image)
            
            # Konvertiere Farben zu RGB
            rgb_colors = [GradientEffects._hex_to_rgb(color) for color in colors]
            
            if direction == "horizontal":
                for x in range(width):
                    progress = x / (width - 1)
                    color = GradientEffects._interpolate_colors(rgb_colors, progress)
                    draw.line([(x, 0), (x, height)], fill=color)
            
            elif direction == "vertical":
                for y in range(height):
                    progress = y / (height - 1)
                    color = GradientEffects._interpolate_colors(rgb_colors, progress)
                    draw.line([(0, y), (width, y)], fill=color)
            
            elif direction == "diagonal":
                for x in range(width):
                    for y in range(height):
                        progress = (x + y) / (width + height - 2)
                        color = GradientEffects._interpolate_colors(rgb_colors, progress)
                        draw.point((x, y), fill=color)
            
            return image
            
        except Exception as e:
            print(f"Gradient-Image Fehler: {e}")
            # Fallback: Einfarbiges Image
            return Image.new('RGB', (width, height), colors[0] if colors else "#FFFFFF")
    
    @staticmethod
    def _hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """Konvertiert Hex-Farbe zu RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @staticmethod
    def _interpolate_colors(colors: List[Tuple[int, int, int]], progress: float) -> Tuple[int, int, int]:
        """
        Interpoliert zwischen mehreren Farben
        """
        if len(colors) == 1:
            return colors[0]
        
        # Bestimme zwischen welchen Farben interpoliert werden soll
        segment_length = 1.0 / (len(colors) - 1)
        segment_index = int(progress / segment_length)
        
        # Begrenze Index
        segment_index = min(segment_index, len(colors) - 2)
        
        # Lokaler Progress innerhalb des Segments
        local_progress = (progress - segment_index * segment_length) / segment_length
        
        # Interpoliere zwischen den beiden Farben
        color1 = colors[segment_index]
        color2 = colors[segment_index + 1]
        
        r = int(color1[0] + (color2[0] - color1[0]) * local_progress)
        g = int(color1[1] + (color2[1] - color1[1]) * local_progress)
        b = int(color1[2] + (color2[2] - color1[2]) * local_progress)
        
        return (r, g, b)


class AdvancedAnimations:
    """
    Erweiterte Animationen für professionelle UI-Effekte
    """
    
    @staticmethod
    def morphing_button_animation(button: ctk.CTkButton,
                                 morph_text: str,
                                 morph_color: str,
                                 duration: float = 0.5,
                                 callback: Optional[Callable] = None):
        """
        Morphing-Animation für Buttons (Text und Farbe ändern sich)
        
        Args:
            button: Der Button
            morph_text: Neuer Text
            morph_color: Neue Farbe
            duration: Animationsdauer
            callback: Callback nach Animation
        """
        def animate():
            try:
                original_text = button.cget("text")
                original_color = button.cget("fg_color")
                
                # Schritt 1: Button verkleinern
                for i in range(10):
                    scale = 1.0 - (i / 10) * 0.1
                    if hasattr(button, '_apply_widget_scaling'):
                        button._apply_widget_scaling(scale)
                    time.sleep(duration / 40)
                
                # Schritt 2: Text und Farbe ändern
                button.configure(text=morph_text, fg_color=morph_color)
                
                # Schritt 3: Button wieder vergrößern
                for i in range(10):
                    scale = 0.9 + (i / 10) * 0.1
                    if hasattr(button, '_apply_widget_scaling'):
                        button._apply_widget_scaling(scale)
                    time.sleep(duration / 40)
                
                if callback:
                    callback()
                    
            except Exception as e:
                print(f"Morphing-Animation Fehler: {e}")
        
        threading.Thread(target=animate, daemon=True).start()
    
    @staticmethod
    def ripple_effect(widget: ctk.CTkFrame, 
                     click_x: int, 
                     click_y: int,
                     ripple_color: str = "#4FC3F7",
                     duration: float = 0.8):
        """
        Ripple-Effekt für Klicks (Material Design)
        
        Args:
            widget: Das Widget
            click_x: X-Koordinate des Klicks
            click_y: Y-Koordinate des Klicks
            ripple_color: Farbe des Ripple-Effekts
            duration: Animationsdauer
        """
        def animate():
            try:
                # Erstelle Ripple-Kreis
                ripple_frame = ctk.CTkFrame(
                    widget,
                    width=10,
                    height=10,
                    corner_radius=5,
                    fg_color=ripple_color
                )
                
                # Positioniere am Klick-Punkt
                ripple_frame.place(x=click_x-5, y=click_y-5)
                
                # Animiere Expansion
                max_radius = max(widget.winfo_width(), widget.winfo_height()) * 1.5
                steps = 30
                step_duration = duration / steps
                
                for i in range(steps):
                    progress = i / steps
                    current_radius = 10 + (max_radius - 10) * progress
                    
                    # Berechne Transparenz (fade out)
                    alpha = 1.0 - progress
                    
                    # Update Ripple-Größe
                    ripple_frame.configure(
                        width=int(current_radius),
                        height=int(current_radius),
                        corner_radius=int(current_radius / 2)
                    )
                    
                    # Zentriere Ripple
                    ripple_frame.place(
                        x=click_x - int(current_radius / 2),
                        y=click_y - int(current_radius / 2)
                    )
                    
                    time.sleep(step_duration)
                
                # Entferne Ripple
                ripple_frame.destroy()
                
            except Exception as e:
                print(f"Ripple-Effekt Fehler: {e}")
        
        threading.Thread(target=animate, daemon=True).start()
    
    @staticmethod
    def floating_elements_animation(widgets: List[ctk.CTkFrame],
                                   amplitude: int = 5,
                                   frequency: float = 0.02,
                                   phase_offset: float = 0.5):
        """
        Schwebende Elemente-Animation für dekorative Effekte
        
        Args:
            widgets: Liste von Widgets zum Animieren
            amplitude: Höhe der Schwebe-Bewegung
            frequency: Frequenz der Animation
            phase_offset: Phasenverschiebung zwischen Elementen
        """
        def animate():
            try:
                # Speichere ursprüngliche Positionen
                original_positions = []
                for widget in widgets:
                    original_positions.append((widget.winfo_x(), widget.winfo_y()))
                
                time_counter = 0
                
                while True:  # Endlos-Animation
                    for i, widget in enumerate(widgets):
                        if not widget.winfo_exists():
                            continue
                        
                        # Berechne Schwebe-Position
                        original_x, original_y = original_positions[i]
                        phase = time_counter + (i * phase_offset)
                        
                        offset_y = math.sin(phase) * amplitude
                        new_y = original_y + offset_y
                        
                        # Aktualisiere Position
                        widget.place(x=original_x, y=int(new_y))
                    
                    time_counter += frequency
                    time.sleep(0.05)  # 20 FPS
                    
            except Exception as e:
                print(f"Schwebende Elemente Fehler: {e}")
        
        threading.Thread(target=animate, daemon=True).start()
    
    @staticmethod
    def parallax_scrolling_effect(background_widgets: List[ctk.CTkFrame],
                                 foreground_widgets: List[ctk.CTkFrame],
                                 scroll_speed_bg: float = 0.5,
                                 scroll_speed_fg: float = 1.0):
        """
        Parallax-Scrolling-Effekt für Tiefenwirkung
        
        Args:
            background_widgets: Hintergrund-Widgets (langsamer)
            foreground_widgets: Vordergrund-Widgets (schneller)
            scroll_speed_bg: Scroll-Geschwindigkeit für Hintergrund
            scroll_speed_fg: Scroll-Geschwindigkeit für Vordergrund
        """
        def animate():
            try:
                scroll_offset = 0
                
                while True:  # Endlos-Animation
                    # Animiere Hintergrund-Widgets
                    for widget in background_widgets:
                        if not widget.winfo_exists():
                            continue
                        
                        current_x = widget.winfo_x()
                        new_x = current_x - scroll_speed_bg
                        
                        # Wrap around wenn aus dem Sichtbereich
                        if new_x < -widget.winfo_width():
                            new_x = widget.master.winfo_width()
                        
                        widget.place(x=int(new_x), y=widget.winfo_y())
                    
                    # Animiere Vordergrund-Widgets
                    for widget in foreground_widgets:
                        if not widget.winfo_exists():
                            continue
                        
                        current_x = widget.winfo_x()
                        new_x = current_x - scroll_speed_fg
                        
                        # Wrap around wenn aus dem Sichtbereich
                        if new_x < -widget.winfo_width():
                            new_x = widget.master.winfo_width()
                        
                        widget.place(x=int(new_x), y=widget.winfo_y())
                    
                    time.sleep(0.03)  # ~30 FPS
                    
            except Exception as e:
                print(f"Parallax-Scrolling Fehler: {e}")
        
        threading.Thread(target=animate, daemon=True).start()


class ParticleSystem:
    """
    Partikelsystem für dekorative Effekte
    """
    
    def __init__(self, parent: ctk.CTkFrame, 
                 particle_count: int = 20,
                 particle_color: str = "#4FC3F7",
                 particle_size: int = 3):
        """
        Initialisiert das Partikelsystem
        
        Args:
            parent: Parent-Widget
            particle_count: Anzahl der Partikel
            particle_color: Farbe der Partikel
            particle_size: Größe der Partikel
        """
        self.parent = parent
        self.particle_count = particle_count
        self.particle_color = particle_color
        self.particle_size = particle_size
        
        self.particles = []
        self.is_running = False
        self.animation_thread = None
        
        self.create_particles()
    
    def create_particles(self):
        """Erstellt die Partikel"""
        try:
            for _ in range(self.particle_count):
                particle = ctk.CTkFrame(
                    self.parent,
                    width=self.particle_size,
                    height=self.particle_size,
                    corner_radius=self.particle_size // 2,
                    fg_color=self.particle_color
                )
                
                # Zufällige Startposition
                x = random.randint(0, self.parent.winfo_width())
                y = random.randint(0, self.parent.winfo_height())
                
                particle.place(x=x, y=y)
                
                # Partikel-Eigenschaften
                particle_data = {
                    'widget': particle,
                    'x': x,
                    'y': y,
                    'velocity_x': random.uniform(-1, 1),
                    'velocity_y': random.uniform(-1, 1),
                    'life': 1.0
                }
                
                self.particles.append(particle_data)
                
        except Exception as e:
            print(f"Partikel-Erstellung Fehler: {e}")
    
    def start_animation(self):
        """Startet die Partikel-Animation"""
        if self.is_running:
            return
        
        self.is_running = True
        self.animation_thread = threading.Thread(target=self._animate_particles, daemon=True)
        self.animation_thread.start()
    
    def stop_animation(self):
        """Stoppt die Partikel-Animation"""
        self.is_running = False
    
    def _animate_particles(self):
        """Animiert die Partikel"""
        try:
            while self.is_running:
                for particle_data in self.particles:
                    if not particle_data['widget'].winfo_exists():
                        continue
                    
                    # Update Position
                    particle_data['x'] += particle_data['velocity_x']
                    particle_data['y'] += particle_data['velocity_y']
                    
                    # Bounce off walls
                    if particle_data['x'] <= 0 or particle_data['x'] >= self.parent.winfo_width():
                        particle_data['velocity_x'] *= -1
                    
                    if particle_data['y'] <= 0 or particle_data['y'] >= self.parent.winfo_height():
                        particle_data['velocity_y'] *= -1
                    
                    # Update visual position
                    particle_data['widget'].place(
                        x=int(particle_data['x']),
                        y=int(particle_data['y'])
                    )
                
                time.sleep(0.05)  # 20 FPS
                
        except Exception as e:
            print(f"Partikel-Animation Fehler: {e}")
    
    def destroy(self):
        """Zerstört das Partikelsystem"""
        self.stop_animation()
        
        for particle_data in self.particles:
            try:
                particle_data['widget'].destroy()
            except:
                pass
        
        self.particles.clear()


class AdvancedColorTheming:
    """
    Erweiterte Farbthemierung mit dynamischen Anpassungen
    """
    
    @staticmethod
    def apply_dynamic_color_scheme(widgets: List[ctk.CTkBaseClass],
                                  base_color: str,
                                  variation_strength: float = 0.2):
        """
        Wendet ein dynamisches Farbschema auf mehrere Widgets an
        
        Args:
            widgets: Liste von Widgets
            base_color: Basis-Farbe
            variation_strength: Stärke der Farbvariation (0.0 - 1.0)
        """
        try:
            # Erstelle Farbvariationen
            color_variations = AdvancedColorTheming._generate_color_variations(
                base_color, len(widgets), variation_strength
            )
            
            # Wende Farben auf Widgets an
            for widget, color in zip(widgets, color_variations):
                if hasattr(widget, 'configure'):
                    widget.configure(fg_color=color)
                
                # Animiere Farbwechsel
                ModernAnimations.color_fade_animation(
                    widget,
                    widget.cget("fg_color") if hasattr(widget, 'cget') else "#FFFFFF",
                    color,
                    0.5,
                    'fg_color'
                )
                
        except Exception as e:
            print(f"Dynamisches Farbschema Fehler: {e}")
    
    @staticmethod
    def _generate_color_variations(base_color: str, 
                                  count: int, 
                                  variation_strength: float) -> List[str]:
        """
        Generiert Farbvariationen basierend auf einer Basis-Farbe
        """
        try:
            # Konvertiere zu HSV für bessere Farbmanipulation
            rgb = GradientEffects._hex_to_rgb(base_color)
            hsv = colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255)
            
            variations = []
            
            for i in range(count):
                # Variiere Hue, Saturation und Value
                hue_offset = (i - count/2) * variation_strength * 0.1
                sat_offset = (i - count/2) * variation_strength * 0.2
                val_offset = (i - count/2) * variation_strength * 0.15
                
                new_hue = (hsv[0] + hue_offset) % 1.0
                new_sat = max(0, min(1, hsv[1] + sat_offset))
                new_val = max(0, min(1, hsv[2] + val_offset))
                
                # Konvertiere zurück zu RGB
                new_rgb = colorsys.hsv_to_rgb(new_hue, new_sat, new_val)
                new_color = f"#{int(new_rgb[0]*255):02x}{int(new_rgb[1]*255):02x}{int(new_rgb[2]*255):02x}"
                
                variations.append(new_color)
            
            return variations
            
        except Exception as e:
            print(f"Farbvariation Fehler: {e}")
            return [base_color] * count
    
    @staticmethod
    def create_color_breathing_effect(widget: ctk.CTkBaseClass,
                                     color1: str,
                                     color2: str,
                                     duration: float = 3.0):
        """
        Erstellt einen "atmenden" Farbeffekt
        
        Args:
            widget: Das Widget
            color1: Erste Farbe
            color2: Zweite Farbe
            duration: Dauer eines Atmungszyklus
        """
        def animate():
            try:
                while widget.winfo_exists():
                    # Atme von color1 zu color2
                    steps = 60
                    step_duration = duration / (steps * 2)
                    
                    for i in range(steps):
                        progress = i / steps
                        # Sinusförmige Interpolation für sanften Übergang
                        smooth_progress = (math.sin(progress * math.pi - math.pi/2) + 1) / 2
                        
                        current_color = AdvancedColorTheming._interpolate_color(
                            color1, color2, smooth_progress
                        )
                        
                        widget.configure(fg_color=current_color)
                        time.sleep(step_duration)
                    
                    # Atme von color2 zu color1
                    for i in range(steps):
                        progress = i / steps
                        smooth_progress = (math.sin(progress * math.pi - math.pi/2) + 1) / 2
                        
                        current_color = AdvancedColorTheming._interpolate_color(
                            color2, color1, smooth_progress
                        )
                        
                        widget.configure(fg_color=current_color)
                        time.sleep(step_duration)
                        
            except Exception as e:
                print(f"Atmungseffekt Fehler: {e}")
        
        threading.Thread(target=animate, daemon=True).start()
    
    @staticmethod
    def _interpolate_color(color1: str, color2: str, progress: float) -> str:
        """
        Interpoliert zwischen zwei Farben
        """
        try:
            rgb1 = GradientEffects._hex_to_rgb(color1)
            rgb2 = GradientEffects._hex_to_rgb(color2)
            
            r = int(rgb1[0] + (rgb2[0] - rgb1[0]) * progress)
            g = int(rgb1[1] + (rgb2[1] - rgb1[1]) * progress)
            b = int(rgb1[2] + (rgb2[2] - rgb1[2]) * progress)
            
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return color1


# Utility-Funktionen für erweiterte visuelle Effekte
def create_modern_dashboard_section(parent, title: str, content_widgets: List[ctk.CTkBaseClass]) -> ctk.CTkFrame:
    """
    Erstellt eine moderne Dashboard-Sektion mit Glasmorphismus-Effekt
    
    Args:
        parent: Parent-Widget
        title: Titel der Sektion
        content_widgets: Liste der Inhalts-Widgets
    
    Returns:
        Dashboard-Sektion Frame
    """
    try:
        # Hauptframe mit Glasmorphismus
        section_frame = ctk.CTkFrame(
            parent,
            corner_radius=UITheme.CORNER_RADIUS_LARGE,
            fg_color=UITheme.COLOR_SURFACE,
            border_width=1,
            border_color=UITheme.COLOR_BORDER
        )
        
        # Glasmorphismus-Effekt anwenden
        GlassmorphismEffect.apply_glass_effect(section_frame, opacity=0.8)
        
        # Header mit Gradient
        header_frame = GradientEffects.create_gradient_frame(
            section_frame,
            [UITheme.COLOR_GRADIENT_PRIMARY_START, UITheme.COLOR_GRADIENT_PRIMARY_END],
            section_frame.winfo_reqwidth(),
            50,
            "horizontal"
        )
        header_frame.pack(fill="x", padx=2, pady=(2, 0))
        
        # Titel
        title_label = ctk.CTkLabel(
            header_frame,
            text=title,
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_HEADING, size=16, weight="bold"),
            text_color=UITheme.COLOR_TEXT_ON_PRIMARY
        )
        title_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Content-Bereich
        content_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Widgets hinzufügen
        for i, widget in enumerate(content_widgets):
            widget.pack(fill="x", pady=5)
        
        return section_frame
        
    except Exception as e:
        print(f"Dashboard-Sektion Fehler: {e}")
        return ctk.CTkFrame(parent)


def apply_advanced_ui_effects(main_window: ctk.CTk):
    """
    Wendet erweiterte UI-Effekte auf das Hauptfenster an
    
    Args:
        main_window: Das Hauptfenster
    """
    try:
        # Glasmorphismus für das Hauptfenster
        if hasattr(main_window, 'configure'):
            main_window.configure(
                fg_color=UITheme.COLOR_BACKGROUND,
                bg_color=UITheme.COLOR_BACKGROUND
            )
        
        # Partikelsystem für Hintergrundeffekte (optional)
        # particle_system = ParticleSystem(main_window, particle_count=15)
        # particle_system.start_animation()
        
        print("Erweiterte UI-Effekte angewendet")
        
    except Exception as e:
        print(f"Erweiterte UI-Effekte Fehler: {e}")


# Import für zufällige Partikelpositionen
import random
