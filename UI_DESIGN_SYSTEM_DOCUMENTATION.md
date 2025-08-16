# 🎨 UI DESIGN SYSTEM DOCUMENTATION
=========================================

Diese Dokumentation beschreibt das zentrale Design System für die Translation Quality Checker Anwendung.

## 🎯 DESIGN SYSTEM ÜBERSICHT

Das Design System gewährleistet Konsistenz und Wartbarkeit durch zentrale Verwaltung aller visuellen Eigenschaften.

### 🎨 FARB-SYSTEM

#### Primäre Farben:
- **Primary:** `#1F4E79` (Hauptaktionen, wichtige Buttons)
- **Primary Hover:** `#1A3F65` (Hover-Zustand primärer Elemente)
- **Primary Light:** `#EEF2FF` (Hintergrund für primäre Bereiche)
- **Primary Dark:** `#1A3F65` (Verstärkung primärer Elemente)

#### Sekundäre Farben:
- **Secondary:** `#6C757D` (Sekundäre Aktionen, weniger wichtige Buttons)
- **Secondary Hover:** `#5A6268` (Hover-Zustand sekundärer Elemente)
- **Secondary Light:** `#F8F9FA` (Neutrale Hintergründe)
- **Secondary Dark:** `#495057` (Verstärkung sekundärer Elemente)

#### Semantische Farben:
- **Success:** `#22C55E` (Erfolgsmeldungen, positive Zustände)
- **Success Hover:** `#16A34A` (Hover-Zustand für Success-Elemente)
- **Warning:** `#F59E0B` (Warnungen, Aufmerksamkeit erforderlich)
- **Warning Hover:** `#D97706` (Hover-Zustand für Warning-Elemente)
- **Error:** `#DC2626` (Fehlermeldungen, kritische Zustände)
- **Error Hover:** `#B91C1C` (Hover-Zustand für Error-Elemente)
- **Info:** `#3B82F6` (Informationen, neutrale Hinweise)
- **Info Hover:** `#2563EB` (Hover-Zustand für Info-Elemente)

#### Neutrale Farben:
- **White:** `#FFFFFF` (Hintergründe, Karten)
- **Gray 50:** `#F9FAFB` (Sehr helle Hintergründe)
- **Gray 100:** `#F3F4F6` (Hover-Zustände, Divider)
- **Gray 200:** `#E5E7EB` (Borders, Trennlinien)
- **Gray 300:** `#D1D5DB` (Input-Borders, Placeholder)
- **Gray 400:** `#9CA3AF` (Placeholder-Text, Icons)
- **Gray 500:** `#6B7280` (Sekundärer Text, Beschreibungen)
- **Gray 600:** `#4B5563` (Text in deaktivierten Zuständen)
- **Gray 700:** `#374151` (Primärer Text, Headlines)
- **Gray 800:** `#1F2937` (Sehr dunkler Text, Emphasis)
- **Gray 900:** `#111827` (Maximaler Kontrast, Überschriften)

#### Surface-Farben:
- **Surface:** `#FFFFFF` (Karten-Hintergrund, Container)
- **Surface Hover:** `#F9FAFB` (Hover-Zustand für Oberflächen)
- **Surface Elevated:** `#FFFFFF` (Erhöhte Bereiche, Dialoge)
- **Surface Border:** `#E5E7EB` (Karten-Borders, Container-Ränder)

### 🔤 TYPOGRAFIE-SYSTEM

#### Basis-Schriftart:
- **Familie:** Segoe UI (Windows-optimiert)
- **Fallback:** Arial, sans-serif

#### Größen-Hierarchie:
```
MICRO (10px):      micro
SMALL (12px):      caption, small, menu  
BODY (14px):       body, body_bold, input, button
LABEL (16px):      label, label_bold
SUBHEADING (18px): subheading, card_header
HEADING (22px):    heading, section
TITLE (26px):      title, page_title
DISPLAY (32px):    display, hero
```

#### Gewichte:
- **Normal:** 400 (Standard-Text, Beschreibungen)
- **Bold:** 700 (Überschriften, wichtige Labels)

### 📐 ABSTÄNDE & LAYOUT

#### Spacing-Scale:
```
XS: 4px    (Sehr kleine Abstände, Icon-Padding)
SM: 8px    (Kleine Abstände, Button-Padding)  
MD: 16px   (Standard-Abstände, Card-Padding)
LG: 24px   (Große Abstände, Section-Margins)
XL: 32px   (Extra große Abstände, Page-Margins)
XXL: 48px  (Sehr große Abstände, Hero-Sections)
```

#### Border-Radius:
```
SM: 4px    (Small elements, inputs)
MD: 8px    (Standard elements, buttons)
LG: 12px   (Cards, containers)
XL: 16px   (Large containers, modals)
FULL: 50%  (Circular elements, avatars)
```

## 🔧 VERWENDUNG IM CODE

### Farben abrufen:
```python
# In GUI-Klassen mit Design System Integration:
primary_color = self.get_color('primary')
text_color = self.get_color('gray_700')
surface_bg = self.get_color('surface')

# In externen Modulen:
from design_system import get_color
button_color = get_color('primary')
```

### Typografie verwenden:
```python
# Standard-Verwendung:
font = ctk.CTkFont(*self.get_typography("body"))
heading_font = ctk.CTkFont(*self.get_typography("heading"))

# Für spezielle Anforderungen:
bold_text = ctk.CTkFont(*self.get_typography("body_bold"))
```

### Abstände definieren:
```python
# Padding und Margins:
padx = self.get_spacing('md')  # 16px
pady = self.get_spacing('sm')  # 8px

# Grid-Abstände:
sticky="nsew", padx=self.get_spacing('lg'), pady=self.get_spacing('md')
```

