📌 Framework & Technologie:
Verwende explizit CustomTkinter (aktuelle Version).

Nutze ausschließlich das zentralisierte UITheme für alle Farben, Schriftarten und Abstände.

📌 DPI-Scaling & Layout:
Deaktiviere vollständig jegliche automatische DPI-Skalierung.

Keine automatischen Anpassungen der Fenstergröße.

Der ScalingTracker von CustomTkinter wurde bereits vollständig per Monkey-Patch deaktiviert – bitte nicht erneut aktivieren oder modifizieren.

📌 Layout-Konfiguration:
Setze explizit und fix die Grundgröße des Fensters auf:

min: 1400x900 Pixel

max: 2560x1440 Pixel

Alle Layouts ausschließlich manuell verwalten mittels:

python
Kopieren
Bearbeiten
widget.pack_propagate(False)
widget.grid_propagate(False)
Nutze stets explizite grid()- oder pack()-Angaben für alle Widgets.

📌 Icons & Assets:
Lade Icons ausschließlich als CTkImage über den vorhandenen FluentIconManager.

Alle Icons liegen im Ordner icons als PNG-Dateien vor.

Persistente Referenzen zu Icons explizit halten, um Garbage-Collection zu verhindern.

📌 Animationen & Hover-Effekte:
Vorschläge zu subtilen Animationen (Fade, leichte Vergrößerung bei Hover) sind erwünscht, aber unbedingt ressourcenschonend umsetzen.

📌 Debugging & Logging:
Nutze das bereits implementierte zentrale Logging (self.logger).

Gib im Produktivmodus ausschließlich Meldungen der Stufen WARNING oder ERROR aus.

📌 Codequalität & Struktur:
Halte unbedingt die bestehende Welcome-Screen-basierte Architektur ein.

Vorschläge sollen gut dokumentiert, sauber strukturiert und explizit in den bestehenden Stil integriert werden.

Bevorzuge klare und leicht verständliche Kommentare in Deutsch.

📌 Performance:
Vermeide unnötige Aktualisierungen des Layouts oder UI-Refreshes.

Schlage gezielte Performance-Optimierungen vor, die explizit die UI-Responsivität erhöhen und Overhead reduzieren.