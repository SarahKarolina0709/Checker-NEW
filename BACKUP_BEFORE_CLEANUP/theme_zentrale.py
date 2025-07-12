import tkinter as tk
from tkinter import colorchooser, messagebox, simpledialog
import json
import os

def öffne_theme_zentrale(root, THEME, speicherpfad="themes.json", apply_callback=None):
    popup = tk.Toplevel(root)
    popup.title("🎨 Theme-Zentrale")
    popup.geometry("440x520")
    popup.configure(bg="#2a2a2a")

    aktuell = tk.StringVar(value=list(THEME.keys())[0])
    tk.Label(popup, text="Theme auswählen:", bg="#2a2a2a", fg="white").pack(pady=(10, 0))
    dropdown = tk.OptionMenu(popup, aktuell, *THEME.keys())
    dropdown.pack()

    einträge = {}

    def update_vorschau():
        try:            bg = einträge["bg"].get()
            fg = einträge["fg"].get()
            btn = einträge["btn"].get()
            preview_box.configure(bg=bg)
            preview_button.configure(bg=btn, fg=fg)
            preview_entry.configure(bg="white", fg=fg)
        except Exception as e:
            print("⚠️ Vorschau konnte nicht aktualisiert werden:", e)

    def aktualisiere_feld():
        farben_neu = THEME[aktuell.get()]
        for k, entry in einträge.items():
            entry.delete(0, "end")
            entry.insert(0, farben_neu[k])
        update_vorschau()

    def farbe_wählen(eingabefeld):
        farbe = colorchooser.askcolor()[1]
        if farbe:
            eingabefeld.delete(0, "end")
            eingabefeld.insert(0, farbe)
            update_vorschau()

    tk.Label(popup, text="Farben bearbeiten:", bg="#2a2a2a", fg="white").pack(pady=(15, 5))

    for key in ["bg", "fg", "btn", "btn_hover", "accent"]:
        rahmen = tk.Frame(popup, bg="#2a2a2a")
        rahmen.pack(pady=3)
        tk.Label(rahmen, text=key, width=10, anchor="w", bg="#2a2a2a", fg="white").pack(side="left")
        ein = tk.Entry(rahmen, width=10)
        ein.insert(0, THEME[aktuell.get()][key])
        ein.pack(side="left", padx=5)
        tk.Button(rahmen, text="🎨", command=lambda e=ein: farbe_wählen(e), width=2).pack(side="left")
        einträge[key] = ein

    # Vorschau mit Button + Eingabefeld
    preview_box = tk.Frame(popup, width=300, height=70, bg=THEME[aktuell.get()]["bg"], bd=1, relief="sunken")
    preview_box.pack(pady=15)
    preview_box.pack_propagate(0)

    preview_button = tk.Button(preview_box, text="Button", font=("Arial", 9))
    preview_button.pack(side="left", padx=10, pady=10)

    preview_entry = tk.Entry(preview_box, width=20)
    preview_entry.pack(side="left", padx=10, pady=10)

    # Duplizieren
    def duplizieren():
        name = simpledialog.askstring("Duplizieren", "Neuen Namen eingeben:")
        if name and name not in THEME:
            THEME[name] = dict(THEME[aktuell.get()])
            aktuell.set(name)
            menu = dropdown["menu"]
            menu.add_command(label=name, command=tk._setit(aktuell, name))

    # Löschen
    def löschen():
        name = aktuell.get()
        if name in THEME and len(THEME) > 1:
            if messagebox.askyesno("Löschen", f"Theme '{name}' wirklich löschen?"):
                THEME.pop(name)
                aktuell.set(list(THEME.keys())[0])
                dropdown["menu"].delete(0, "end")
                for key in THEME:
                    dropdown["menu"].add_command(label=key, command=tk._setit(aktuell, key))
                aktualisiere_feld()

    tk.Button(popup, text="➕ Duplizieren", command=duplizieren).pack(pady=(5, 0))
    tk.Button(popup, text="🗑 Theme löschen", command=löschen).pack(pady=(0, 10))

    def speichern():
        try:
            THEME[aktuell.get()] = {k: e.get() for k, e in einträge.items()}
            with open(speicherpfad, "w") as f:
                json.dump(THEME, f, indent=2)
            messagebox.showinfo("Gespeichert", "Theme wurde aktualisiert.")
            popup.destroy()
        except Exception as e:
            messagebox.showerror("Fehler", f"Theme konnte nicht gespeichert werden:\\n{e}")

    def anwenden():
        THEME[aktuell.get()] = {k: e.get() for k, e in einträge.items()}
        if apply_callback:
            apply_callback(aktuell.get(), THEME)

    # Buttons einfügen (jetzt richtig eingerückt!)
    tk.Button(popup, text="💾 Speichern", command=speichern).pack(pady=(5, 2))
    tk.Button(popup, text="🔁 Anwenden (nicht speichern)", command=anwenden).pack()

    aktuell.trace_add("write", lambda *_: aktualisiere_feld())
    aktualisiere_feld()
