# 🎨 Typography System - Translation Quality GUI

Ein umfassendes Design-Token-basiertes Typography-System mit CSS-Variablen, Tailwind-Integration, automatischen Codemod-Tools und CI/CD-Guardrails.

## 📋 Übersicht

Dieses Typography-System basiert auf der vereinheitlichten Hierarchie der Translation Quality GUI:

| Klasse | Größe | Gewicht | Verwendung |
|--------|-------|---------|------------|
| `ty-caption` | 12px | normal | Kleine Labels, Menü-Text, Status |
| `ty-body` | 14px | normal | Standard Content, Inputs |
| `ty-body-bold` | 14px | bold | Buttons, wichtige Labels |
| `ty-subheading` | 18px | bold | Card Headers, Sections |
| `ty-heading` | 22px | bold | Hauptüberschriften |
| `ty-title` | 26px | bold | Page Titles, Hero Text |

## 🚀 Quick Start

### 1. CSS Design Tokens verwenden

```css
/* CSS Variablen */
.custom-button {
  font-size: var(--ty-body-bold-size);
  font-weight: var(--ty-body-bold-weight);
  line-height: var(--ty-body-bold-line-height);
}

/* Utility Classes */
.my-title { @apply ty-title; }
.my-content { @apply ty-body; }
.my-button { @apply ty-body-bold; }
```

### 2. HTML Integration

```html
<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="design-tokens.css">
</head>
<body>
  <h1 class="ty-title">Page Title</h1>
  <h2 class="ty-heading">Section Header</h2>
  <h3 class="ty-subheading">Card Header</h3>
  <p class="ty-body">Standard content text</p>
  <button class="btn btn-primary">Action Button</button>
  <span class="ty-caption">Meta information</span>
</body>
</html>
```

### 3. React Components

```jsx
import { Typography, Button, Card } from './TypographySystem';

function App() {
  return (
    <div>
      <Typography.Title>Translation Quality GUI</Typography.Title>
      <Card title="Analysis Results">
        <Typography.Body>
          Die Qualitätsanalyse zeigt eine Gesamtbewertung von 85%.
        </Typography.Body>
        <Button variant="primary">Mehr Details</Button>
      </Card>
    </div>
  );
}
```

### 4. Python Integration

```python
# Bestehende get_typography() Aufrufe bleiben unverändert
font = ctk.CTkFont(*self.get_typography("body"))
button_font = ctk.CTkFont(*self.get_typography("body_bold"))
title_font = ctk.CTkFont(*self.get_typography("heading"))
```

## 🛠️ Installation & Setup

### Design Tokens

```bash
# CSS Design Tokens einbinden
<link rel="stylesheet" href="design-tokens.css">
```

### Tailwind CSS

```bash
# Tailwind Config verwenden
cp tailwind.config.js your-project/
cp globals.css your-project/src/
```

### Stylelint Guardrails

```bash
# Stylelint installieren
npm install --save-dev stylelint stylelint-config-standard
cp .stylelintrc.json your-project/

# Validation ausführen
npx stylelint "**/*.css"
```

## 🔧 Migration Tools

### Automatischer Codemod (Node.js)

```bash
# Dry Run - zeigt Änderungen ohne sie zu machen
node typography-codemod.js ./src --dry-run

# Live Run - macht tatsächliche Änderungen
node typography-codemod.js ./src --verbose

# Spezifische Dateitypen
node typography-codemod.js ./src --ext=.py,.js
```

### PowerShell Alternative

```powershell
# Analyse der aktuellen Typography-Nutzung
.\typography-analysis.ps1 -Directory .\src

# Dry Run Migration
.\typography-refactor.ps1 -Directory .\src -DryRun

# Live Migration
.\typography-refactor.ps1 -Directory .\src -Verbose
```

## 📊 Migration Mapping

Das Codemod-System führt automatisch folgende Transformationen durch:

