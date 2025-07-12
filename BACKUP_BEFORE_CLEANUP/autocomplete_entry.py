import tkinter as tk
import customtkinter as ctk

class CTkAutocompleteEntry(ctk.CTkEntry):
    def __init__(self, master=None, completions=None, variable=None, completion_command=None, **kwargs):
        if variable:
            self._variable = variable
        else:
            self._variable = tk.StringVar()
        
        super().__init__(master, textvariable=self._variable, **kwargs)

        self._completions = sorted(completions if completions else [])
        self._completion_command = completion_command # Command to call on selection

        self._listbox = None
        self._listbox_active = False

        self.bind("<KeyRelease>", self._on_keyrelease)
        self.bind("<FocusOut>", self._on_focus_out)
        self.bind("<Down>", self._on_arrow_down_entry) # Renamed to avoid conflict
        self.bind("<Escape>", lambda e: self._hide_listbox())


    def _on_keyrelease(self, event):
        # Ignore control keys that don't change the text
        if event.keysym in ("Down", "Up", "Return", "Escape", "Control_L", "Control_R", "Shift_L", "Shift_R", "Alt_L", "Alt_R"):
            return

        value = self._variable.get()
        if not value:
            self._hide_listbox()
            return

        matches = [comp for comp in self._completions if value.lower() in comp.lower()]

        if matches:
            if not self._listbox_active:
                self._show_listbox()
            
            self._listbox.delete(0, tk.END)
            for idx, match in enumerate(matches):
                self._listbox.insert(tk.END, match)
            
            if matches: # Select first item if listbox is not empty
                self._listbox.selection_set(0)
                self._listbox.activate(0)
        else:
            self._hide_listbox()

    def _show_listbox(self):
        if self._listbox_active:
            return
        
        self.update_idletasks() 
        x = self.winfo_x()
        y = self.winfo_y() + self.winfo_height() + 2 # Small gap
        width = self.winfo_width()

        self._listbox = tk.Listbox(self.master, 
                                   width=max(10, width // 8), # Approx char width, min width 10
                                   height=min(4, len(self._completions)), 
                                   relief=tk.SOLID, 
                                   borderwidth=1,
                                   highlightthickness=1, # For better visibility
                                   highlightcolor=selfcget("border_color") if self.cget("border_width") > 0 else "gray"
                                   )
        self._listbox.place(x=x, y=y, width=width)
        
        self._listbox.bind("<<ListboxSelect>>", self._on_listbox_select_event)
        self._listbox.bind("<ButtonRelease-1>", self._on_listbox_select_event) # Handle click
        self._listbox.bind("<FocusOut>", self._on_focus_out_listbox)
        self._listbox.bind("<Return>", self._on_listbox_select_event)
        self._listbox.bind("<Escape>", lambda e: self._hide_listbox())
        self._listbox.bind("<Up>", self._on_arrow_up_listbox)
        self._listbox.bind("<Down>", self._on_arrow_down_listbox)

        self._listbox_active = True

    def _hide_listbox(self, event=None):
        if self._listbox_active and self._listbox:
            self._listbox.destroy()
            self._listbox = None
            self._listbox_active = False
        return "break" # Prevent further processing for Escape if needed

    def _on_focus_out(self, event=None):
        self.after(150, self._check_focus_and_hide)

    def _on_focus_out_listbox(self, event=None):
        self.after(100, self._check_focus_and_hide)

    def _check_focus_and_hide(self):
        focused_widget = self.winfo_toplevel().focus_get()
        if focused_widget != self and (not self._listbox or focused_widget != self._listbox):
            self._hide_listbox()

    def _on_listbox_select_event(self, event=None): # Renamed to avoid conflict
        if self._listbox_active and self._listbox.curselection():
            selection = self._listbox.get(self._listbox.curselection())
            self._variable.set(selection)
            self._hide_listbox()
            self.icursor(tk.END) # Move cursor to end of entry
            self.focus_set() 
            if self._completion_command:
                self._completion_command(selection)
        return "break"


    def _on_arrow_down_entry(self, event): # Bound to Entry
        if not self._listbox_active and self._variable.get():
            self._on_keyrelease(event) 
        
        if self._listbox_active and self._listbox.size() > 0:
            self._listbox.focus_set()
            self._listbox.selection_clear(0, tk.END)
            self._listbox.selection_set(0)
            self._listbox.activate(0)
            self._listbox.see(0)
            return "break" 

    def _on_arrow_up_listbox(self, event): # Bound to Listbox
        if self._listbox_active and self._listbox.size() > 0:
            current_selection = self._listbox.curselection()
            if not current_selection or current_selection[0] == 0: # If first or no selection, go to entry
                self.focus_set()
                self._hide_listbox() # Optionally hide or just move focus
                return "break"
            
            prev_idx = max(current_selection[0] - 1, 0)
            self._listbox.selection_clear(0, tk.END)
            self._listbox.selection_set(prev_idx)
            self._listbox.activate(prev_idx)
            self._listbox.see(prev_idx)
        return "break"

    def _on_arrow_down_listbox(self, event): # Bound to Listbox
        if self._listbox_active and self._listbox.size() > 0:
            current_selection = self._listbox.curselection()
            if not current_selection: # Should ideally not happen if listbox has focus
                idx_to_set = 0
            else:
                idx_to_set = min(current_selection[0] + 1, self._listbox.size() - 1)
            
            self._listbox.selection_clear(0, tk.END)
            self._listbox.selection_set(idx_to_set)
            self._listbox.activate(idx_to_set)
            self._listbox.see(idx_to_set)
        return "break"

    def set_completions(self, completions):
        self._completions = sorted(completions if completions else [])

    def configure(self, **kwargs):
        if "completions" in kwargs:
            self.set_completions(kwargs.pop("completions"))
        if "completion_command" in kwargs:
            self._completion_command = kwargs.pop("completion_command")
        if "variable" in kwargs:
            self._variable = kwargs["variable"]
            # Ensure the entry's textvariable is also updated if variable is changed post-init
            super().configure(textvariable=self._variable) 
            kwargs.pop("variable") # remove so it's not passed to super if already handled

        super().configure(**kwargs)
    
    def get(self): # Override get to use the StringVar
        return self._variable.get()

    def set(self, value): # Add set method for convenience
        self._variable.set(value)
        # self._on_keyrelease(None) # Optionally trigger update, but might be too aggressive
