"""
Enhanced Visual Effects for Checker Pro Suite
Adds beautiful visual effects like gradients, shadows, and animations.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import Canvas
from ui_theme import enhanced_theme, ProfessionalColors
from typing import Tuple, Optional, Dict, Any
import threading
import time
import math


class GradientFrame(ctk.CTkFrame):
    """A custom frame with gradient background."""
    
    def __init__(self, master, color1: str, color2: str, direction: str = "vertical", **kwargs):
        super().__init__(master, **kwargs)
        self.color1 = color1
        self.color2 = color2
        self.direction = direction
        self.gradient_canvas = None
        self.bind("<Configure>", self._on_resize)
        self.after(1, self._create_gradient)
    
    def _create_gradient(self):
        """Create gradient background."""
        if self.gradient_canvas:
            self.gradient_canvas.destroy()
        
        self.gradient_canvas = Canvas(
            self,
            highlightthickness=0,
            borderwidth=0,
            relief='flat'
        )
        self.gradient_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Draw gradient
        self._draw_gradient()
    
    def _draw_gradient(self):
        """Draw the gradient on the canvas."""
        if not self.gradient_canvas:
            return
        
        width = self.winfo_width()
        height = self.winfo_height()
        
        if width <= 1 or height <= 1:
            self.after(10, self._draw_gradient)
            return
        
        self.gradient_canvas.delete("gradient")
        
        # Create gradient steps
        steps = max(width, height)
        
        if self.direction == "vertical":
            for i in range(steps):
                ratio = i / steps
                color = self._interpolate_color(self.color1, self.color2, ratio)
                y = int(height * ratio)
                self.gradient_canvas.create_rectangle(
                    0, y, width, y + 1,
                    fill=color,
                    outline=color,
                    tags="gradient"
                )
        else:  # horizontal
            for i in range(steps):
                ratio = i / steps
                color = self._interpolate_color(self.color1, self.color2, ratio)
                x = int(width * ratio)
                self.gradient_canvas.create_rectangle(
                    x, 0, x + 1, height,
                    fill=color,
                    outline=color,
                    tags="gradient"
                )
    
    def _interpolate_color(self, color1: str, color2: str, ratio: float) -> str:
        """Interpolate between two colors."""
        if color1.startswith('#'):
            color1 = color1[1:]
        if color2.startswith('#'):
            color2 = color2[1:]
        
        # Convert to RGB
        r1, g1, b1 = int(color1[0:2], 16), int(color1[2:4], 16), int(color1[4:6], 16)
        r2, g2, b2 = int(color2[0:2], 16), int(color2[2:4], 16), int(color2[4:6], 16)
        
        # Interpolate
        r = int(r1 + (r2 - r1) * ratio)
        g = int(g1 + (g2 - g1) * ratio)
        b = int(b1 + (b2 - b1) * ratio)
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _on_resize(self, event):
        """Handle resize event."""
        self.after(1, self._draw_gradient)


class AnimatedCard(ctk.CTkFrame):
    """A card with smooth entrance animations and hover effects."""
    
    def __init__(self, master, delay: float = 0.0, **kwargs):
        super().__init__(master, **kwargs)
        self.delay = delay
        self.original_opacity = 1.0
        self.hover_scale = 1.02
        self.is_hovered = False
        self.animation_running = False
        
        # Start with invisible
        self.configure(fg_color=enhanced_theme.get_color('background'))
        
        # Schedule entrance animation
        self.after(int(delay * 1000), self._animate_entrance)
        
        # Bind hover effects
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        
        # Bind to all child widgets
        self.bind_all("<Enter>", self._on_widget_enter)
        self.bind_all("<Leave>", self._on_widget_leave)
    
    def _animate_entrance(self):
        """Animate card entrance."""
        if self.animation_running:
            return
        
        self.animation_running = True
        
        # Fade in animation
        for i in range(20):
            opacity = i / 20
            self._set_opacity(opacity)
            self.update()
            time.sleep(0.02)
        
        self.animation_running = False
    
    def _set_opacity(self, opacity: float):
        """Set visual opacity effect."""
        base_color = enhanced_theme.get_color('card')
        bg_color = enhanced_theme.get_color('background')
        
        # Simulate opacity by blending colors
        if base_color.startswith('#') and bg_color.startswith('#'):
            blended = self._blend_colors(base_color, bg_color, opacity)
            self.configure(fg_color=blended)
    
    def _blend_colors(self, color1: str, color2: str, ratio: float) -> str:
        """Blend two colors based on ratio."""
        if color1.startswith('#'):
            color1 = color1[1:]
        if color2.startswith('#'):
            color2 = color2[1:]
        
        r1, g1, b1 = int(color1[0:2], 16), int(color1[2:4], 16), int(color1[4:6], 16)
        r2, g2, b2 = int(color2[0:2], 16), int(color2[2:4], 16), int(color2[4:6], 16)
        
        r = int(r1 * ratio + r2 * (1 - ratio))
        g = int(g1 * ratio + g2 * (1 - ratio))
        b = int(b1 * ratio + b2 * (1 - ratio))
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _on_enter(self, event):
        """Handle mouse enter."""
        if self.is_hovered:
            return
        
        self.is_hovered = True
        self._animate_hover_in()
    
    def _on_leave(self, event):
        """Handle mouse leave."""
        if not self.is_hovered:
            return
        
        self.is_hovered = False
        self._animate_hover_out()
    
    def _on_widget_enter(self, event):
        """Handle enter on child widgets."""
        if event.widget.master == self or event.widget == self:
            self._on_enter(event)
    
    def _on_widget_leave(self, event):
        """Handle leave on child widgets."""
        if event.widget.master == self or event.widget == self:
            self._on_leave(event)
    
    def _animate_hover_in(self):
        """Animate hover in effect."""
        if not self.is_hovered:
            return
        
        # Scale up effect
        self.configure(
            fg_color=enhanced_theme.get_color('surface'),
            border_width=2,
            border_color=enhanced_theme.get_color('primary')
        )
    
    def _animate_hover_out(self):
        """Animate hover out effect."""
        if self.is_hovered:
            return
        
        # Scale down effect
        self.configure(
            fg_color=enhanced_theme.get_color('card'),
            border_width=1,
            border_color=enhanced_theme.get_color('border')
        )


class PulsingIcon(ctk.CTkLabel):
    """An icon that pulses with color changes."""
    
    def __init__(self, master, colors: list = None, pulse_duration: float = 2.0, **kwargs):
        super().__init__(master, **kwargs)
        self.colors = colors or [
            enhanced_theme.get_color('primary'),
            enhanced_theme.get_color('secondary'),
            enhanced_theme.get_color('accent')
        ]
        self.pulse_duration = pulse_duration
        self.color_index = 0
        self.pulse_active = True
        
        # Start pulsing
        self.after(100, self._pulse_color)
    
    def _pulse_color(self):
        """Pulse through colors."""
        if not self.pulse_active:
            return
        
        # Change color
        current_color = self.colors[self.color_index]
        self.configure(text_color=current_color)
        
        # Move to next color
        self.color_index = (self.color_index + 1) % len(self.colors)
        
        # Schedule next pulse
        delay = int(self.pulse_duration * 1000)
        self.after(delay, self._pulse_color)
    
    def stop_pulsing(self):
        """Stop the pulsing effect."""
        self.pulse_active = False
    
    def start_pulsing(self):
        """Start the pulsing effect."""
        if not self.pulse_active:
            self.pulse_active = True
            self.after(100, self._pulse_color)


class FloatingButton(ctk.CTkButton):
    """A button with floating animation effect."""
    
    def __init__(self, master, float_amplitude: int = 5, float_speed: float = 2.0, **kwargs):
        super().__init__(master, **kwargs)
        self.float_amplitude = float_amplitude
        self.float_speed = float_speed
        self.original_y = None
        self.float_active = True
        self.float_time = 0
        
        # Start floating after widget is mapped
        self.after(100, self._start_floating)
    
    def _start_floating(self):
        """Start the floating animation."""
        if self.original_y is None:
            self.original_y = self.winfo_y()
        
        self._float_animation()
    
    def _float_animation(self):
        """Animate floating effect."""
        if not self.float_active:
            return
        
        # Calculate new position
        offset = int(self.float_amplitude * math.sin(self.float_time * self.float_speed))
        new_y = self.original_y + offset
        
        # Apply position (if using place layout)
        try:
            place_info = self.place_info()
            if place_info:
                self.place(y=new_y)
        except:
            pass
        
        # Update time
        self.float_time += 0.1
        
        # Schedule next frame
        self.after(50, self._float_animation)
    
    def stop_floating(self):
        """Stop the floating effect."""
        self.float_active = False
        if self.original_y is not None:
            try:
                self.place(y=self.original_y)
            except:
                pass
    
    def start_floating(self):
        """Start the floating effect."""
        if not self.float_active:
            self.float_active = True
            self.after(100, self._start_floating)


class RainbowProgressBar(ctk.CTkProgressBar):
    """A progress bar with rainbow colors."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.rainbow_colors = [
            "#FF0000", "#FF7F00", "#FFFF00", "#00FF00", 
            "#0000FF", "#4B0082", "#9400D3"
        ]
        self.color_index = 0
        self.rainbow_active = True
        
        # Start rainbow animation
        self.after(100, self._rainbow_animation)
    
    def _rainbow_animation(self):
        """Animate rainbow colors."""
        if not self.rainbow_active:
            return
        
        # Change color
        current_color = self.rainbow_colors[self.color_index]
        self.configure(progress_color=current_color)
        
        # Move to next color
        self.color_index = (self.color_index + 1) % len(self.rainbow_colors)
        
        # Schedule next color change
        self.after(500, self._rainbow_animation)
    
    def stop_rainbow(self):
        """Stop the rainbow effect."""
        self.rainbow_active = False
    
    def start_rainbow(self):
        """Start the rainbow effect."""
        if not self.rainbow_active:
            self.rainbow_active = True
            self.after(100, self._rainbow_animation)