```javascript
// Vorher → Nachher
get_typography('button_lg') → get_typography('body_bold')
get_typography('heading_lg') → get_typography('heading')
get_typography('body_sm') → get_typography('body')
get_typography('label_bold') → get_typography('body_bold')

// CSS Classes
.ty-button-lg → .ty-body-bold
.ty-heading-lg → .ty-heading
.ty-label → .ty-body

// JavaScript/React
fontSize: 'button_lg' → fontSize: 'body_bold'
typography="heading_lg" → typography="heading"
```

## 🎯 Responsive Scaling

Das System unterstützt automatische responsive Skalierung:

```css
/* Mobile (sm): -1px */
@media (max-width: 640px) {
  --font-size-body: 0.8125rem; /* 13px statt 14px */
}

/* Desktop Large (lg): +1px */
@media (min-width: 1024px) {
  --font-size-body: 0.9375rem; /* 15px statt 14px */
}
```

## 🛡️ CI/CD Guardrails

### GitHub Actions Integration

```yaml
# .github/workflows/typography-ci.yml wird automatisch ausgeführt bei:
- push zu main/develop
- Pull Requests
- Validiert Typography-Compliance
- Führt automatische Fixes durch
- Deployt Dokumentation
```

### Lokale Validation

```bash
# Stylelint Check
npm run lint:css

# Typography Pattern Check
grep -r "font-size:\s*[0-9]" --include="*.css" .
```

## 📚 Verfügbare Dateien

### Core System
- `design-tokens.css` - CSS Custom Properties & Utility Classes
- `TypographySystem.tsx` - React Components & TypeScript Definitions
- `typography-demo.html` - Live Demo & Beispiele

### Tailwind Integration  
- `tailwind.config.js` - Tailwind Theme Extension
- `globals.css` - Tailwind + Typography Integration

### Migration Tools
- `typography-codemod.js` - Node.js Automatic Refactoring Tool
- `typography-refactor.ps1` - PowerShell Migration Script
- `typography-analysis.ps1` - Usage Analysis & Dry-Run Report

### Guardrails
- `.stylelintrc.json` - CSS Linting Rules & Typography Validation
- `.github/workflows/typography-ci.yml` - CI/CD Pipeline

## 🎨 Design Principles

### 1. Konsistenz
- Einheitliche Schriftgrößen-Hierarchie
- Semantische Namensgebung  
- Vorhersagbare Skalierung

### 2. Wartbarkeit
- Zentrale Token-Definition
- Automatische Migration
- CI/CD Validation

### 3. Performance
- CSS Custom Properties für optimale Performance
- Minimale CSS-Bundle-Größe
- Responsive ohne JavaScript

### 4. Developer Experience
- Klare Utility Classes
- TypeScript Support
- Comprehensive Documentation

## 🔧 Erweiterte Nutzung

### Custom CSS Variables

```css
:root {
  /* Benutzerdefinierte Extensions */
  --ty-custom-size: 1.75rem; /* 28px */
  --ty-custom-weight: 600;
}

.custom-typography {
  font-size: var(--ty-custom-size);
  font-weight: var(--ty-custom-weight);
  line-height: var(--ty-line-height-heading);
}
```

### Styled Components Integration

```javascript
import styled from 'styled-components';

const CustomTitle = styled.h1`
  font-size: var(--ty-title-size);
  font-weight: var(--ty-title-weight);
  line-height: var(--ty-title-line-height);
  color: var(--ty-text);
`;
```

### CSS-in-JS

```javascript
const titleStyles = {
  fontSize: 'var(--ty-title-size)',
  fontWeight: 'var(--ty-title-weight)',
  lineHeight: 'var(--ty-title-line-height)',
  fontFamily: 'var(--font-family-base)',
};
```

## 📋 Troubleshooting

### Häufige Probleme

**Problem:** Alte Typography-Klassen werden noch verwendet
```bash
# Lösung: Codemod ausführen
node typography-codemod.js . --dry-run
```

