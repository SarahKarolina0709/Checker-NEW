# Welcome Screen Components - Übersicht und Verwendung

Dieses Dokument erklärt die verschiedenen Welcome Screen Komponenten und ihre Verwendung.

## Customer Section Komponenten

### 🟢 **CustomerSectionV2** (Produktionsversion)
- **Datei**: `welcome_screen_components/customer_section_v2.py`
- **Status**: ✅ **AKTIVE PRODUKTIONSVERSION**
- **Verwendung**: Hauptanwendung, alle neuen Entwicklungen
- **Features**: 
  - Erweiterte Projektauswahl
  - Neues Projekt-Dialog
  - Recent Projects Liste
  - Intelligente Kundenerkennung
  - Modernes scrollbares UI

### 🟡 **CustomerSection** (Basic Version)
- **Datei**: `welcome_screen_components/customer_section.py`
- **Status**: ⚠️ **NUR FÜR TESTS/KOMPATIBILITÄT**
- **Verwendung**: Vereinfachte Tests, Legacy-Unterstützung
- **Features**: Basis-Funktionalität ohne erweiterte Projektauswahl

### 🟡 **CustomerSectionComplete** (Transitional Version)
- **Datei**: `welcome_screen_components/customer_section_complete.py`
- **Status**: ⚠️ **ÜBERGANGSVERSION**
- **Verwendung**: Kompatibilität mit bestehenden Test-Scripts
- **Features**: Vollständige Funktionalität, aber nicht die neueste API

### 🔵 **CustomerSectionWithCalendar** (Spezialisierte Version)
- **Datei**: `welcome_screen_components/customer_section_with_calendar.py`
- **Status**: 🎯 **SPEZIALISIERT FÜR KALENDER-WORKFLOWS**
- **Verwendung**: Workflows mit Kalender-Funktionalität
- **Features**: 
  - Alle CustomerSectionV2 Features
  - Zusätzlich: Smart Upload Calendar
  - Datums-basierte Navigation
  - Kalender-Visualisierung

### 🔴 **customer_section_v2.py** (Root - DEPRECATED)
- **Datei**: `customer_section_v2.py` (Root-Verzeichnis)
- **Status**: ❌ **DEPRECATED WRAPPER**
- **Verwendung**: Nur Weiterleitung für Rückwärtskompatibilität
- **Hinweis**: Diese Datei wird in zukünftigen Versionen entfernt

## Verwendungsrichtlinien

### ✅ Für neue Entwicklungen verwenden:
```python
from welcome_screen_components.customer_section_v2 import CustomerSectionV2
```

### ✅ Für Kalender-basierte Workflows verwenden:
```python
from welcome_screen_components.customer_section_with_calendar import CustomerSectionWithCalendar
```

### ⚠️ Nur für Tests/Kompatibilität:
```python
from welcome_screen_components.customer_section import CustomerSection
from welcome_screen_components.customer_section_complete import CustomerSectionComplete
```

### ❌ Nicht mehr verwenden:
```python
from customer_section_v2 import CustomerSectionV2  # DEPRECATED
```

## Migration Guide

Wenn Sie derzeit die deprecated Root-Datei verwenden:

### Vorher:
```python
from customer_section_v2 import CustomerSectionV2
```

### Nachher:
```python
from welcome_screen_components.customer_section_v2 import CustomerSectionV2
```

## Bereinigungsplan

1. ✅ **Sofort**: Root `customer_section_v2.py` als Deprecation Wrapper
2. 🔄 **Nächste Phase**: Aktualisierung aller Imports auf neue Pfade
3. 🗑️ **Später**: Entfernung des Deprecated Wrappers
4. 📝 **Optional**: Konsolidierung der Test-/Legacy-Versionen

## API Kompatibilität

Alle CustomerSection Varianten implementieren die gleichen Basis-Methoden:
- `get_data()` - Gibt Kundendaten zurück
- `reset_selection()` - Setzt Auswahl zurück  
- `select_customer(name)` - Wählt Kunde aus

CustomerSectionV2 und CustomerSectionWithCalendar haben zusätzliche erweiterte Methoden.
