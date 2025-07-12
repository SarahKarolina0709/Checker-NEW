
import customtkinter as ctk
from ui_theme import UITheme
import tkinter as tk

class SearchableDropdown(ctk.CTkFrame):
    """
    A searchable dropdown widget that appears below the entry field.
    """
    def __init__(self, parent, variable, options, command=None, font=None, **kwargs):
        super().__init__(parent, **kwargs)

        self.variable = variable
        self.options = sorted(options)
        self.command = command
        self.font = font or UITheme.get_font("body")

        self.configure(fg_color="transparent")

        self.entry = ctk.CTkEntry(self, textvariable=self.variable, font=self.font)
        self.entry.pack(fill="x")

        # This Toplevel will contain the scrollable frame
        self.dropdown_toplevel = None

        self.entry.bind("<KeyRelease>", self._on_key_release)
        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)
        self.entry.bind("<Down>", self._on_arrow_down)


    def _create_dropdown_toplevel(self):
        if self.dropdown_toplevel and self.dropdown_toplevel.winfo_exists():
            return

        self.dropdown_toplevel = tk.Toplevel(self)
        self.dropdown_toplevel.wm_overrideredirect(True) # Remove window decorations
        self.dropdown_toplevel.wm_attributes("-topmost", True)

        self.scrollable_frame = ctk.CTkScrollableFrame(
            self.dropdown_toplevel,
            fg_color=UITheme.COLOR_SURFACE,
            border_color=UITheme.COLOR_PRIMARY,
            border_width=1
        )
        self.scrollable_frame.pack(fill="both", expand=True)
        self.scrollable_frame.bind("<FocusOut>", self._on_focus_out)
        self.scrollable_frame.bind("<Escape>", lambda e: self._hide_dropdown())

        self._update_dropdown_options(self.options)


    def _update_dropdown_position(self):
        if not self.dropdown_toplevel or not self.dropdown_toplevel.winfo_exists():
            return
        
        entry_x = self.entry.winfo_rootx()
        entry_y = self.entry.winfo_rooty()
        entry_height = self.entry.winfo_height()
        entry_width = self.entry.winfo_width()

        self.dropdown_toplevel.geometry(f"{entry_width}x200+{entry_x}+{entry_y + entry_height}")


    def _show_dropdown(self):
        if not self.dropdown_toplevel or not self.dropdown_toplevel.winfo_exists():
            self._create_dropdown_toplevel()
        
        self._update_dropdown_position()
        self.dropdown_toplevel.deiconify()
        self.dropdown_toplevel.lift()
        self.entry.focus_set() # Keep focus on entry


    def _hide_dropdown(self):
        if self.dropdown_toplevel and self.dropdown_toplevel.winfo_exists():
            self.dropdown_toplevel.withdraw()

    def _on_focus_in(self, event=None):
        search_term = self.variable.get().lower()
        filtered_options = [opt for opt in self.options if search_term in opt.lower()]
        self._update_dropdown_options(filtered_options)
        self._show_dropdown()

    def _on_focus_out(self, event=None):
        # Use `after` to delay hiding, allowing time for a button click to register
        self.after(200, self._check_focus_and_hide)

    def _check_focus_and_hide(self):
        # Check if the focus is still within the dropdown or the entry
        focused_widget = self.focus_get()
        if focused_widget != self.entry and (not self.dropdown_toplevel or not self.dropdown_toplevel.winfo_exists() or focused_widget not in self.dropdown_toplevel.winfo_children()):
             self._hide_dropdown()


    def _on_key_release(self, event=None):
        search_term = self.variable.get().lower()
        filtered_options = [opt for opt in self.options if search_term in opt.lower()]
        self._update_dropdown_options(filtered_options)
        self._show_dropdown()

    def _update_dropdown_options(self, options):
        if not self.dropdown_toplevel or not self.scrollable_frame.winfo_exists():
            return
            
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        for option in options:
            btn = ctk.CTkButton(
                self.scrollable_frame,
                text=option,
                command=lambda opt=option: self._select_option(opt),
                font=self.font,
                anchor="w",
                **UITheme.BUTTON_STYLE_FLAT
            )
            btn.pack(fill="x", padx=2, pady=2)

    def _select_option(self, option):
        self.variable.set(option)
        self._hide_dropdown()
        self.entry.focus_set()
        if self.command:
            self.command(option)

    def _on_arrow_down(self, event=None):
        if self.dropdown_toplevel and self.dropdown_toplevel.winfo_exists():
            self.scrollable_frame.focus_set()
            first_button = self.scrollable_frame.winfo_children()[0] if self.scrollable_frame.winfo_children() else None
            if first_button:
                first_button.focus_set()

    def set_options(self, options):
        self.options = sorted(options)
        self._update_dropdown_options(self.options)