**Problem:** Stylelint Fehler bei Custom Properties
```json
// Lösung: .stylelintrc.json anpassen
{
  "rules": {
    "custom-property-pattern": "^(ty|your-prefix)-[a-z0-9-]+$"
  }
}
```

**Problem:** Typography in Python nicht aktualisiert
```bash
# Lösung: Python-spezifischen Check
grep -r "get_typography.*button_lg" --include="*.py" .
```

### Debug Commands

```bash
# Typography Usage Report
.\typography-analysis.ps1 -Directory .

# Detailed Migration Preview
node typography-codemod.js . --dry-run --verbose

# CSS Validation
npx stylelint "**/*.css" --formatter verbose
```

## 🎯 Best Practices

### ✅ Empfohlen

```css
/* CSS Custom Properties nutzen */
.component { font-size: var(--ty-body-size); }

/* Utility Classes verwenden */
<p class="ty-body">Content</p>

/* Semantische Namen */
.card-header { @apply ty-subheading; }
```

### ❌ Vermeiden

```css
/* Hardcoded Werte */
.component { font-size: 14px; }

/* Inline Styles */
<p style="font-size: 14px;">Content</p>

/* Nicht-semantische Namen */
.text-14 { font-size: 14px; }
```

## 📈 Roadmap

### Phase 1 (Completed)
- ✅ Design Token System
- ✅ CSS Utility Classes  
- ✅ Tailwind Integration
- ✅ Migration Tools
- ✅ CI/CD Pipeline

- ✅ Legacy Token Removal (aktive Codebasis)

### Phase 1.1 (Jetzt abgeschlossen – 2025-08-08)

Die produktive Codebasis (Python + CSS) verwendet nur noch die vereinheitlichten 6 Stufen. Legacy-Bezeichner sind: `micro_bold`, `caption_bold`, `metric_value`, `input`, `heading_lg`, `heading_xl`, `title_lg`, `title_xl`.

**Governance Status:**

- Stylelint blockiert verbotene Werte
- PowerShell `typography-analysis.ps1` bricht CI mit Exit-Code 2 bei Legacy-Funden
- CI Workflow (`typography-ci.yml`) integriert PowerShell-Enforcement
- Deprecation Mapping in `quality_gui_main_app.py` verbleibt als Übergangsschutz bis erster grüner CI-Lauf nach Merge

**Entfernungs-Plan Deprecation Mapping:**

1. CI Lauf ohne Legacy (Bestätigung: kein Exit-Code 2)
2. Entferne Mapping + Logging-Hinweis (`deprecation_map`) aus `get_typography`
3. Füge Prüf-Assertion hinzu, falls ein alter Name wieder auftaucht → sofortiger Fehler
4. Aktualisiere diese README (Phase 1.1 → Locked)
5. Erstelle Lock-File Marker: `TYPOGRAPHY_GOVERNANCE_LOCKED.md`

**Archivierung:**

- Historische Backup-Dateien wurden (oder werden) nach `/archive` verschoben
- Analyse ignoriert Dateien mit Namensmustern: `backup`, `.bak`, `.old`, `.orig`

Nach Removal des Mappings gilt Zero-Tolerance: Jeder neue Legacy-Identifier schlägt lokal (grep hook) + CI fehl.

### Phase 2 (Geplant)

- 🔄 Dark Mode Support
- 🔄 Component Library Extension
- 🔄 Advanced Animation Support
- 🔄 Performance Monitoring

### Phase 3 (Zukunft)

- 📋 Visual Testing Integration
- 📋 Design Token Studio Integration
- 📋 Multi-Brand Support
- 📋 Advanced Typography Features

## 🤝 Contributing

1. Fork das Repository
2. Erstelle einen Feature Branch
3. Implementiere Änderungen mit Tests
4. Führe `npm run lint:css` aus
5. Committe mit semantischen Commit Messages
6. Erstelle einen Pull Request

## 📄 License

MIT License - siehe LICENSE.md für Details.

---

**Translation Quality GUI Typography System** - Professional, consistent, maintainable typography für moderne Web-Anwendungen. 🎨✨
