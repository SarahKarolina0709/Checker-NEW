import tkinter as tk
import customtkinter as ctk

class TestApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.geometry("800x600")
        self.root.title("Geometry Lock Test")

        self.label = ctk.CTkLabel(self.root, text="Try to resize this window.")
        self.label.pack(pady=20, padx=20)

        # Button to activate the standard lock
        self.lock_button = ctk.CTkButton(self.root, text="Activate MinSize Lock (current size)", command=self.activate_std_lock)
        self.lock_button.pack(pady=10)

        # Button to activate the absolute lock
        self.abs_lock_button = ctk.CTkButton(self.root, text="Activate Absolute Lock (1400x900)", command=self.activate_abs_lock)
        self.abs_lock_button.pack(pady=10)

        # Button to try to resize the window programmatically
        self.resize_button = ctk.CTkButton(self.root, text="Try to resize to 500x400", command=self.try_resize)
        self.resize_button.pack(pady=10)

    def activate_std_lock(self):
        print("\n--- ACTIVATING STANDARD MINSIZE LOCK ---")
        # activate_lock_for_window(self.root)
        print("--- STANDARD LOCK ACTIVATED ---\n")

    def activate_abs_lock(self):
        print("\n--- ACTIVATING ABSOLUTE 1400x900 LOCK ---")
        # activate_absolute_lock_for_main_window(self.root)
        print("--- ABSOLUTE LOCK ACTIVATED ---\n")

    def try_resize(self):
        print("\n--- ATTEMPTING TO RESIZE TO 500x400 ---")
        try:
            self.root.geometry("500x400")
            print("--- RESIZE ATTEMPTED ---")
        except Exception as e:
            print(f"--- RESIZE FAILED WITH EXCEPTION: {e} ---")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = TestApp()
    app.run()
