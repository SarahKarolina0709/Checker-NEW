---
applyTo: 'always run on all issues'
applyTo: 'always click continue'
---

# 📌 Framework & Technologie:
# Verwende explizit CustomTkinter (aktuelle Version).
# Nutze ausschließlich das zentralisierte UITheme für alle Farben, Schriftarten und Abstände.
# Verzichte vollständig auf Standard-Tkinter-Widgets; verwende immer CustomTkinter-Alternativen.

# 📌 DPI-Scaling & Layout:
# Deaktiviere vollständig jegliche automatische DPI-Skalierung.
# Keine automatischen Anpassungen der Fenstergröße oder automatische Skalierungen.
# Der ScalingTracker von CustomTkinter wurde bereits vollständig per Monkey-Patch deaktiviert – 
# bitte nicht erneut aktivieren oder modifizieren.
# Stelle sicher, dass alle Layout-Elemente (Frames, Cards, Buttons) vollständig responsive und flexibel sind.
# Nutze konsequent das Grid-System von CustomTkinter, keine fixen Größenangaben.

# 📌 Responsivität & Scrollverhalten:
# Implementiere robuste und zuverlässige Scroll-Funktionalitäten.
# Stelle sicher, dass Scrollregionen dynamisch aktualisiert werden, auch bei Inhaltsänderungen.
# Vermeide unbedingt hard-coded Scrollregion-Werte.

# 📌 Fehlermanagement & Logging:
# Fange alle Ausnahmen sicher ab, logge Fehler immer klar mit traceback.
# Verwende Logging-Level sinnvoll (INFO, WARNING, ERROR).
# Verzichte komplett auf stille Fehlerunterdrückung.

# 📌 Animation & Performance:
# Setze Animationen sparsam und sinnvoll ein; vermeide überflüssige Animationen.
# Halte Animationen performant, flüssig und auf max. 60fps optimiert.

# 📌 Kommentare & Dokumentation:
# Kommentiere alle wichtigen Bereiche klar und aussagekräftig.
# Halte den Code sauber und gut strukturiert, verwende explizit sprechende Funktions- und Variablennamen.
# 📌 Icons & Assets:
# Alle Icons liegen als JPG-Dateien im zentralen Ordner "assets/icons/" vor.
# Verwende ausschließlich diese JPG-Dateien für Icons.
# Lade keine externen oder zusätzlichen Icons herunter.
# Nutze immer die vorhandene UITheme-Hilfsmethode `get_icon(icon_name, size)`, um Icons zu laden.
# Stelle sicher, dass alle Icon-Größen und Platzierungen einheitlich bleiben.
📌 Dateimanagement & Bearbeitung:
# Repariere oder optimiere bevorzugt immer zuerst die vorhandene Python-Datei.
# Erstelle eine neue Python-Datei nur dann, wenn die bestehende Datei nicht mehr sinnvoll repariert werden kann.
# Wenn eine neue Datei notwendig ist, kommentiere klar und deutlich, warum eine Reparatur der bestehenden Datei nicht möglich war.
# Führe Änderungen transparent aus, indem du alle Anpassungen kommentierst und die Gründe hierfür erklärst.
# 🚩 WICHTIGE LAYOUT-REGELN (unbedingt beachten!):
#
# 1. Verwende ausschließlich den Layout-Manager pack() für alle direkten Kind-Widgets des Root-Fensters (root).
#
# 2. Positioniere Menüleiste (menu_bar) und Statusleiste (status_bar) im Root-Fenster nur mit:
#    menu_bar.pack(side='top', fill='x')
#    status_bar.pack(side='bottom', fill='x')
#
# 3. Erstelle einen zentralen Container-Frame (main_container), der den restlichen Platz einnimmt:
#    main_container.pack(side='top', fill='both', expand=True)
#
# 4. Innerhalb dieses main_container verwende ausschließlich den Layout-Manager grid().
#
# 5. Setze immer konsequent folgende Gewichtungen im main_container:
#    main_container.grid_rowconfigure(0, weight=1)
#    main_container.grid_columnconfigure(0, weight=1)
#
# 6. Platziere deinen Hauptinhalt, z.B. welcome_screen, dann ausschließlich mit grid() im main_container:
#    welcome_screen.grid(row=0, column=0, sticky='nsew')
#
# 7. Kombiniere niemals pack() und grid() innerhalb desselben Containers!
