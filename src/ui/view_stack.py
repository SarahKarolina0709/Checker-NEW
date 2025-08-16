
"""
ViewStack - Lean Pattern for View Management
==========================================

A clean, efficient view management system that eliminates the need for repeated
pack_forget() calls and provides O(1) view switching without layout conflicts.

This pattern uses place() geometry manager for the view stack while maintaining
compatibility with pack() and grid() within individual views.
"""

from typing import Dict, Optional, Callable, Any
import logging

import customtkinter as ctk

try:
    from ui_theme import enhanced_theme
except ImportError:
    # Create a fallback theme object if enhanced_theme is not available
    class FallbackTheme:
        @staticmethod
        def get_color(key: str, fallback: str = "#FFFFFF") -> str:
            """Fallback theme that always returns the fallback color."""
            return fallback

    enhanced_theme = FallbackTheme()

class ViewStack(ctk.CTkFrame):
    """
    Efficient view management system with O(1) switching.

    Uses place() geometry manager for stacking views while allowing
    individual views to use pack() or grid() internally.
    """

    def __init__(self, master, default_view: Optional[str] = None, **kwargs):
        """
        Initialize the ViewStack.

        Args:
            master: Parent widget
            default_view: Optional name of a view to show when requested view is not found
            **kwargs: Additional CTkFrame arguments
        """
        # Set up default styling from enhanced theme with fallbacks
        try:
            default_kwargs = {
                'fg_color': enhanced_theme.get_color("background") or "#FFFFFF",
                'corner_radius': 0,
                'border_width': 0
            }
        except (ImportError, AttributeError, NameError) as e:
            # Fallback to safe defaults if enhanced_theme is not available
            default_kwargs = {
                'fg_color': "#FFFFFF",  # Safe white background
                'corner_radius': 0,
                'border_width': 0
            }
        default_kwargs.update(kwargs)

        super().__init__(master, **default_kwargs)

        # Internal state
        self._frames: Dict[str, ctk.CTkFrame] = {}
        self._current_view: Optional[str] = None
        self._view_callbacks: Dict[str, Dict[str, Callable]] = {}
        self._default_view: Optional[str] = default_view

        # Set up logging
        self.logger = logging.getLogger(__name__)

        # Configure the container for proper stacking
        self.configure(bg_color="transparent")

    def add(self, name: str, frame: ctk.CTkFrame, **callbacks) -> None:
        """
        Add a view to the stack.

        Args:
            name: Unique identifier for the view
            frame: The CTkFrame to add to the stack
            **callbacks: Optional callbacks (on_show, on_hide, on_before_show, on_after_hide)
        """
        if name in self._frames:
            self.logger.warning(f"ViewStack: Overwriting existing view '{name}'")

        self._frames[name] = frame
        self._view_callbacks[name] = callbacks

        # Place the frame to fill the entire ViewStack
        frame.place(in_=self, x=0, y=0, relwidth=1, relheight=1)

        # Initially hide the frame by lowering it
        frame.lower()

        self.logger.info(f"ViewStack: Added view '{name}' to stack")

    def show(self, name: str, **transition_kwargs) -> bool:
        """
        Show the specified view (O(1) operation).

        Args:
            name: Name of the view to show
            **transition_kwargs: Additional arguments passed to callbacks

        Returns:
            bool: True if view was shown successfully, False if view not found
        """
        if name not in self._frames:
            self.logger.error(f"ViewStack: View '{name}' not found in stack")

            # Try to show default view as fallback
            if self._default_view and self._default_view != name and self._default_view in self._frames:
                self.logger.info(f"ViewStack: Falling back to default view '{self._default_view}'")
                return self.show(self._default_view, **transition_kwargs)

            return False

        # Call before_show callback for the new view
        if name in self._view_callbacks:
            before_show_callback = self._view_callbacks[name].get('on_before_show')
            if before_show_callback:
                try:
                    before_show_callback(**transition_kwargs)
                except Exception as e:
                    self.logger.error(f"ViewStack: Error in before_show callback for '{name}': {e}")

        # Hide current view if any
        if self._current_view and self._current_view != name:
            self._hide_current_view()

        # Show the new view
        self._frames[name].lift()
        previous_view = self._current_view
        self._current_view = name

        # Call on_show callback for the new view
        if name in self._view_callbacks:
            on_show_callback = self._view_callbacks[name].get('on_show')
            if on_show_callback:
                try:
                    on_show_callback(previous_view=previous_view, **transition_kwargs)
                except Exception as e:
                    self.logger.error(f"ViewStack: Error in on_show callback for '{name}': {e}")

        self.logger.info(f"ViewStack: Showing view '{name}' (was: '{previous_view}')")
        return True

    def hide(self, name: str) -> bool:
        """
        Hide a specific view.

        Args:
            name: Name of the view to hide

        Returns:
            bool: True if view was hidden successfully, False if view not found
        """
        if name not in self._frames:
            self.logger.error(f"ViewStack: View '{name}' not found in stack")
            return False

        # Lower the frame to hide it
        self._frames[name].lower()

        # Call on_hide callback
        if name in self._view_callbacks:
            on_hide_callback = self._view_callbacks[name].get('on_hide')
            if on_hide_callback:
                try:
                    on_hide_callback()
                except Exception as e:
                    self.logger.error(f"ViewStack: Error in on_hide callback for '{name}': {e}")

        # Update current view if this was the current view
        if self._current_view == name:
            self._current_view = None

        self.logger.info(f"ViewStack: Hidden view '{name}'")
        return True

    def _hide_current_view(self) -> None:
        """Hide the currently shown view."""
        if self._current_view:
            current_frame = self._frames[self._current_view]
            current_frame.lower()

            # Call on_hide callback
            if self._current_view in self._view_callbacks:
                on_hide_callback = self._view_callbacks[self._current_view].get('on_hide')
                if on_hide_callback:
                    try:
                        on_hide_callback()
                    except Exception as e:
                        self.logger.error(f"ViewStack: Error in on_hide callback for '{self._current_view}': {e}")

            # Call on_after_hide callback
            if self._current_view in self._view_callbacks:
                after_hide_callback = self._view_callbacks[self._current_view].get('on_after_hide')
                if after_hide_callback:
                    try:
                        after_hide_callback()
                    except Exception as e:
                        self.logger.error(f"ViewStack: Error in on_after_hide callback for '{self._current_view}': {e}")

    def get_current_view(self) -> Optional[str]:
        """
        Get the name of the currently shown view.

        Returns:
            Optional[str]: Name of current view or None if no view is shown
        """
        return self._current_view

    def get_views(self) -> Dict[str, ctk.CTkFrame]:
        """
        Get all views in the ViewStack.

        Returns:
            Dict[str, ctk.CTkFrame]: Dictionary of view names to frames
        """
        return self._frames.copy()

    def get_view(self, name: str) -> Optional[ctk.CTkFrame]:
        """
        Get a specific view by name.

        Args:
            name: The name of the view to retrieve

        Returns:
            Optional[ctk.CTkFrame]: The view frame if found, None otherwise
        """
        return self._frames.get(name)

    def remove_view(self, name: str, destroy_widget: bool = False) -> bool:
        """
        Remove a view from the stack.

        Args:
            name: Name of the view to remove
            destroy_widget: If True, the frame widget will be destroyed.
                            Set to False if you want to reuse the frame later.

        Returns:
            bool: True if view was removed successfully, False if view not found
        """
        if name not in self._frames:
            self.logger.error(f"ViewStack: View '{name}' not found in stack")
            return False

        # Hide the view if it's currently shown
        if self._current_view == name:
            self._hide_current_view()
            self._current_view = None

        # Remove the frame
        frame = self._frames[name]
        frame.place_forget()

        if destroy_widget:
            frame.destroy()
            self.logger.info(f"ViewStack: Destroyed widget for view '{name}'")

        # Clean up
        del self._frames[name]
        if name in self._view_callbacks:
            del self._view_callbacks[name]

        self.logger.info(f"ViewStack: Removed view '{name}' from stack")
        return True

    def has_view(self, name: str) -> bool:
        """
        Check if a view exists in the stack.

        Args:
            name: Name of the view to check

        Returns:
            bool: True if view exists, False otherwise
        """
        return name in self._frames

    def clear(self, destroy_widgets: bool = True) -> None:
        """
        Remove all views from the stack.

        Args:
            destroy_widgets: If True, all frame widgets will be destroyed.
        """
        for name in list(self._frames.keys()):
            self.remove_view(name, destroy_widget=destroy_widgets)

        self.logger.info("ViewStack: Cleared all views from stack")

    def replace_view(self, name: str, new_frame: ctk.CTkFrame, destroy_old: bool = True, **callbacks) -> bool:
        """
        Replace an existing view with a new frame.

        Args:
            name: Name of the view to replace
            new_frame: The new CTkFrame to replace the old one with
            destroy_old: If True, the old frame widget will be destroyed
            **callbacks: Optional callbacks for the new view

        Returns:
            bool: True if view was replaced successfully, False if view didn't exist
        """
        if name not in self._frames:
            self.logger.warning(f"ViewStack: View '{name}' not found for replacement, adding as new view")
            self.add(name, new_frame, **callbacks)
            return True

        # Check if this view is currently shown
        was_current = self._current_view == name

        # Remove the old view
        success = self.remove_view(name, destroy_widget=destroy_old)
        if not success:
            return False

        # Add the new view
        self.add(name, new_frame, **callbacks)

        # If the old view was currently shown, show the new one
        if was_current:
            self.show(name)

        self.logger.info(f"ViewStack: Replaced view '{name}' successfully")
        return True

    def set_default_view(self, name: Optional[str]) -> bool:
        """
        Set the default fallback view.

        Args:
            name: Name of the view to use as default, or None to disable fallback

        Returns:
            bool: True if default view was set successfully, False if view doesn't exist
        """
        if name is None:
            self._default_view = None
            self.logger.info("ViewStack: Default view disabled")
            return True

        if name not in self._frames:
            self.logger.error(f"ViewStack: Cannot set default view '{name}' - view not found")
            return False

        self._default_view = name
        self.logger.info(f"ViewStack: Default view set to '{name}'")
        return True

    def get_default_view(self) -> Optional[str]:
        """
        Get the current default fallback view.

        Returns:
            Optional[str]: Name of default view or None if not set
        """
        return self._default_view

