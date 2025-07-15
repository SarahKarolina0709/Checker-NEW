"""
Icon-System Anleitung und Beispiele
=====================================

Das Fluent Icons System in der Checker-App ermöglicht es, Icons dynamisch anzupassen
und zu verwalten. Hier ist eine Übersicht über die verfügbaren Funktionen:

## 1. Grundlegende Icon-Verwendung

```python
from fluent_icons_manager import FluentIconManager

# Icon-Manager initialisieren
icon_manager = FluentIconManager()

# Icons abrufen
home_icon = icon_manager.get_icon('home')          # 🏠
workflow_icon = icon_manager.get_icon('workflow')  # ⚡
user_icon = icon_manager.get_icon('user')          # 👤
```

## 2. Verfügbare Icon-Kategorien

### Navigation & Actions
- home: 🏠
- search: 🔍
- settings: ⚙️
- help: ❓
- close: ❌
- menu: ☰

### Files & Documents  
- file: 📄
- folder: 📁
- save: 💾
- export: 📤
- import: 📥
- upload: ⬆️

### Workflows & Processes
- workflow: ⚡
- process: 🔄
- check: ✅
- warning: ⚠️
- error: ❌
- success: ✅

### User & Customer
- user: 👤
- customer: 👥
- profile: 👤
- account: 🔐

### Status & Feedback
- loading: ⟳
- spinner: 🔄
- complete: ✅
- pending: ⏳

### Dark/Light Mode
- light_mode: ☀️
- dark_mode: 🌙
- theme: 🎨

## 3. Custom Icons erstellen

```python
# Neues Icon hinzufügen
icon_manager.set_custom_icon('rocket', '🚀')
icon_manager.set_custom_icon('star', '⭐')

# Custom Icon verwenden
rocket_icon = icon_manager.get_icon('rocket')  # 🚀
```

## 4. Theme-Wechsel

```python
# Theme ändern
icon_manager.set_theme('fluent')   # Fluent Design
icon_manager.set_theme('minimal')  # Minimalistisch
icon_manager.set_theme('classic')  # Klassisch
icon_manager.set_theme('custom')   # Benutzerdefiniert
```

## 5. Icon-Suche

```python
# Icons suchen
results = icon_manager.search_icons('file')
# Gibt alle Icons zurück, die 'file' im Namen enthalten

# Alle verfügbaren Icons
all_icons = icon_manager.get_all_available_icons()
```

## 6. Verwendung in der Welcome Screen

In der `modern_welcome_screen.py` werden Icons folgendermaßen verwendet:

```python
# Icon-Manager initialisieren (wird automatisch gemacht)
self.icon_manager = FluentIconManager()

# Icons in UI-Elementen verwenden
def get_ui_icon(self, icon_name, fallback=""):
    if self.icon_manager:
        return self.icon_manager.get_icon(icon_name, fallback)
    return fallback

# Beispiel: Button mit Icon
button = ctk.CTkButton(
    text=f"{self.get_ui_icon('workflow')} Neuer Workflow",
    # ...weitere Parameter
)

# Beispiel: Status-Nachricht mit Icon  
self.update_status_with_icon(
    self.get_ui_icon('success'), 
    "Workflow erfolgreich gestartet", 
    "success"
)
```

## 7. Icon-Anpassung über UI

Die Welcome Screen bietet einen integrierten Dialog zur Icon-Anpassung:

1. **Settings-Menü öffnen** (⚙️ Icon oben rechts)
2. **"Icon-Anpassung"** auswählen
3. **Theme wechseln** über Dropdown-Menü
4. **Verfügbare Icons ansehen** in der Liste
5. **Icons exportieren** über Export-Button

## 8. Konfigurationsdatei

Icons werden in `fluent_icons_config.json` gespeichert:

```json
{
  "theme": "fluent",
  "use_unicode_fallback": true,
  "custom_icons": {
    "rocket": "🚀",
    "star": "⭐"
  },
  "version": "1.0"
}
```

## 9. Fallback-System

Das Icon-System hat ein robustes Fallback-System:

1. **Custom Icons** werden zuerst geprüft
2. **Fluent Icons** als Standard-Set
3. **Unicode Alternativen** für Kompatibilität
4. **Fallback-Icon** wenn nichts gefunden wird

## 10. Erweiterte Funktionen

### Icon-Export
```python
# Icon-Liste exportieren
success = icon_manager.export_icon_list("my_icons.json")
```

### Theme-spezifische Icons
```python
# Je nach Theme können Icons variieren
if icon_manager.icon_theme == "minimal":
    # Einfachere Icon-Varianten verwenden
    pass
```

### Performance-Optimierung
- Icons werden gecacht
- Nur benötigte Icons werden geladen
- Konfiguration wird nur bei Änderungen gespeichert

## 11. Integration in eigene Komponenten

```python
class MyComponent:
    def __init__(self, icon_manager):
        self.icon_manager = icon_manager
    
    def create_button(self, icon_name, text):
        icon = self.icon_manager.get_icon(icon_name)
        return ctk.CTkButton(text=f"{icon} {text}")
```

## Fazit

Das Fluent Icons System bietet:
- ✅ **Konsistente Icon-Verwendung** app-weit
- ✅ **Einfache Anpassung** über UI oder Code
- ✅ **Theme-Support** für verschiedene Designs
- ✅ **Robustes Fallback-System** für Kompatibilität
- ✅ **Performance-Optimierung** durch Caching
- ✅ **Erweiterbarkeit** für neue Icons und Themes

Die Icons verbessern die Benutzerfreundlichkeit und machen die App visuell ansprechender!
"""
