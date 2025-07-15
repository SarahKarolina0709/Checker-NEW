# Cleanup Commands für Customer-Management Dateien

## Option 1: Sicher archivieren (empfohlen)
```powershell
# Archive-Ordner erstellen und Legacy-Dateien verschieben
python cleanup_customer_files.py
```

## Option 2: Test-Dateien aufräumen (optional) 
```powershell
# Nur Test-Dateien in test_archive verschieben
mkdir test_archive
move demo_customer_section_calls.py test_archive/
move live_test_customer_section.py test_archive/  
move test_customer_section_integration.py test_archive/
move customer_section_test_utils.py test_archive/
move test_modern_customer_ui.py test_archive/
move test_customer_management.py test_archive/
```

## Option 3: Status prüfen (jederzeit)
```powershell
python analyze_duplicate_files.py
```

## ✅ Nach dem Cleanup aktive Architektur:
1. **checker_app.py** -> Haupteinstiegspunkt  
2. **show_customer_menu()** -> Prioritätssystem:
   - Priorität 1: CustomerSectionComplete  
   - Priorität 2: SimplifiedModernCustomerUI
   - Priorität 3: ui_modernizer fallback

## 📊 Dateien-Statistik:
- **Aktiv:** 3 Dateien (196KB)
- **Legacy:** 4 Dateien (98KB) -> Archivieren  
- **Integration:** 2 Dateien (47KB) -> Löschen/Archivieren
- **Tests:** 6 Dateien (30KB) -> Optional aufräumen

**Gesamte Einsparung:** ~175KB und deutlich übersichtlichere Struktur!
