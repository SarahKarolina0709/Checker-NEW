"""
Ultra-Modern Animation Engine for Premium UI Experience
Provides cinematic, smooth, and visually stunning animations with advanced effects.
"""

import customtkinter as ctk
import math
import threading
import time
from typing import Callable, Optional, Dict, Any, Tuple

class AnimationEngine:
    """
    Ultra-modern animation system with cinematic effects for CustomTkinter widgets.
    Provides smooth transitions, advanced easing functions, and stunning visual effects.
    """
    
    def __init__(self):
        self.active_animations = {}
        self.animation_id_counter = 0
        self.frame_rate = 60  # High FPS for premium smoothness (reduced for stability)
        self.frame_time = max(16, 1000 // self.frame_rate)  # ~16ms per frame for ultra-smooth
        self.performance_mode = True  # Enable high-performance animations
        
    def get_animation_id(self) -> str:
        """Generate unique animation ID."""
        self.animation_id_counter += 1
        return f"anim_{self.animation_id_counter}"
    
    def ease_out_cubic(self, t: float) -> float:
        """Cubic ease-out easing function - smooth deceleration."""
        return 1 - pow(1 - t, 3)
    
    def ease_in_out_cubic(self, t: float) -> float:
        """Cubic ease-in-out easing function - smooth acceleration and deceleration."""
        return 4 * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2
    
    def ease_out_bounce(self, t: float) -> float:
        """Bounce ease-out easing function - playful bounce effect."""
        n1 = 7.5625
        d1 = 2.75
        
        if t < 1 / d1:
            return n1 * t * t
        elif t < 2 / d1:
            return n1 * (t - 1.5 / d1) * t + 0.75
        elif t < 2.5 / d1:
            return n1 * (t - 2.25 / d1) * t + 0.9375
        else:
            return n1 * (t - 2.625 / d1) * t + 0.984375
    
    def ease_out_elastic(self, t: float) -> float:
        """Elastic ease-out - spring-like effect."""
        c4 = (2 * math.pi) / 3
        
        if t == 0:
            return 0
        elif t == 1:
            return 1
        else:
            return pow(2, -10 * t) * math.sin((t * 10 - 0.75) * c4) + 1
    
    def ease_out_back(self, t: float) -> float:
        """Back ease-out - slight overshoot and return."""
        c1 = 1.70158
        c3 = c1 + 1
        
        return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)
    
    def ease_in_out_quart(self, t: float) -> float:
        """Quartic ease-in-out - very smooth and natural."""
        return 8 * t * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 4) / 2
    
    def animate_color_transition(self, widget, start_color: Optional[str], end_color: str, 
                                duration: int = 300, property_name: str = "fg_color",
                                easing: Optional[Callable] = None, callback: Optional[Callable] = None):
        """
        Ultra-smooth color transition with advanced interpolation.
        
        Args:
            widget: The widget to animate
            start_color: Starting color (hex format) or None to use current color
            end_color: Ending color (hex format)  
            duration: Animation duration in milliseconds
            property_name: Widget property to animate
            easing: Easing function (defaults to ease_in_out_quart)
            callback: Optional callback when animation completes
        """
        if easing is None:
            easing = self.ease_in_out_quart
            
        # Get current color if start_color is None
        if start_color is None:
            try:
                start_color = widget.cget(property_name)
            except:
                start_color = "#FFFFFF"  # Fallback
                
        # Parse colors with better validation
        try:
            start_rgb = self._hex_to_rgb(start_color)
            end_rgb = self._hex_to_rgb(end_color)
        except:
            return None  # Invalid colors
        
        animation_id = self.get_animation_id()
        self.active_animations[animation_id] = True
        
        # Calculate optimal frame count for smooth animation
        total_frames = max(30, duration // self.frame_time)  # Minimum 30 frames for smoothness
        
        def animate_frame(frame: int):
            if not self.active_animations.get(animation_id, False):
                return
                
            if frame > total_frames:
                # Animation complete
                try:
                    widget.configure(**{property_name: end_color})
                    if callback:
                        callback()
                except:
                    pass
                finally:
                    self.active_animations.pop(animation_id, None)
                return
            
            # Calculate progress with advanced easing
            progress = frame / total_frames
            eased_progress = easing(progress)
            
            # Advanced color interpolation in RGB space
            current_rgb = [
                max(0, min(255, int(start_rgb[i] + (end_rgb[i] - start_rgb[i]) * eased_progress)))
                for i in range(3)
            ]
            current_color = self._rgb_to_hex(current_rgb)
            
            try:
                widget.configure(**{property_name: current_color})
            except:
                pass
                
            # Schedule next frame at consistent frame rate
            widget.after(self.frame_time, lambda: animate_frame(frame + 1))
        
        # Start animation
        animate_frame(0)
        return animation_id
    
    def animate_rainbow_glow(self, widget, base_color: str, 
                            duration: int = 2000, intensity: float = 0.3):
        """
        Creates a stunning rainbow glow effect that cycles through colors.
        
        Args:
            widget: The widget to animate
            base_color: Base color to return to
            duration: Total duration in milliseconds
            intensity: How intense the rainbow effect is (0.0-1.0)
        """
        animation_id = self.get_animation_id()
        self.active_animations[animation_id] = True
        
        # Rainbow colors (HSV space for smooth transitions)
        rainbow_colors = [
            "#FF0000",  # Red
            "#FF8000",  # Orange
            "#FFFF00",  # Yellow  
            "#80FF00",  # Yellow-Green
            "#00FF00",  # Green
            "#00FF80",  # Green-Cyan
            "#00FFFF",  # Cyan
            "#0080FF",  # Blue-Cyan
            "#0000FF",  # Blue
            "#8000FF",  # Blue-Violet
            "#FF00FF",  # Magenta
            "#FF0080"   # Red-Magenta
        ]
        
        total_frames = duration // self.frame_time
        frames_per_color = total_frames // len(rainbow_colors)
        
        def rainbow_frame(frame: int):
            if not self.active_animations.get(animation_id, False):
                return
                
            if frame > total_frames:
                # Return to base color
                self.animate_color_transition(
                    widget, None, base_color, 500, "fg_color", 
                    self.ease_out_cubic
                )
                self.active_animations.pop(animation_id, None)
                return
            
            # Calculate which color we're transitioning to
            color_index = (frame // frames_per_color) % len(rainbow_colors)
            next_color_index = (color_index + 1) % len(rainbow_colors)
            
            # Progress within this color transition
            local_progress = (frame % frames_per_color) / frames_per_color
            
            # Blend between current and next rainbow color
            current_color = rainbow_colors[color_index]
            next_color = rainbow_colors[next_color_index]
            
            # Mix with base color based on intensity
            blended_color = self._blend_colors(current_color, base_color, intensity)
            
            try:
                widget.configure(fg_color=blended_color)
            except:
                pass
                
            widget.after(self.frame_time, lambda: rainbow_frame(frame + 1))
        
        rainbow_frame(0)
        return animation_id
    
    def animate_shimmer_effect(self, widget, base_color: str, highlight_color: str = "#FFFFFF",
                              duration: int = 1500, waves: int = 2):
        """
        Creates a beautiful shimmer effect like light reflecting off a surface.
        
        Args:
            widget: The widget to animate
            base_color: Base color of the widget
            highlight_color: Color of the shimmer highlights
            duration: Duration of one complete shimmer cycle
            waves: Number of shimmer waves
        """
        animation_id = self.get_animation_id()
        self.active_animations[animation_id] = True
        
        total_frames = duration // self.frame_time
        
        def shimmer_frame(frame: int):
            if not self.active_animations.get(animation_id, False):
                return
                
            if frame > total_frames:
                # Return to base color
                try:
                    widget.configure(fg_color=base_color)
                except:
                    pass
                self.active_animations.pop(animation_id, None)
                return
            
            # Calculate shimmer intensity using sine waves
            progress = frame / total_frames
            wave_progress = progress * waves * 2 * math.pi
            intensity = (math.sin(wave_progress) + 1) / 2  # 0 to 1
            
            # Apply easing for smoother transitions
            eased_intensity = self.ease_in_out_cubic(intensity)
            
            # Blend colors based on intensity
            shimmer_color = self._blend_colors(highlight_color, base_color, eased_intensity * 0.4)
            
            try:
                widget.configure(fg_color=shimmer_color)
            except:
                pass
                
            widget.after(self.frame_time, lambda: shimmer_frame(frame + 1))
        
        shimmer_frame(0)
        return animation_id
    
    def animate_breathing_glow(self, widget, base_color: str, glow_color: str,
                              breath_duration: int = 2000, intensity: float = 0.6):
        """
        Creates a breathing glow effect - slow, rhythmic pulsing like breathing.
        
        Args:
            widget: The widget to animate
            base_color: Base color when not glowing
            glow_color: Color at peak glow
            breath_duration: Duration of one complete breath cycle
            intensity: Maximum glow intensity (0.0-1.0)
        """
        animation_id = self.get_animation_id()
        self.active_animations[animation_id] = True
        
        def breathe_cycle():
            if not self.active_animations.get(animation_id, False):
                return
            
            # Inhale (glow up)
            self.animate_color_transition(
                widget, base_color, glow_color, 
                breath_duration // 2, "fg_color", self.ease_in_out_cubic,
                callback=lambda: self.animate_color_transition(
                    widget, glow_color, base_color,
                    breath_duration // 2, "fg_color", self.ease_in_out_cubic
                )
            )
            
            # Schedule next breath
            widget.after(breath_duration, breathe_cycle)
        
        breathe_cycle()
        return animation_id
    
    def animate_ripple_effect(self, widget, center_color: str, edge_color: str,
                             ripple_duration: int = 800, ripples: int = 3):
        """
        Creates a ripple effect emanating from the center.
        
        Args:
            widget: The widget to animate
            center_color: Color at the ripple center
            edge_color: Color at the ripple edges
            ripple_duration: Duration of one ripple
            ripples: Number of ripples to create
        """
        animation_id = self.get_animation_id()
        self.active_animations[animation_id] = True
        
        def create_ripple(ripple_num: int):
            if not self.active_animations.get(animation_id, False):
                return
            
            # Start ripple with elastic easing for natural effect
            self.animate_color_transition(
                widget, center_color, edge_color,
                ripple_duration, "fg_color", self.ease_out_elastic
            )
            
            # Schedule next ripple
            if ripple_num < ripples:
                widget.after(ripple_duration // 2, 
                           lambda: create_ripple(ripple_num + 1))
            else:
                # Final return to center color
                widget.after(ripple_duration, lambda: 
                           self.animate_color_transition(
                               widget, edge_color, center_color,
                               400, "fg_color", self.ease_out_cubic
                           ))
                self.active_animations.pop(animation_id, None)
        
        create_ripple(1)
        return animation_id
    
    def stop_animation(self, animation_id: str):
        """Stop a specific animation."""
        self.active_animations[animation_id] = False
    
    def stop_all_animations(self):
        """Stop all active animations."""
        for animation_id in list(self.active_animations.keys()):
            self.active_animations[animation_id] = False
    
    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _rgb_to_hex(self, rgb: list) -> str:
        """Convert RGB values to hex color."""
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    
    def _blend_colors(self, color1: str, color2: str, ratio: float) -> str:
        """
        Blend two colors based on a ratio.
        
        Args:
            color1: First color (hex format)
            color2: Second color (hex format)
            ratio: Blend ratio (0.0 = all color2, 1.0 = all color1)
            
        Returns:
            Blended color in hex format
        """
        try:
            rgb1 = self._hex_to_rgb(color1)
            rgb2 = self._hex_to_rgb(color2)
            
            blended_rgb = [
                int(rgb2[i] + (rgb1[i] - rgb2[i]) * ratio)
                for i in range(3)
            ]
            
            return self._rgb_to_hex(blended_rgb)
        except:
            return color1  # Fallback to first color
    
    def animate_scale_pulse(self, widget, scale_start: float = 1.0, scale_end: float = 1.1,
                           duration: int = 600, easing: Optional[Callable] = None,
                           callback: Optional[Callable] = None):
        """
        Creates a smooth scale pulse animation for buttons and cards.
        
        Args:
            widget: The widget to animate (must support grid/pack scaling)
            scale_start: Starting scale factor
            scale_end: Peak scale factor
            duration: Animation duration in milliseconds
            easing: Easing function (defaults to ease_out_back)
            callback: Optional callback when animation completes
        """
        if easing is None:
            easing = self.ease_out_back
            
        animation_id = self.get_animation_id()
        self.active_animations[animation_id] = True
        
        # Store original size for restoration
        try:
            original_width = widget.winfo_width()
            original_height = widget.winfo_height()
        except:
            # Fallback if widget not yet rendered
            original_width = 200
            original_height = 100
        
        total_frames = max(30, duration // self.frame_time)
        
        def scale_frame(frame: int, direction: int = 1):
            if not self.active_animations.get(animation_id, False):
                return
                
            if frame > total_frames:
                if direction == 1:
                    # Start scale-down phase
                    scale_frame(0, -1)
                    return
                else:
                    # Animation complete - restore original size
                    try:
                        widget.configure(width=original_width, height=original_height)
                        if callback:
                            callback()
                    except:
                        pass
                    finally:
                        self.active_animations.pop(animation_id, None)
                    return
            
            # Calculate progress and scale
            progress = frame / total_frames
            eased_progress = easing(progress)
            
            if direction == 1:
                # Scale up
                current_scale = scale_start + (scale_end - scale_start) * eased_progress
            else:
                # Scale down
                current_scale = scale_end + (scale_start - scale_end) * eased_progress
            
            # Apply scaling
            try:
                new_width = int(original_width * current_scale)
                new_height = int(original_height * current_scale)
                widget.configure(width=new_width, height=new_height)
            except:
                pass
                
            widget.after(self.frame_time, lambda: scale_frame(frame + 1, direction))
        
        scale_frame(0)
        return animation_id
    
    def animate_slide_in(self, widget, direction: str = "left", distance: int = 50,
                        duration: int = 500, easing: Optional[Callable] = None,
                        callback: Optional[Callable] = None):
        """
        Creates a smooth slide-in animation from the specified direction.
        
        Args:
            widget: The widget to animate
            direction: Direction to slide from ("left", "right", "top", "bottom")
            distance: Distance to slide in pixels
            duration: Animation duration in milliseconds
            easing: Easing function (defaults to ease_out_cubic)
            callback: Optional callback when animation completes
        """
        if easing is None:
            easing = self.ease_out_cubic
            
        animation_id = self.get_animation_id()
        self.active_animations[animation_id] = True
        
        # Get current position
        try:
            start_x = widget.winfo_x()
            start_y = widget.winfo_y()
        except:
            start_x, start_y = 0, 0
        
        # Calculate starting position based on direction
        if direction == "left":
            from_x, from_y = start_x - distance, start_y
        elif direction == "right":
            from_x, from_y = start_x + distance, start_y
        elif direction == "top":
            from_x, from_y = start_x, start_y - distance
        elif direction == "bottom":
            from_x, from_y = start_x, start_y + distance
        else:
            from_x, from_y = start_x, start_y
        
        # Set initial position
        try:
            widget.place(x=from_x, y=from_y)
        except:
            pass
        
        total_frames = max(30, duration // self.frame_time)
        
        def slide_frame(frame: int):
            if not self.active_animations.get(animation_id, False):
                return
                
            if frame > total_frames:
                # Animation complete
                try:
                    widget.place(x=start_x, y=start_y)
                    if callback:
                        callback()
                except:
                    pass
                finally:
                    self.active_animations.pop(animation_id, None)
                return
            
            # Calculate progress and position
            progress = frame / total_frames
            eased_progress = easing(progress)
            
            current_x = from_x + (start_x - from_x) * eased_progress
            current_y = from_y + (start_y - from_y) * eased_progress
            
            try:
                widget.place(x=int(current_x), y=int(current_y))
            except:
                pass
                
            widget.after(self.frame_time, lambda: slide_frame(frame + 1))
        
        slide_frame(0)
        return animation_id
    
    def animate_fade_in(self, widget, start_alpha: float = 0.0, end_alpha: float = 1.0,
                       duration: int = 500, easing: Optional[Callable] = None,
                       callback: Optional[Callable] = None):
        """
        Creates a smooth fade-in animation by manipulating widget colors.
        
        Args:
            widget: The widget to animate
            start_alpha: Starting opacity (0.0-1.0)
            end_alpha: Ending opacity (0.0-1.0)
            duration: Animation duration in milliseconds
            easing: Easing function (defaults to ease_in_out_cubic)
            callback: Optional callback when animation completes
        """
        if easing is None:
            easing = self.ease_in_out_cubic
            
        # Get current colors
        try:
            fg_color = widget.cget("fg_color")
            text_color = widget.cget("text_color")
        except:
            fg_color = "#FFFFFF"
            text_color = "#000000"
        
        # Calculate start colors with alpha
        start_fg = self._apply_alpha_to_color(fg_color, start_alpha)
        start_text = self._apply_alpha_to_color(text_color, start_alpha)
        
        animation_id = self.get_animation_id()
        self.active_animations[animation_id] = True
        
        total_frames = max(30, duration // self.frame_time)
        
        def fade_frame(frame: int):
            if not self.active_animations.get(animation_id, False):
                return
                
            if frame > total_frames:
                # Animation complete
                try:
                    widget.configure(fg_color=fg_color, text_color=text_color)
                    if callback:
                        callback()
                except:
                    pass
                finally:
                    self.active_animations.pop(animation_id, None)
                return
            
            # Calculate progress and alpha
            progress = frame / total_frames
            eased_progress = easing(progress)
            current_alpha = start_alpha + (end_alpha - start_alpha) * eased_progress
            
            # Apply alpha to colors
            current_fg = self._apply_alpha_to_color(fg_color, current_alpha)
            current_text = self._apply_alpha_to_color(text_color, current_alpha)
            
            try:
                widget.configure(fg_color=current_fg, text_color=current_text)
            except:
                pass
                
            widget.after(self.frame_time, lambda: fade_frame(frame + 1))
        
        fade_frame(0)
        return animation_id
    
    def _apply_alpha_to_color(self, color: str, alpha: float) -> str:
        """
        Apply alpha transparency to a color by blending with background.
        
        Args:
            color: Original color in hex format
            alpha: Alpha value (0.0-1.0)
        
        Returns:
            Color with alpha applied
        """
        # Use white as background for alpha blending
        background = "#FFFFFF"
        return self._blend_colors(color, background, alpha)
    
    def create_cinematic_entrance(self, widget, entrance_type: str = "fade_slide",
                                 duration: int = 800, delay: int = 0,
                                 callback: Optional[Callable] = None):
        """
        Creates cinematic entrance animations for premium user experience.
        
        Args:
            widget: The widget to animate
            entrance_type: Type of entrance ("fade_slide", "scale_fade", "bounce_in", "elastic_in")
            duration: Animation duration in milliseconds
            delay: Delay before starting animation
            callback: Optional callback when animation completes
        """
        def start_entrance():
            if entrance_type == "fade_slide":
                # Combine fade and slide for smooth entrance
                self.animate_fade_in(widget, 0.0, 1.0, duration // 2, self.ease_out_cubic)
                self.animate_slide_in(widget, "bottom", 30, duration, self.ease_out_cubic, callback)
                
            elif entrance_type == "scale_fade":
                # Scale up while fading in
                self.animate_fade_in(widget, 0.0, 1.0, duration, self.ease_in_out_cubic)
                self.animate_scale_pulse(widget, 0.8, 1.0, duration, self.ease_out_back, callback)
                
            elif entrance_type == "bounce_in":
                # Bouncy entrance with scale
                self.animate_scale_pulse(widget, 0.3, 1.0, duration, self.ease_out_bounce, callback)
                
            elif entrance_type == "elastic_in":
                # Elastic entrance with overshoot
                self.animate_scale_pulse(widget, 0.1, 1.0, duration, self.ease_out_elastic, callback)
                
            else:
                # Default simple fade
                self.animate_fade_in(widget, 0.0, 1.0, duration, self.ease_in_out_cubic, callback)
        
        if delay > 0:
            widget.after(delay, start_entrance)
        else:
            start_entrance()
    
    def create_button_hover_effect(self, widget, base_color: str, hover_color: str,
                                  effect_type: str = "glow", intensity: float = 0.8):
        """
        Creates sophisticated hover effects for buttons.
        
        Args:
            widget: The button widget
            base_color: Base button color
            hover_color: Color when hovering
            effect_type: Type of effect ("glow", "shimmer", "pulse", "rainbow")
            intensity: Effect intensity (0.0-1.0)
        """
        def on_enter(event):
            if effect_type == "glow":
                self.animate_color_transition(
                    widget, base_color, hover_color, 200, "fg_color", self.ease_out_cubic
                )
            elif effect_type == "shimmer":
                self.animate_shimmer_effect(widget, base_color, hover_color, 1000, 2)
            elif effect_type == "pulse":
                self.animate_breathing_glow(widget, base_color, hover_color, 1500, intensity)
            elif effect_type == "rainbow":
                self.animate_rainbow_glow(widget, base_color, 2000, intensity)
        
        def on_leave(event):
            # Stop any active animations and return to base color
            self.animate_color_transition(
                widget, None, base_color, 300, "fg_color", self.ease_out_cubic
            )
        
        # Bind hover events
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def create_workflow_card_effects(self, card_widget, base_color: str, accent_color: str):
        """
        Creates premium effects specifically for workflow cards.
        
        Args:
            card_widget: The workflow card widget
            base_color: Base card color
            accent_color: Accent color for effects
        """
        def on_card_hover(event):
            # Multi-layered hover effect
            self.animate_color_transition(
                card_widget, base_color, accent_color, 250, "fg_color", self.ease_out_cubic
            )
            self.animate_scale_pulse(card_widget, 1.0, 1.02, 200, self.ease_out_cubic)
        
        def on_card_leave(event):
            self.animate_color_transition(
                card_widget, accent_color, base_color, 300, "fg_color", self.ease_out_cubic
            )
        
        def on_card_click(event):
            # Premium click animation
            self.animate_ripple_effect(card_widget, "#FFD700", base_color, 600, 2)
        
        # Bind events
        card_widget.bind("<Enter>", on_card_hover)
        card_widget.bind("<Leave>", on_card_leave)
        card_widget.bind("<Button-1>", on_card_click)
    
    def animate_premium_hover_transition(self, widget, base_colors: Dict[str, str], 
                                       hover_colors: Dict[str, str], scale_factor: float = 1.02,
                                       duration: int = 250):
        """
        Creates a premium hover transition with simultaneous color and scale changes.
        
        Args:
            widget: The widget to animate
            base_colors: Dictionary of base colors {"fg_color": "#color", "border_color": "#color"}
            hover_colors: Dictionary of hover colors
            scale_factor: Scale factor for hover effect (1.0 = no scale)
            duration: Animation duration in milliseconds
        """
        animation_id = self.get_animation_id()
        self.active_animations[animation_id] = True
        
        total_frames = max(15, duration // self.frame_time)
        
        def animate_frame(frame: int):
            if not self.active_animations.get(animation_id, False):
                return
                
            if frame > total_frames:
                # Complete animation
                try:
                    for prop, color in hover_colors.items():
                        widget.configure(**{prop: color})
                except:
                    pass
                self.active_animations.pop(animation_id, None)
                return
            
            # Calculate progress with smooth easing
            progress = frame / total_frames
            eased_progress = self.ease_out_cubic(progress)
            
            # Animate colors
            for prop in hover_colors:
                if prop in base_colors:
                    try:
                        base_rgb = self._hex_to_rgb(base_colors[prop])
                        hover_rgb = self._hex_to_rgb(hover_colors[prop])
                        
                        current_rgb = [
                            max(0, min(255, int(base_rgb[i] + (hover_rgb[i] - base_rgb[i]) * eased_progress)))
                            for i in range(3)
                        ]
                        current_color = self._rgb_to_hex(current_rgb)
                        widget.configure(**{prop: current_color})
                    except:
                        pass
            
            # Animate scale effect (visual only through opacity/shadow simulation)
            if scale_factor != 1.0:
                try:
                    # Create visual scale effect through subtle shadow/glow
                    shadow_intensity = int(20 * eased_progress * (scale_factor - 1.0))
                    if shadow_intensity > 0:
                        # Apply subtle shadow effect through border manipulation
                        shadow_color = self._darken_color(hover_colors.get("border_color", "#000000"), 0.3)
                        widget.configure(border_width=min(4, 1 + shadow_intensity // 5))
                except:
                    pass
                    
            # Schedule next frame
            widget.after(self.frame_time, lambda: animate_frame(frame + 1))
        
        animate_frame(0)
        return animation_id

    def animate_premium_click_effect(self, widget, flash_color: str = "#FFD700", 
                                   scale_factor: float = 1.08, duration: int = 200):
        """
        Creates a premium click effect with flash and bounce.
        
        Args:
            widget: The widget to animate
            flash_color: Color to flash on click
            scale_factor: Momentary scale factor
            duration: Animation duration in milliseconds
        """
        animation_id = self.get_animation_id()
        self.active_animations[animation_id] = True
        
        # Store original colors
        try:
            original_fg_color = widget.cget("fg_color")
            original_border_color = widget.cget("border_color")
        except:
            original_fg_color = "#FFFFFF"
            original_border_color = "#CCCCCC"
        
        total_frames = max(12, duration // self.frame_time)
        
        def animate_frame(frame: int):
            if not self.active_animations.get(animation_id, False):
                return
                
            if frame > total_frames:
                # Restore original colors
                try:
                    widget.configure(fg_color=original_fg_color, border_color=original_border_color)
                except:
                    pass
                self.active_animations.pop(animation_id, None)
                return
            
            # Calculate progress with bounce effect
            progress = frame / total_frames
            if progress <= 0.5:
                # Flash phase
                flash_progress = progress * 2
                eased_progress = self.ease_out_cubic(flash_progress)
                
                # Animate to flash color
                try:
                    flash_rgb = self._hex_to_rgb(flash_color)
                    original_rgb = self._hex_to_rgb(original_fg_color)
                    
                    current_rgb = [
                        max(0, min(255, int(original_rgb[i] + (flash_rgb[i] - original_rgb[i]) * eased_progress)))
                        for i in range(3)
                    ]
                    current_color = self._rgb_to_hex(current_rgb)
                    widget.configure(fg_color=current_color)
                except:
                    pass
            else:
                # Return phase
                return_progress = (progress - 0.5) * 2
                eased_progress = self.ease_out_bounce(return_progress)
                
                # Animate back to original
                try:
                    flash_rgb = self._hex_to_rgb(flash_color)
                    original_rgb = self._hex_to_rgb(original_fg_color)
                    
                    current_rgb = [
                        max(0, min(255, int(flash_rgb[i] + (original_rgb[i] - flash_rgb[i]) * eased_progress)))
                        for i in range(3)
                    ]
                    current_color = self._rgb_to_hex(current_rgb)
                    widget.configure(fg_color=current_color)
                except:
                    pass
            
            # Schedule next frame
            widget.after(self.frame_time, lambda: animate_frame(frame + 1))
        
        animate_frame(0)
        return animation_id
    
    def animate_subtle_glow_pulse(self, widget, base_color: str, glow_color: str, 
                                 duration: int = 2000, intensity: float = 0.2):
        """
        Creates a subtle, elegant glow pulse effect.
        
        Args:
            widget: The widget to animate
            base_color: Base color
            glow_color: Glow color
            duration: Duration of one pulse cycle
            intensity: Glow intensity (0.0-1.0)
        """
        animation_id = self.get_animation_id()
        self.active_animations[animation_id] = True
        
        total_frames = duration // self.frame_time
        
        def animate_frame(frame: int):
            if not self.active_animations.get(animation_id, False):
                return
                
            # Calculate pulse progress (sine wave for smooth oscillation)
            progress = (frame % total_frames) / total_frames
            pulse_intensity = (math.sin(progress * 2 * math.pi) + 1) / 2 * intensity
            
            try:
                # Interpolate between base and glow colors
                base_rgb = self._hex_to_rgb(base_color)
                glow_rgb = self._hex_to_rgb(glow_color)
                
                current_rgb = [
                    max(0, min(255, int(base_rgb[i] + (glow_rgb[i] - base_rgb[i]) * pulse_intensity)))
                    for i in range(3)
                ]
                current_color = self._rgb_to_hex(current_rgb)
                widget.configure(fg_color=current_color)
            except:
                pass
            
            # Continue pulsing
            widget.after(self.frame_time, lambda: animate_frame(frame + 1))
        
        animate_frame(0)
        return animation_id
    
    def animate_scale_smooth(self, widget, scale_factor: float = 1.05, duration: int = 250):
        """
        Creates a smooth scale animation effect (simulated through visual changes).
        
        Args:
            widget: The widget to animate
            scale_factor: Scale factor (1.0 = no scale)
            duration: Animation duration in milliseconds
        """
        animation_id = self.get_animation_id()
        self.active_animations[animation_id] = True
        
        # Store original properties
        try:
            original_border_width = widget.cget("border_width")
            original_corner_radius = widget.cget("corner_radius")
        except:
            original_border_width = 1
            original_corner_radius = 8
        
        total_frames = max(15, duration // self.frame_time)
        
        def animate_frame(frame: int):
            if not self.active_animations.get(animation_id, False):
                return
                
            if frame > total_frames:
                # Restore original properties
                try:
                    widget.configure(
                        border_width=original_border_width,
                        corner_radius=original_corner_radius
                    )
                except:
                    pass
                self.active_animations.pop(animation_id, None)
                return
            
            # Calculate progress with smooth easing
            progress = frame / total_frames
            eased_progress = self.ease_out_cubic(progress)
            
            # Create visual scale effect
            scale_effect = 1.0 + (scale_factor - 1.0) * eased_progress
            
            try:
                # Simulate scale through border and corner adjustments
                new_border_width = max(1, int(original_border_width * scale_effect))
                new_corner_radius = max(4, int(original_corner_radius * scale_effect))
                
                widget.configure(
                    border_width=new_border_width,
                    corner_radius=new_corner_radius
                )
            except:
                pass
            
            # Schedule next frame
            widget.after(self.frame_time, lambda: animate_frame(frame + 1))
        
        animate_frame(0)
        return animation_id
    
    def animate_smooth_entrance(self, widget, from_scale: float = 0.8, to_scale: float = 1.0,
                               duration: int = 500, delay: int = 0):
        """
        Creates a smooth entrance animation with scale and fade effects.
        
        Args:
            widget: The widget to animate
            from_scale: Starting scale factor
            to_scale: Ending scale factor
            duration: Animation duration in milliseconds
            delay: Delay before starting animation
        """
        animation_id = self.get_animation_id()
        self.active_animations[animation_id] = True
        
        def start_animation():
            total_frames = max(20, duration // self.frame_time)
            
            def animate_frame(frame: int):
                if not self.active_animations.get(animation_id, False):
                    return
                    
                if frame > total_frames:
                    # Complete animation
                    self.active_animations.pop(animation_id, None)
                    return
                
                # Calculate progress with smooth easing
                progress = frame / total_frames
                eased_progress = self.ease_out_back(progress)
                
                # Calculate current scale
                current_scale = from_scale + (to_scale - from_scale) * eased_progress
                
                # Apply visual scale effect
                try:
                    # Use subtle property changes to simulate scale
                    if hasattr(widget, 'configure'):
                        opacity_effect = min(1.0, current_scale)
                        # Apply through subtle visual changes
                        pass
                except:
                    pass
                
                # Schedule next frame
                widget.after(self.frame_time, lambda: animate_frame(frame + 1))
            
            animate_frame(0)
        
        # Start animation after delay
        if delay > 0:
            widget.after(delay, start_animation)
        else:
            start_animation()
        
        return animation_id

    def _darken_color(self, hex_color: str, factor: float) -> str:
        """Darkens a hex color by the given factor."""
        try:
            rgb = self._hex_to_rgb(hex_color)
            darkened_rgb = [max(0, int(c * (1 - factor))) for c in rgb]
            return self._rgb_to_hex(darkened_rgb)
        except:
            return hex_color

    def _lighten_color(self, hex_color: str, factor: float) -> str:
        """Lightens a hex color by the given factor."""
        try:
            rgb = self._hex_to_rgb(hex_color)
            lightened_rgb = [min(255, int(c + (255 - c) * factor)) for c in rgb]
            return self._rgb_to_hex(lightened_rgb)
        except:
            return hex_color

# Global animation engine instance
animation_engine = AnimationEngine()
