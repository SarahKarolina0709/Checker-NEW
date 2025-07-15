# 📁 Kundenmanagement-Logik für CheckerApp

## 🧭 Ziel
Die CheckerApp verwaltet Kundendaten, Uploads und Projektordner basierend auf einer lokal organisierten Dateistruktur. Die Lösung ist leichtgewichtig (keine Datenbank), modular, robust und durch einen intelligenten Kalender visuell erweiterbar.

---

## ⚙️ Funktionen im Überblick

### 1. Kundenverwaltung
- Kunden werden über eine JSON-Datei (`customers.json`) gepflegt.
- Jeder Kunde erhält ein Kürzel (z. B. MUE für Müller GmbH).
- Fuzzy-Matching soll genutzt werden, um ähnliche Namen zu erkennen.
- Bei Mehrdeutigkeit erfolgt eine Rückfrage:
  > „Meinten Sie 'Müller GmbH (MUE)'?“

---

### 2. Uploadprozess

#### Ablauf:
- Vor Upload muss ein Kunde ausgewählt oder neu angelegt werden.
- Der Nutzer kann einen oder mehrere Texte hochladen.
- Wenn ein Kunde mehrmals am selben Tag Texte liefert:
  - Option: Bestehenden Tagesordner verwenden
  - Oder: Neuen Ordner mit Zeitstempel anlegen (z. B. `2025-07-12_1430`)

#### Zielverzeichnis:
- Upload-Dateien werden automatisch verschoben in:
  ```
  ./kunden/<KÜRZEL>/<YYYY-MM-DD>/
  ```

- Innerhalb dieses Ordners sollten strukturierte Unterordner vorhanden sein:
  - `Ausgangstexte`
  - `Übersetzung`
  - `Fertig` (oder weitere Workflows)

---

### 3. Kalender (SmartUploadCalendar)

#### Funktionen:
- Visualisiert Upload-Tage im Monatsraster
- Farbcodes:
  - **Grün:** Heute
  - **Blau:** Upload-Tag
  - **Grau:** Normaler Tag
- Tooltip zeigt:
  - 📅 Datum
  - 👤 Kunde
  - 🎯 Projektname
  - 📄 Anzahl der Ausgangstexte
- Klick auf Tag mit Upload:
  - Öffnet Projektdialog mit allen Uploads des Tages
  - Sortierung der Projekte nach Kundenname
  - Projekte ohne Ausgangstexte werden ausgeblendet
- Klick auf Tag ohne Upload:
  - GUI-Meldung: „Für diesen Tag liegen keine Uploads vor“

---

### 4. Dynamik & Aktualisierung

- Nach jedem Upload muss der Kalender aktualisiert werden:
  ```python
  calendar.reload()
  ```

- Diese Methode:
  - Lädt alle Daten neu
  - Ruft `update_calendar()` auf

---

### 5. Design / UI-Anpassung

- Farben im Kalender sollen dynamisch an das Dark-/Light-Theme angepasst werden
- Feste Hex-Werte (z. B. `#2D5AA0`) möglichst ersetzen durch ThemeManager-Zugriffe:
  ```python
  ctk.ThemeManager.theme["CTkButton"]["fg_color"]
  ```

---

### 6. Fehlerbehandlung & Schutz

- Kein Upload möglich, wenn kein Kunde ausgewählt wurde
- Wenn der Upload-Ordner nicht erstellt werden kann → Fehlermeldung anzeigen
- Workflows dürfen unabhängig vom Kunden ausgewählt werden
- Projekte mit 0 Dateien sollen:
  - Nicht im Kalender angezeigt werden
  - Optional mit Hinweis im Tooltip versehen werden

---

### 7. Technische Ergänzungen

- Projektverzeichnisse sollten `YYYY-MM-DD_<Projektname>` als Format nutzen
- Optionale Projektverlinkung zu bestehenden Ordnern zulassen
- Logging-Mechanismus optional ergänzbar (`upload_log.json`), z. B.:
  ```json
  [
    {
      "kunde": "MUE",
      "datum": "2025-07-12",
      "dateiname": "angebot.docx",
      "projekt": "Website Übersetzung"
    }
  ]
  ```

---

## ✅ Ziel für Copilot

Copilot soll bei folgenden Aufgaben unterstützen:

- Kundenwahl und -anlage
- Uploadlogik und Ordnerstrukturierung
- Kalenderintegration und Tooltip-Anzeige
- Fehlerabfang und Benutzerinteraktion
- Reload-Mechanik zur Synchronisierung
- UI-Anpassung für Theme-Kompatibilität
- Sortierung und intelligente Darstellung im Dialog
