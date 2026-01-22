# Quick Reference: Analysis Results Features

## What's New

### 1. Accordion Phases (Phasen Tab)
**Location**: Click the "Phasen" (Phases) tab in analysis results window

**What You'll See**:
- 6 collapsible phase sections
- Each phase shows:
  - Traffic light indicator (🔴 red / 🟠 orange / 🟢 green)
  - Status description (e.g., "Kritische Befunde vorhanden")
  - Metrics (count, severity breakdown, risk score)
  - Click "Details anzeigen" to expand and see example findings

**How to Use**:
```
1. Open analysis results
2. Go to "Phasen" tab
3. Look for red/orange phases (indicate issues found)
4. Click "Details anzeigen" to see examples
5. Click "Befunde anzeigen" to jump to filtered findings
```

### 2. Phase Filters (Befunde Tab)
**Location**: Control panel in "Befunde" (Findings) tab

**What You'll See**:
- Row of filter buttons: "All", "Phase 1", "Phase 2", etc.
- Each button shows count: "Phase 1 (15)"
- Currently active filter button is highlighted in blue

**How to Use**:
```
1. Go to "Befunde" tab
2. Click a phase button to see only findings from that phase
3. Click "All" to see findings from all phases
4. Your choice is remembered next time
```

### 3. Jump to Filtered Findings
**Location**: "Befunde anzeigen" button in each phase accordion

**What It Does**:
- Switches to Findings tab
- Pre-selects the phase filter
- Shows only findings from that phase

**Example**:
```
Phase 1 accordion shows "Kritische Befunde vorhanden"
→ Click "Befunde anzeigen"
→ Findings tab opens
→ Phase 1 filter is automatically selected
→ Shows only Phase 1 findings
```

## Understanding the Indicators

### Traffic Light Colors (Phasen Tab)

🔴 **RED (Kritisch/Critical)**
- Means: Critical errors found in this phase
- Action: Review immediately

🟠 **ORANGE (Schwerwiegend/Major)**
- Means: Significant issues found
- Action: Review and fix before final check

🟢 **GREEN (Keine Befunde)**
- Means: No issues in this phase
- Action: Good - continue to next phase

### Severity Levels (Befunde Tab)

**Critical** (Kritisch) - Red
- Translation error that changes meaning
- Example: Missing placeholder {0}

**Major** (Schwerwiegend) - Orange  
- Significant quality issue
- Example: Low segment similarity

**Minor** (Leicht) - Blue
- Minor quality suggestion
- Example: Grammar inconsistency

## Tips & Tricks

### Finding Specific Issues
1. Go to Findings tab
2. Use Phase filter to narrow down
3. Use Severity filter to see only important issues
4. Use search box to find specific keywords

### Understanding Metrics

```
Befunde: 24          ← Total findings in phase
Kritisch: 2          ← Number of critical issues
Schwerwiegend: 8     ← Number of major issues
Leicht: 14           ← Number of minor issues
Risiko-Score: 65     ← Risk assessment (0-100)
Empfehlungen: 3      ← Number of suggestions
```

### Reviewing Your Translation

**Best Practice**:
1. Start with Phase 1 (Consistency)
2. Move to Phase 2 (Structure)
3. Review Phase 3 (Completeness)
4. Check Phase 4 analysis (Risk assessment)
5. Consider Phase 6 suggestions

## Troubleshooting

### "Keine Befunde erkannt" (No Findings Detected)

**This is GOOD** - Means:
- Your translation has excellent quality
- No issues detected by automated checks
- Ready for final review

### Phase Shows No Details

**This is NORMAL** - Means:
- That specific check wasn't needed for your files
- No findings from that phase
- No need to fix

### Findings Not Visible

**Try**:
1. Check if "All" phase filter is selected
2. Check if "All" severity filter is selected
3. Scroll down - findings might be below visible area
4. Try refreshing/re-running analysis

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Ctrl+1 | Jump to Overview tab |
| Ctrl+2 | Jump to Phases tab |
| Ctrl+3 | Jump to Findings tab |
| Ctrl+F | Focus search in Findings tab |
| Ctrl+C | Copy selected finding |
| ↑/↓ | Navigate through findings |

## Need Help?

Look for these indicators:

- 🟡 **Yellow/Orange Phase** → Minor issues, can continue
- 🔴 **Red Phase** → Fix critical issues first
- 📊 **High Risk Score** → Consider deeper review
- ✅ **Green Phases** → You're doing well

---

**Version**: 1.0  
**Date**: 2025-10-16  
**Language**: Deutsch/German UI + English Comments