class EnhancedViewStack(ViewStack):
    """
    Enhanced ViewStack with additional features:
    - View history/navigation
    - Transition animations
    - View lifecycle management
    - Theme integration
    """

    def __init__(self, master, enable_history: bool = True, max_history: int = 10, **kwargs):
        """
        Initialize the Enhanced ViewStack.

        Args:
            master: Parent widget
            enable_history: Whether to track view history
            max_history: Maximum number of views to keep in history
            **kwargs: Additional CTkFrame arguments
        """
        super().__init__(master, **kwargs)

        self._enable_history = enable_history
        self._max_history = max_history
        self._view_history: list[str] = []
        self._animation_enabled = True

    def show(self, name: str, add_to_history: bool = True, **transition_kwargs) -> bool:
        """
        Show a view with optional history tracking.

        Args:
            name: Name of the view to show
            add_to_history: Whether to add this view to history
            **transition_kwargs: Additional arguments passed to callbacks

        Returns:
            bool: True if view was shown successfully
        """
        # Add to history before showing
        if add_to_history and self._enable_history and name != self._current_view:
            if self._current_view and self._current_view != name:
                self._view_history.append(self._current_view)
                # Limit history size
                if len(self._view_history) > self._max_history:
                    self._view_history.pop(0)

        # Show the view with animation if enabled
        if self._animation_enabled:
            return self._show_with_animation(name, **transition_kwargs)
        else:
            return super().show(name, **transition_kwargs)

    def go_back(self) -> bool:
        """
        Go back to the previous view in history.

        Returns:
            bool: True if successfully went back, False if no history
        """
        if not self._enable_history or not self._view_history:
            self.logger.info("ViewStack: No history available for going back")
            return False

        previous_view = self._view_history.pop()
        return self.show(previous_view, add_to_history=False)

    def get_history(self) -> list[str]:
        """
        Get the view history.

        Returns:
            list[str]: List of view names in history order
        """
        return self._view_history.copy()

    def clear_history(self) -> None:
        """Clear the view history."""
        self._view_history.clear()
        self.logger.info("ViewStack: Cleared view history")

    def set_animation_enabled(self, enabled: bool) -> None:
        """
        Enable or disable view transition animations.

        Args:
            enabled: Whether to enable animations
        """
        self._animation_enabled = enabled
        self.logger.info(f"ViewStack: Animation {'enabled' if enabled else 'disabled'}")

    def _show_with_animation(self, name: str, **transition_kwargs) -> bool:
        """
        Show a view with fade-in animation.

        Args:
            name: Name of the view to show
            **transition_kwargs: Additional arguments passed to callbacks

        Returns:
            bool: True if view was shown successfully
        """
        # First show the view normally (but hidden)
        success = super().show(name, **transition_kwargs)
        if not success:
            return False

        # Get the frame for animation
        frame = self._frames[name]

        # Start with low opacity
        try:
            frame.configure(fg_color=frame.cget("fg_color"))  # Ensure color is set
            self._animate_fade_in(frame, steps=10, duration=200)
        except Exception as e:
            self.logger.warning(f"ViewStack: Animation failed for '{name}': {e}")
            # Animation failed, but view is still shown

        return True

    def _animate_fade_in(self, frame: ctk.CTkFrame, steps: int = 10, duration: int = 200) -> None:
        """
        Animate fade-in effect for a frame.

        Args:
            frame: The frame to animate
            steps: Number of animation steps
            duration: Total animation duration in milliseconds
        """
        step_delay = duration // steps

        def fade_step(current_step: int):
            if current_step <= steps:
                # Calculate alpha value (0.3 to 1.0)
                alpha = 0.3 + (0.7 * current_step / steps)

                try:
                    # Get current color and apply alpha effect through color manipulation
                    current_color = frame.cget("fg_color")
                    if isinstance(current_color, tuple):
                        # Light/dark mode tuple
                        light_color, dark_color = current_color
                    else:
                        light_color = dark_color = current_color

                    # Apply alpha effect by blending with background
                    # This is a simplified approach since CTk doesn't support direct alpha
                    if current_step < steps:
                        # During animation, slightly modify appearance
                        if hasattr(frame, '_original_border_width'):
                            border_width = frame._original_border_width
                        else:
                            frame._original_border_width = frame.cget("border_width")
                            border_width = frame._original_border_width

                        # Subtle border effect during animation
                        frame.configure(border_width=max(0, int(border_width * alpha)))
                    else:
                        # Animation complete, restore original appearance
                        if hasattr(frame, '_original_border_width'):
                            frame.configure(border_width=frame._original_border_width)

                    # Schedule next step
                    if current_step < steps:
                        frame.after(step_delay, lambda: fade_step(current_step + 1))

                except Exception as e:
                    self.logger.debug(f"ViewStack: Animation step failed: {e}")
                    # Stop animation on error
                    return

        # Start animation
        fade_step(0)

# Convenience function for creating a ViewStack
def create_view_stack(master, enhanced: bool = False, **kwargs) -> ViewStack:
    """
    Create a ViewStack instance.

    Args:
        master: Parent widget
        enhanced: Whether to create an EnhancedViewStack
        **kwargs: Additional arguments for ViewStack

    Returns:
        ViewStack: A ViewStack or EnhancedViewStack instance
    """
    if enhanced:
        return EnhancedViewStack(master, **kwargs)
    else:
        return ViewStack(master, **kwargs)