def create_sparkle_effect(widget, duration: float = 3.0, sparkle_count: int = 10):
    """Create a sparkle effect on a widget."""
    canvas = Canvas(widget, highlightthickness=0, borderwidth=0)
    canvas.place(x=0, y=0, relwidth=1, relheight=1)
    
    sparkles = []
    
    def create_sparkle():
        """Create a single sparkle."""
        if len(sparkles) >= sparkle_count:
            return
        
        x = widget.winfo_width() * 0.1 + (widget.winfo_width() * 0.8) * (len(sparkles) / sparkle_count)
        y = widget.winfo_height() * 0.1 + (widget.winfo_height() * 0.8) * (len(sparkles) / sparkle_count)
        
        sparkle = canvas.create_oval(
            x - 2, y - 2, x + 2, y + 2,
            fill="#FFD700",
            outline="#FFD700"
        )
        sparkles.append(sparkle)
        
        # Animate sparkle
        def animate_sparkle(step=0):
            if step > 20:
                canvas.delete(sparkle)
                if sparkle in sparkles:
                    sparkles.remove(sparkle)
                return
            
            # Scale and fade
            scale = 1 + (step / 20) * 2
            alpha = 1 - (step / 20)
            
            # Update sparkle
            canvas.coords(sparkle, x - scale, y - scale, x + scale, y + scale)
            
            # Continue animation
            widget.after(50, lambda: animate_sparkle(step + 1))
        
        animate_sparkle()
    
    # Create sparkles over time
    for i in range(sparkle_count):
        widget.after(i * 200, create_sparkle)
    
    # Clean up after duration
    widget.after(int(duration * 1000), lambda: canvas.destroy())


