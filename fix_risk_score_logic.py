"""
🔧 RISIKO-SCORE LOGIK-FIX
========================================

PROBLEM:
  Analyse zeigt "Befunde: 0 | Risiko: 100/100"
  ❌ Das macht keinen Sinn!
  
KORREKT:
  Befunde: 0 → Risiko: 0/100 ✅
  (Keine Fehler = Exzellente Qualität = Kein Risiko)

========================================
URSACHE
========================================

Die Risiko-Berechnung hatte mehrere Probleme:

1. MISSING ELSE-BLOCK:
   ```python
   if findings:
       # Berechne Risiko
       phase4['risk_score'] = risk
   # ❌ KEIN ELSE! Bei 0 Findings wurde nichts gesetzt
   ```

2. EXCEPTION OHNE RISK_SCORE:
   ```python
   except Exception:
       consolidated = {'total': len(findings)}
       # ❌ risk_score fehlt komplett!
   ```

3. UI FALLBACK:
   Wenn risk_score = None, könnte die UI
   einen Default-Wert angezeigt haben

========================================
LÖSUNG
========================================

✅ Fix 1: Expliziter Else-Block
```python
if findings:
    # Berechne Risiko aus Befunden
    risk = min(100.0, round(((crit * 3 + maj * 2 + mi) / denom) * 25.0, 2))
    phase4['risk_score'] = risk
else:
    # WICHTIG: Keine Befunde = Risiko 0 (nicht 100!)
    phases_info['consolidation'] = {'total': 0, 'risk_score': 0.0}
    phases_info['phase4'] = {'total': 0, 'risk_score': 0.0}
```

✅ Fix 2: Exception-Handler mit risk_score
```python
except Exception:
    # Bei Fehler: Sichere Defaults (0 Befunde = 0 Risiko)
    consolidated = {
        'total': len(findings),
        'risk_score': 0.0 if not findings else 50.0
    }
```

✅ Fix 3: UI-Fallback mit Logik
```python
# WICHTIG: 0 Befunde = 0 Risiko (nicht None oder 100!)
if total == 0:
    risk = 0.0
```

========================================
RISIKO-FORMEL (zur Dokumentation)
========================================

Wenn Befunde vorhanden:
```
risk = min(100, ((kritisch×3 + schwer×2 + leicht×1) / segments) × 25)

Beispiele:
  10 Segments, 1 Kritisch:           (1×3)/10 × 25 = 7.5
  10 Segments, 2 Kritisch, 3 Schwer: (2×3 + 3×2)/10 × 25 = 30
  10 Segments, 10 Kritisch:          (10×3)/10 × 25 = 75
```

Wenn KEINE Befunde:
```
risk = 0  (Exzellente Qualität)
```

========================================
VORHER/NACHHER
========================================

❌ VORHER:
┌───────────────────────────┐
│ 🔴 Konsolidierung         │
│ Kritisches Risiko         │
│ Befunde: 0                │
│ Risiko: 100/100           │
└───────────────────────────┘

✅ NACHHER:
┌───────────────────────────┐
│ ✅ Konsolidierung         │
│ Exzellente Qualität       │
│ Befunde: 0                │
│ 🟢 Risiko: 0/100          │
└───────────────────────────┘

========================================
GEÄNDERTE DATEIEN
========================================

✓ quality_gui_main_app.py
  - Zeile 12615-12640: Expliziter else-Block für 0 Findings
  - Zeile 14177: Exception-Handler mit risk_score

✓ quality_gui_components_analysis_results.py
  - Zeile 286: UI-Fallback prüft total==0 → risk=0
  - Debug-Ausgaben hinzugefügt

========================================
VALIDIERUNG
========================================

Test-Szenarien:
1. ✅ 0 Befunde → Risiko = 0
2. ✅ 1 Kritischer Befund → Risiko > 0
3. ✅ Viele Kritische → Risiko ≈ 100
4. ✅ Exception während Berechnung → Risiko = 0 oder 50

Die Logik ist jetzt konsistent und macht Sinn!
"""

if __name__ == '__main__':
    print(__doc__)
