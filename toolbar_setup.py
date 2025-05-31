
import tkinter as tk
from tooltip import Tooltip

def create_toolbar(root, icons, callbacks):
    toolbar = tk.Frame(root, bg="#2a2a2a")
    toolbar.pack(fill="x", padx=5, pady=(10, 5))

    buttons = {
        "export_pdf": tk.Button(toolbar, image=icons["export_pdf"], command=callbacks["export_pdf"], bg="#2a2a2a", bd=0),
        "export_score": tk.Button(toolbar, image=icons["export_score"], command=callbacks["export_score"], bg="#2a2a2a", bd=0),
        "mail": tk.Button(toolbar, image=icons["mail"], command=callbacks["mail"], bg="#2a2a2a", bd=0),
        "kommentar": tk.Button(toolbar, image=icons["kommentar"], command=callbacks["kommentar"], bg="#2a2a2a", bd=0),
        "ordner": tk.Button(toolbar, image=icons["ordner"], command=callbacks["ordner"], bg="#2a2a2a", bd=0),
        "vergleich": tk.Button(toolbar, image=icons["vergleich"], command=callbacks["vergleich"], bg="#2a2a2a", bd=0),
        "theme": tk.Button(toolbar, image=icons["theme"], command=callbacks["theme"], bg="#2a2a2a", bd=0),
        "save": tk.Button(toolbar, image=icons["save"], command=callbacks["save"], bg="#2a2a2a", bd=0),
        "close": tk.Button(toolbar, image=icons["close"], command=callbacks["close"], bg="#2a2a2a", bd=0)
    }

    tooltips = {
        "export_pdf": "PDF für Übersetzer exportieren",
        "export_score": "PDF mit Score exportieren",
        "mail": "E-Mail anzeigen",
        "kommentar": "Kommentar an Übersetzer",
        "ordner": "Kundenordner öffnen",
        "vergleich": "Vergleich starten",
        "theme": "Theme wechseln",
        "save": "Profil speichern",
        "close": "App schließen"
    }

    for key, btn in buttons.items():
        btn.pack(side="left", padx=4)
        Tooltip(btn, tooltips[key])
        btn.image = icons[key]  # wichtig für Tkinter!

    return toolbar
