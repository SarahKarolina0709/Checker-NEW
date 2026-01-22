# Bericht Migration Parität – Checkliste (Stand 2025-08-23)

## Übersicht

Alle ehemaligen `improved_report_step*` Varianten wurden als `Bericht_*` migriert. Ziel dieser Checkliste: Nachweis 1:1 Funktionsumfang vor Refactoring / Konsolidierung.

## Mapping Tabelle

| Legacy | Neuer Name | Fokus | Status |
|--------|-----------|-------|--------|
| improved_report_step1.html | Bericht_Basis.html | Basis / Grundlayout | MIGRIERT |
| improved_report_step2a.html | Bericht_Filter.html | Filter + Suche (einfach) | MIGRIERT |
| improved_report_step2b.html | Bericht_Export.html | Export-zentriert | MIGRIERT |
| improved_report_step2c.html | Bericht_Interaktiv.html | Volle Interaktion (Notizen+Kommentare+Team) | MIGRIERT |
| improved_report_step3a.html | Bericht_Core_A.html | Performance-optimiert | MIGRIERT |
| improved_report_step3b.html | Bericht_Core_B.html | Modernes UI/UX | MIGRIERT |
| improved_report_step3c1.html | Bericht_Core_C1.html | Core C1 Variante | MIGRIERT |
| improved_report_step3c3.html | Bericht_Core_C3.html | Core C3 Variante | MIGRIERT |
| improved_report_step3d1.html | Bericht_Core_D1.html | Core D1 Variante | MIGRIERT |
| improved_report_step3d2.html | Bericht_Core_D2.html | Core D2 Variante | MIGRIERT |

## Feature-Parität Matrix (Auszug wichtiger Achsen)

Legende: ✓ vorhanden, – nicht vorgesehen in Variante

| Feature / Module | Basis | Filter | Export | Interaktiv | Core_A | Core_B | C1 | C3 | D1 | D2 |
|------------------|:----:|:-----:|:-----:|:---------:|:-----:|:-----:|:--:|:--:|:--:|:--:|
| Filter Priorität  | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Filter Kategorie  | ✓ | ✓ | ✓ | ✓ | ✓ | (nur Priorität+Status?) | ✓ | ✓ | ✓ | ✓ |
| Filter Status (markiert/erledigt/Notizen) | – | – | – | ✓ | ✓ (markiert/erledigt/Notizen/Kommentare?) | ✓ | ✓ | ✓ | ✓ | ✓ |
| Suche Text        | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Notizen           | – | – | – | ✓ (Notizen + Kommentare + Undo) | ✓ (Notizen) | ✓ (Notizen) | ✓ | ✓ | ✓ | ✓ |
| Kommentare        | – | – | – | ✓ | – | – | – | – | – | – |
| Markieren         | – | – | – | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Erledigt/Resolve  | – | – | – | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Export PDF        | – | – | ✓ | ✓ | (Basis?) | (Placeholder) | ✓ | ✓ | ✓ | ✓ |
| Export CSV/Excel  | – | – | ✓ | ✓ | – | – | ✓ | ✓ | ✓ | ✓ |
| Export JSON       | – | – | ✓ | ✓ | – | – | ✓ | ✓ | ✓ | ✓ |
| Export Copy/Clipboard | – | – | ✓ | ✓ | – | – | ✓ | ✓ | ✓ | ✓ |
| Team Export JSON  | – | – | – | ✓ | – | – | – | – | – | – |
| Progress Bar      | – | – | – | ✓ | – | – | – | – | – | – |
| Undo Toast (Notiz/Kommentar Löschung) | – | – | – | ✓ | – | – | – | – | – | – |
| Lokaler Speicher Fortschritt | – | – | – | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Tastaturkürzel (Ctrl+S/F) | – | – | – | – | – | ✓ | – | – | – | – |
| Accessibility ARIA pressed | – | – | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

(Hinweis: Feinabgleich C1/C3/D1/D2 nach Bedarf ergänzen – aktuelle Tabelle fokussiert auf neue Hauptvarianten.)

## Offene Validierungsaktionen

1. Sichtkontrolle: Alle migrierten Dateien lokal im Browser öffnen (kein JS Fehler in Console).
2. Filter-Funktion: Kombination von Priorität + Kategorie + Status testweise anwenden (Interaktiv, Core_A/B).
3. Export Smoke-Test (Export & Interaktiv): PDF Druckdialog öffnet; CSV/JSON Dateien mit korrekter BOM (CSV) und UTF-8.
4. Persistenz-Test (Core_A/B/Interaktiv): Markieren + Notiz anlegen → Speichern → Reload → Zustand bleibt erhalten.
5. Accessibility-Stati: Buttons mit aria-pressed togglen korrekt (Developer Tools prüfen).
6. Edge Case Suche: Leere Suche, Groß-/Kleinschreibung, diakritische Zeichen (Normierungsfunktion).

## Geplante Nacharbeiten (Post-Parität Phase)

- Konsolidierung: debounce(), norm(), buildCSV(), downloadBlob() zentralisieren (DRY).
- Entfernen sämtlicher Emoji/Icons falls UI-Policy „No Icons“ auf HTML-Variante ausgeweitet werden soll.
- Design-System Angleichung: Farben/Tokens an zentrales design_system übertragen (Hex ↔ Token Mapping).
- Barrierefreiheit: ARIA Rollen/Labels ergänzen (role="list", role="listitem", aria-live Regionen).
- Performance: Lazy Rendering für lange Issue-Listen (IntersectionObserver).
- Security: Sanitizing für dynamische Notiz-/Kommentar-Einträge (innerText statt innerHTML, falls erweitert).
- Build Pipeline: Optional Preprocessing Schritt für Minifizierung & Hashing.

## Quick Review Ergebnisse (initial)

- Alle Ziel-Dateien vorhanden ✓
- Parität: Export-Funktionen in Export + Interaktiv ✓
- Notiz/Kommentar-Funktion nur Interaktiv (Intentional) ✓
- Tastaturkürzel nur UI/UX Variante (Core_B) ✓
- Keine Refactors vorgenommen ✓

## Entscheidungspunkt

Freigabe für Start der Konsolidierungs-/Refactoring-Phase nach Abschluss der Validierungsschritte 1–6.

---

Erstellt automatisch am 2025-08-23 (Paritätssicherung).
