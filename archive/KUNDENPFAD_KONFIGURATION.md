# Kundenpfad-Konfiguration - Vollständige Anleitung

## Übersicht

Sie können den Pfad für die Kundendaten in der Checker Pro Suite auf verschiedene Weise konfigurieren. Diese Anleitung zeigt Ihnen alle verfügbaren Optionen.

## Methoden zur Pfad-Konfiguration

### 1. 🎯 Über das Menü (EMPFOHLEN)

**Am einfachsten über die grafische Benutzeroberfläche:**

1. **Menü öffnen**: `Tools` → `Kundenpfad konfigurieren`
2. **Aktueller Pfad**: Wird angezeigt
3. **Neuen Pfad eingeben**: Manuell oder über "Durchsuchen" Button
4. **Optionen wählen**:
   - ✅ Ordner erstellen, falls er nicht existiert
   - ✅ Bestehende Kundendaten kopieren
5. **Übernehmen**: Sofort aktiv

**Vorteile:**
- ✅ Benutzerfreundlich
- ✅ Validierung und Fehlerprüfung
- ✅ Automatisches Kopieren bestehender Daten
- ✅ Sofortige Anwendung

### 2. 📝 Über die Konfigurationsdatei

**Datei**: `kunden_config.json` (im Anwendungsverzeichnis)

```json
{
  "kunden_base_dir": "Ihr_Gewünschter_Pfad"
}
```

**Beispiele:**

```json
// Relativer Pfad (empfohlen)
{
  "kunden_base_dir": "Checker_Projekte"
}

// Absoluter Pfad Windows
{
  "kunden_base_dir": "C:\\Projekte\\Checker_Kunden"
}

// Absoluter Pfad mit Netzlaufwerk
{
  "kunden_base_dir": "\\\\Server\\Shared\\Checker_Kunden"
}

// Benutzerprofil
{
  "kunden_base_dir": "C:\\Users\\IhrName\\Documents\\Checker_Kunden"
}
```

**Anwendung:**
- Anwendung neu starten für Aktivierung
- JSON-Syntax beachten (Backslashes escapen: `\\`)

### 3. 🔧 Programmatisch (für Entwickler)

```python
# Im Code der Checker-App
app.speichere_kunden_base_dir("Neuer_Pfad")
app.kunden_manager = KundenManager(base_dir="Neuer_Pfad")
```

## Pfad-Optionen

### Relative Pfade
```
"Checker_Projekte"           → Anwendungsverzeichnis/Checker_Projekte
"Kunden"                     → Anwendungsverzeichnis/Kunden
"../Projekte"                → Übergeordnetes Verzeichnis/Projekte
```

### Absolute Pfade
```
"C:\\Projekte\\Kunden"       → Fester Windows-Pfad
"D:\\Backup\\Checker"        → Anderes Laufwerk
"\\\\NAS\\Projekte"          → Netzlaufwerk
```

### Spezielle Pfade
```
"%USERPROFILE%\\Documents\\Checker"    → Benutzerdokumente
"%APPDATA%\\Checker\\Projekte"         → App-Daten Ordner
```

## Ordnerstruktur

Nach der Pfad-Konfiguration wird folgende Struktur erstellt:

```
Ihr_Kundenpfad/
├── Kunde_1/
│   ├── Angebot/
│   ├── Pruefung/
│   ├── Finalisierung/
│   └── Ausgangstexte/
├── Kunde_2/
│   ├── Angebot/
│   ├── Pruefung/
│   ├── Finalisierung/
│   └── Ausgangstexte/
└── ...
```

## Empfohlene Pfade

### Für Einzelbenutzer:
```json
{
  "kunden_base_dir": "C:\\Users\\IhrName\\Documents\\Checker_Projekte"
}
```

### Für Teams (Netzwerk):
```json
{
  "kunden_base_dir": "\\\\Server\\Projekte\\Checker_Kunden"
}
```

