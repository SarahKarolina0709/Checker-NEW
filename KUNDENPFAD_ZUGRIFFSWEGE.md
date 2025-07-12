# Kundenpfad-Konfiguration - Zugriffswege

## 🎯 Übersicht

Die Kundenpfad-Konfiguration ist über **mehrere Wege** in der Checker Pro Suite verfügbar:

## 📋 Zugriffswege

### 1. **Tools-Menü** 🔧
- **Menü**: `Tools` → `Kundenpfad konfigurieren`
- **Funktion**: `configure_customer_path()`
- **Icon**: 📁 (Folder)

### 2. **Kunden-Menü** 👥
- **Menü**: `Kunden` → `Kundenpfad konfigurieren`
- **Funktion**: `configure_customer_path()`
- **Icon**: 📁 (Folder)

## 🚀 Funktionalität

### Konfigurationsdialog
- **Titel**: "Kundenpfad konfigurieren"
- **Größe**: 600x400 Pixel (resizable)
- **Modal**: Ja (blockiert andere Fenster)

### Features
- ✅ **Aktueller Pfad anzeigen**
- ✅ **Neuen Pfad eingeben** (mit Validierung)
- ✅ **Ordner durchsuchen** (Browse-Dialog)
- ✅ **Ordner automatisch erstellen** (optional)
- ✅ **Bestehende Daten kopieren** (optional)
- ✅ **Konfiguration speichern** (in `kunden_config.json`)

### Optionen
- **Ordner erstellen**: Falls der neue Pfad nicht existiert
- **Daten kopieren**: Bestehende Kundendaten in neuen Pfad übertragen
- **Backup erstellen**: Vor dem Wechsel (automatisch)

## 📁 Konfigurationsdatei

```json
{
    "customer_base_path": "C:\\Projekte\\Checker_Kunden",
    "last_updated": "2024-01-XX",
    "backup_enabled": true
}
```

## 🔧 Verwendung

### Über das Menü
1. Öffne die Checker Pro Suite
2. Klicke auf **"Tools"** oder **"Kunden"** in der oberen Menüleiste
3. Wähle **"Kundenpfad konfigurieren"**
4. Konfiguriere den gewünschten Pfad
5. Bestätige mit **"Speichern"**

### Programmatisch
```python
# Konfiguration laden
config = load_customer_config()

# Pfad ändern
config['customer_base_path'] = "C:\\Neue\\Struktur"

# Konfiguration speichern
save_customer_config(config)
```

## 🛡️ Sicherheit

- **Validierung**: Pfade werden auf Gültigkeit geprüft
- **Backup**: Automatische Sicherung vor Änderungen
- **Rollback**: Möglichkeit zum Rückgängigmachen
- **Berechtigungen**: Prüfung auf Schreibrechte

## 🎨 Benutzerfreundlichkeit

- **Intuitive UI**: Klare Beschriftungen und Icons
- **Fehlerbehandlung**: Verständliche Fehlermeldungen
- **Fortschrittsanzeige**: Bei längeren Operationen
- **Hilfe-Tooltips**: Für alle Optionen

## 📍 Implementierungsdetails

### Dateien
- `checker_app.py`: Hauptimplementierung
- `kunden_config.json`: Konfigurationsdatei
- `kunden_manager.py`: Verwaltungslogik

### Funktionen
- `configure_customer_path()`: Hauptdialog
- `load_customer_config()`: Konfiguration laden
- `save_customer_config()`: Konfiguration speichern
- `validate_customer_path()`: Pfad validieren

## ✅ Tests

### Automatisierte Tests
```bash
python test_menu_structure.py
python demo_path_configuration.py
```

### Manuelle Tests
1. Menüzugriff über Tools
2. Menüzugriff über Kunden
3. Pfad-Konfiguration
4. Daten-Migration
5. Fehlerbehandlung

## 🎉 Status

✅ **Vollständig implementiert**
✅ **In beiden Menüs verfügbar**
✅ **Getestet und validiert**
✅ **Dokumentiert**

---

**Letzte Aktualisierung**: Januar 2024
**Version**: 1.0
**Status**: Produktiv
