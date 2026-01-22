# Plugin Einstellungen

Dieser Abschnitt beschreibt konfigurierbare Plugin-Laufzeitparameter.

## Schlüssel

- plugins.timeout_ms
  Beschreibung: Maximale Ausführungszeit einer einzelnen Regel (Millisekunden) bevor sie als Timeout gezählt wird.
  Standard: 2000
  Gültig: >= 50 (praktisch > 0)
  Wirkung: Erhöhen für sehr langsame Regeln, verringern für schnellere Abbrüche.

- plugins.timeout_log_level
  Beschreibung: Logging-Level für Timeout-Meldungen (info|warning|error|debug).
  Standard: warning
  Hinweis: Ungültige Werte fallen auf warning zurück.

- plugins.abort_timeout_ratio
  Beschreibung: Frühabbruch-Schwelle. Wenn (Timeouts / ausgeführte Regeln) > Schwelle und mindestens 5 Regeln ausgeführt wurden, wird die Analyse abgebrochen.
  Standard: 0.4
  Gültig: 0.1 – 0.9 (Werte außerhalb werden auf 0.4 zurückgesetzt)
  Ereignisse:
  - plugins.analysis.aborted (Payload: reason, timeout_ratio, executed, timeouts, threshold)
  - plugins.analysis.completed (enthält aborted Flag + threshold)

## Verhalten

1. Einzel-Timeouts erhöhen stats.timeouts; Regelresultat fehlt dann.
2. Erreicht die Timeout-Quote die Abort-Schwelle, setzt das System _plugin_cancel_requested und stoppt weitere Regeln.
3. Statusleiste zeigt Hinweis mit tatsächlicher Quote und Schwelle.
4. Completed-Event enthält immer vollständige Statistik + aborted + threshold.

## Empfehlungen

- Hohe Schwelle (z.B. 0.8): bevorzugt vollständige Ergebnisse, seltene Abbrüche.
- Niedrige Schwelle (z.B. 0.2): aggressiv, spart Zeit bei massiven Verzögerungen.
- Beobachte stats.per_rule um langsame Regeln gezielt zu optimieren.

## Beispiel

```ini
plugins.timeout_ms = 1500
plugins.timeout_log_level = info
plugins.abort_timeout_ratio = 0.35
```

## Fehlerbehandlung

- Ungültige numerische Eingabe in UI wird verworfen und Toast "Ungültiger Wert" angezeigt.
- Werte außerhalb des erlaubten Bereichs lösen Warn-Toast aus.