### Für Backup-Integration:
```json
{
  "kunden_base_dir": "D:\\Backup\\Checker_Projekte"
}
```

### Standard (Anwendungsverzeichnis):
```json
{
  "kunden_base_dir": "Checker_Projekte"
}
```

## Wichtige Hinweise

### ✅ Berechtigungen
- Pfad muss **lesbar** und **schreibbar** sein
- Keine Admin-Rechte für normale Ordner erforderlich
- Bei Netzlaufwerken: Entsprechende Netzwerk-Berechtigungen

### ✅ Pfad-Validierung
Das System prüft automatisch:
- ✅ Pfad existiert oder kann erstellt werden
- ✅ Schreibberechtigung vorhanden
- ✅ Ausreichend Speicherplatz
- ✅ Gültige Pfad-Syntax

### ✅ Datenübertragung
- Bestehende Kundendaten können automatisch kopiert werden
- **Backup empfohlen** vor Pfad-Änderung
- Kopiervorgang kann bei vielen Daten dauern

### ⚠️ Wichtige Warnungen
- **Backup erstellen** vor Pfad-Änderung
- **Netzlaufwerke**: Dauerhafte Verbindung sicherstellen
- **Leerzeichen in Pfaden**: In Anführungszeichen setzen
- **Lange Pfade**: Windows hat 260-Zeichen-Limit

## Fehlerbehebung

### Problem: "Pfad nicht gefunden"
```
Lösung: 
1. Pfad-Syntax prüfen (Backslashes escapen)
2. Ordner manuell erstellen
3. Berechtigung prüfen
```

### Problem: "Zugriff verweigert"
```
Lösung:
1. Als Administrator ausführen
2. Berechtigungen anpassen
3. Anderen Pfad wählen
```

### Problem: "JSON-Fehler"
```
Lösung:
1. JSON-Syntax prüfen
2. Backslashes verdoppeln: C:\\Pfad
3. Keine Kommentare in JSON
```

### Problem: "Daten nicht kopiert"
```
Lösung:
1. Ausreichend Speicherplatz sicherstellen
2. Quelldaten vorhanden prüfen
3. Berechtigungen für beide Pfade prüfen
```

## Beispiel-Workflows

### Szenario 1: Lokaler Pfad
1. `Tools` → `Kundenpfad konfigurieren`
2. Pfad: `C:\Projekte\Checker_Kunden`
3. ✅ `Ordner erstellen`
4. ✅ `Daten kopieren`
5. `Übernehmen`

### Szenario 2: Netzlaufwerk
1. Netzlaufwerk verbinden (z.B. Z:)
2. `Tools` → `Kundenpfad konfigurieren`
3. Pfad: `Z:\Checker_Projekte`
4. ✅ `Ordner erstellen`
5. ✅ `Daten kopieren`
6. `Übernehmen`

### Szenario 3: Standard zurücksetzen
1. `Tools` → `Kundenpfad konfigurieren`
2. `Standard` Button klicken
3. `Übernehmen`

## Status prüfen

**Aktueller Pfad anzeigen:**
- `Tools` → `Kundenpfad konfigurieren` → Aktueller Pfad wird angezeigt
- Oder: `Menü` → `Kunden` → `Kundenordner öffnen`

**Konfigurationsdatei prüfen:**
```bash
# Anzeigen der aktuellen Konfiguration
notepad kunden_config.json
```

## Support

Bei Problemen mit der Pfad-Konfiguration:

1. **Logs prüfen**: `checker_app.log`
2. **Standard wiederherstellen**: `Standard` Button verwenden
3. **Konfigurationsdatei löschen**: Für kompletten Reset
4. **Neu starten**: Nach manuellen Änderungen

---

**Status**: ✅ Vollständig implementiert
**Kompatibilität**: Windows, Netzlaufwerke, USB-Laufwerke
**Version**: 2.0.1
**Letzte Aktualisierung**: Juli 2025
