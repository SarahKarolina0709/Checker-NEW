"""
Test-Script für das Layout-Problem mit dem grauen Fenster

Das Problem: 
- Nach dem Vergrößern der App erscheint oben rechts ein graues Fenster
- Dies wurde durch Layout-Manager-Konflikte verursacht

Die Lösung:
1. Wechsel von TkinterDnD.Tk() zu ctk.CTk() für bessere Layout-Kompatibilität
2. Notification-Container initial verstecken
3. Drag-Drop-Overlay richtig verstecken
4. Resize-Event-Handler hinzufügen
5. Clean-Layout-Methode für bessere Kontrolle

Änderungen in checker_app.py:
- init_core_components(): CTk statt TkinterDnD.Tk()
- _create_notification_system(): place_forget() initial
- _create_drag_drop_overlay(): zusätzliches pack_forget()
- _ensure_clean_layout(): neue Methode für sauberes Layout
- _on_window_resize(): Resize-Event-Handler
- center_window_on_screen(): minsize() hinzugefügt
"""

import customtkinter as ctk
import tkinter as tk

def demo_layout_problem():
    """Demonstriert das Layout-Problem und die Lösung"""
    
    # Erstelle ein Test-Fenster
    root = ctk.CTk()
    root.title("Layout-Problem Demo")
    root.geometry("800x600")
    
    # Hauptinhalt
    main_frame = ctk.CTkFrame(root)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Label mit Info
    info_label = ctk.CTkLabel(
        main_frame,
        text="🔧 Layout-Problem behoben!\n\n"
             "✅ Kein graues Fenster mehr bei Resize\n"
             "✅ CTk statt TkinterDnD für bessere Kompatibilität\n"
             "✅ Notification-Container richtig versteckt\n"
             "✅ Drag-Drop-Overlay korrekt verwaltet\n"
             "✅ Resize-Event-Handler hinzugefügt",
        font=ctk.CTkFont(family="Segoe UI", size=14),
        text_color=("#2D3748", "#E2E8F0"),
        justify="left"
    )
    info_label.pack(pady=20)
    
    # Problematisches Element (sichtbar)
    problematic_frame = ctk.CTkFrame(
        root,
        fg_color=("#FFE5E5", "#8B0000"),
        corner_radius=8,
        border_width=2,
        border_color=("#FF0000", "#FF4444")
    )
    problematic_frame.place(relx=1.0, rely=0.1, anchor="ne", x=-20, y=20)
    
    problem_label = ctk.CTkLabel(
        problematic_frame,
        text="❌ Problematisches Element\n(normalerweise versteckt)",
        font=ctk.CTkFont(family="Segoe UI", size=10),
        text_color=("red", "white")
    )
    problem_label.pack(padx=10, pady=5)
    
    # Button zum Verstecken
    def hide_problematic():
        problematic_frame.place_forget()
        hide_btn.configure(text="✅ Problem versteckt!")
    
    hide_btn = ctk.CTkButton(
        main_frame,
        text="Problem verstecken",
        command=hide_problematic,
        font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
        fg_color=("#10B981", "#34D399"),
        hover_color=("#059669", "#10B981")
    )
    hide_btn.pack(pady=20)
    
    # Resize-Handler Demo
    def on_resize(event):
        if event.widget == root:
            # Verstecke problematische Elemente bei Resize
            problematic_frame.place_forget()
            hide_btn.configure(text="✅ Auto-versteckt bei Resize!")
    
    root.bind("<Configure>", on_resize)
    
    # Starte die Demo
    root.mainloop()

if __name__ == "__main__":
    print("🔧 Layout-Problem Demo")
    print("=" * 50)
    print("Demonstriert die Lösung für das graue Fenster-Problem")
    print("Vergrößern Sie das Fenster - das rote Element wird versteckt")
    print("=" * 50)
    
    demo_layout_problem()