## 🎨 KOMPONENTEN-VORLAGEN

### Button-Stile:
```python
# Primary Button (Hauptaktionen):
create_button(style='primary', text='Speichern')
# → fg_color='#1F4E79', hover_color='#1A3F65', text_color='#FFFFFF'

# Secondary Button (Nebenaktionen):
create_button(style='secondary', text='Abbrechen')  
# → fg_color='#6C757D', hover_color='#5A6268', text_color='#FFFFFF'

# Success Button (Bestätigungen):
create_button(style='success', text='Bestätigen')
# → fg_color='#22C55E', hover_color='#16A34A', text_color='#FFFFFF'

# Warning Button (Vorsicht):
create_button(style='warning', text='Warnung')
# → fg_color='#F59E0B', hover_color='#D97706', text_color='#FFFFFF'

# Danger Button (Löschungen):
create_button(style='danger', text='Löschen')
# → fg_color='#DC2626', hover_color='#B91C1C', text_color='#FFFFFF'

# Outline Button (Subtile Aktionen):
create_button(style='outline', text='Details')
# → fg_color='transparent', border_color='#D1D5DB', text_color='#374151'
```

### Card-Stile:
```python
# Standard Card:
card = create_card()
# → fg_color='#FFFFFF', border_color='#E5E7EB', corner_radius=12

# Elevated Card:
elevated_card = create_card(elevated=True)
# → fg_color='#FFFFFF', border_color='#D1D5DB', corner_radius=12, shadow=True
```

### Input-Stile:
```python
# Standard Input:
input_config = create_input_style()
entry = ctk.CTkEntry(parent, **input_config)
# → fg_color='#FFFFFF', border_color='#D1D5DB', text_color='#374151'

# Focus Input:
# → border_color='#1F4E79', fg_color='#FFFFFF'
```

## 📊 DESIGN TOKEN REFERENZ

### Layout-Token:
```
CONTAINER_MAX_WIDTH: 1200px
SIDEBAR_WIDTH: 280px
HEADER_HEIGHT: 64px
FOOTER_HEIGHT: 48px
CARD_MIN_HEIGHT: 120px
BUTTON_HEIGHT_SM: 32px
BUTTON_HEIGHT_MD: 40px
BUTTON_HEIGHT_LG: 48px
```

### Animation-Token:
```
TRANSITION_FAST: 150ms
TRANSITION_NORMAL: 250ms
TRANSITION_SLOW: 350ms
EASING_DEFAULT: ease-in-out
EASING_SPRING: cubic-bezier(0.34, 1.56, 0.64, 1)
```

### Z-Index-Scale:
```
Z_BACKGROUND: -1
Z_NORMAL: 0
Z_ELEVATED: 10
Z_STICKY: 100
Z_OVERLAY: 1000
Z_MODAL: 2000
Z_TOOLTIP: 3000
Z_NOTIFICATION: 4000
```

## 🚨 DESIGN VIOLATIONS VERMEIDEN

### ❌ Häufige Fehler:
```python
# Hartcodierte Farben:
fg_color="#1F4E79"  # ❌ FALSCH

# Hardcodierte Schriftgrößen:
font=ctk.CTkFont(size=14)  # ❌ FALSCH

# Inkonsistente Abstände:
padx=20, pady=15  # ❌ FALSCH

# Eigene Button-Farben:
button_color="#FF0000"  # ❌ FALSCH
```

### ✅ Korrekte Verwendung:
```python
# Design System Farben:
fg_color=self.get_color('primary')  # ✅ RICHTIG

# Systematische Typografie:
font=ctk.CTkFont(*self.get_typography("body"))  # ✅ RICHTIG

# Konsistente Abstände:
padx=self.get_spacing('lg'), pady=self.get_spacing('md')  # ✅ RICHTIG

# Vordefinierte Button-Stile:
create_button(style='primary', text='Button')  # ✅ RICHTIG
```

## 🔍 QUALITY CHECKS

### Automatische Prüfungen:
```bash
# Prüfe auf hartcodierte Farben:
grep -r "#[0-9A-F]\{6\}" *.py | grep -v "get_color\|Design.System"

# Prüfe auf hartcodierte Fonts:
grep -r "CTkFont.*size=" *.py | grep -v "get_typography"

# Prüfe auf inkonsistente Abstände:
grep -r "padx=[0-9]" *.py | grep -v "get_spacing"
```

### Code Review Checklist:
- [ ] Alle Farben über `get_color()` definiert
- [ ] Alle Fonts über `get_typography()` definiert  
- [ ] Alle Abstände über `get_spacing()` definiert
- [ ] Vordefinierte Button-Stile verwendet
- [ ] Konsistente Card-Stile verwendet
- [ ] Keine hartcodierten Design-Werte

## 🚀 ERWEITERUNGEN

### Neue Farben hinzufügen:
```python
# In design_system.py:
'new_color': '#HEXCODE',
'new_color_hover': '#HEXCODE',
'new_color_light': '#HEXCODE'
```

### Neue Typography-Varianten:
```python
# In get_typography():
'new_variant': ('Segoe UI', SIZE, 'WEIGHT')
```

### Neue Component-Stile:
```python
# Neue create_* Funktion:
def create_new_component(style='default'):
    return {
        'fg_color': get_color('surface'),
        'border_color': get_color('surface_border'),
        # ... weitere Properties
    }
```

---

**Status:** ✅ Design System dokumentiert und einsatzbereit
**Wartung:** Regelmäßige Updates bei Design-Änderungen
**Integration:** Vollständig in alle Module integriert