# Color theme utilities
def get_vibrant_color_scheme(base_color: str) -> Dict[str, str]:
    """Get a vibrant color scheme based on a base color."""
    vibrant_schemes = {
        'blue': {
            'primary': '#0078D4',
            'secondary': '#64B5F6',
            'accent': '#81C784',
            'background': '#E1F5FE'
        },
        'purple': {
            'primary': '#9C27B0',
            'secondary': '#BA68C8',
            'accent': '#FFD54F',
            'background': '#F3E5F5'
        },
        'green': {
            'primary': '#4CAF50',
            'secondary': '#81C784',
            'accent': '#FFD54F',
            'background': '#E8F5E8'
        },
        'orange': {
            'primary': '#FF7043',
            'secondary': '#FFB74D',
            'accent': '#64B5F6',
            'background': '#FFF3E0'
        }
    }
    
    return vibrant_schemes.get(base_color, vibrant_schemes['blue'])


def apply_glow_effect(widget, glow_color: str, intensity: float = 0.5):
    """Apply a glow effect to a widget."""
    original_border = widget.cget('border_width')
    original_border_color = widget.cget('border_color')
    
    def glow_in():
        widget.configure(
            border_width=3,
            border_color=glow_color
        )
    
    def glow_out():
        widget.configure(
            border_width=original_border,
            border_color=original_border_color
        )
    
    widget.bind("<Enter>", lambda e: glow_in())
    widget.bind("<Leave>", lambda e: glow_out())
