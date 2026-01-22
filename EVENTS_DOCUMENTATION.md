# Event Schema Dokumentation

Dieser Abschnitt dokumentiert die aktuell verwendeten Event-Themen (Topics) der Qualitäts-GUI sowie deren Payload-Schema (vereinheitlicht Stand 2025-08-21).

## Grundsätze

- Alle Payloads sind Dictionaries.
- Zeitstempel ("ts") sind Unix-Zeit (Sekunden float) sofern vorhanden.
- Neue vereinheitlichte Felder: `overall_score`, `summary`, `findings`, `plugins`, `counts`, `ui_completed_ts`.
- `analysis.ui.completed` spiegelt jetzt das finale Schema von `analysis.done` und ergänzt `ui_completed_ts`.

## Topics

### analysis.started

Minimaler Start-Hinweis vor Regelverarbeitung.

```json
{
  "phase": "start",
  "rules": "<int Gesamtanzahl Regeln>",
  "ts": "<float>"
}
```

### analysis.progress

Wiederholte Fortschrittsupdates während Regel- / Datei-Verarbeitung.

```json
{
  "phase": "<str Phase|step>",
  "current": "<int Anzahl verarbeitete Einheiten>",
  "total": "<int Gesamt-Einheiten>",
  "percent": "<float 0..100>",
  "duration": "<float Sekunden seit Start>",
  "quality_score": "<float 0..100 optional>",
  "issues": "<int kumulierte Anzahl Findings>",
  "critical": "<int>",
  "major": "<int>",
  "minor": "<int>"
}
```

### analysis.finalize

Letzte Aggregationsphase (optional Zwischenschritt vor done).

```json
{
  "phase": "finalize",
  "duration": "<float>",
  "issues": "<int>",
  "critical": "<int>",
  "major": "<int>",
  "minor": "<int>"
}
```

### analysis.done

Abschluss der Backend-Analyse (Rohdaten vollständig).

```json
{
  "phase": "done",
  "overall_score": "<float 0..100>",
  "summary": {
     "issues": "<int>",
     "critical": "<int>",
     "major": "<int>",
     "minor": "<int>"
  },
  "findings": [ { "... Finding ...": "..." } ],
  "plugins": [ { "name": "str", "duration": "float", "issues": "int" } ],
  "counts": { "files": "<int>", "rules": "<int>" },
  "duration": "<float Gesamt>",
  "ts": "<float>",
  "_cache_key": "<str optional>"
}
```

### analysis.ui.completed

UI-seitiger Abschluss nachdem Rendering vollständig ist. Spiegel von `analysis.done` plus UI-spezifischer Zeitstempel.

```json
{
  "phase": "ui.completed",
  "overall_score": "<float>",
  "summary": { "... wie oben ...": "" },
  "findings": [ "..." ],
  "plugins": [ "..." ],
  "counts": { "..." },
  "duration": "<float>",
  "ts": "<float Analyse-Ende>",
  "ui_completed_ts": "<float Zeitpunkt UI fertig>"
}
```

### analysis.background.completed

Hintergrundprozess (Batch/Async) fertig.

```json
{
  "phase": "background.completed",
  "summary": { "...": "" },
  "findings": [ "..." ],
  "overall_score": "<float>",
  "counts": { "..." },
  "duration": "<float>",
  "ts": "<float>"
}
```

### report.generated

Report (Export) erstellt.

```json
{
  "phase": "report.generated",
  "path": "<str Pfad zur Datei>",
  "overall_score": "<float>",
  "issues": "<int>",
  "critical": "<int>",
  "major": "<int>",
  "minor": "<int>",
  "ts": "<float>"
}
```

## Feldbeschreibungen

- overall_score: Aggregierter Qualitätswert (0..100).
- summary: Verdichtete Metriken (Issues & Severity-Breakdown).
- findings: Liste strukturierter Finding-Objekte (Mapping zu model.Finding falls vorhanden).
- plugins: Optionaler Performance-/Issues-Überblick pluginbasierter Regeln.
- counts: Zusatzstatistik (z.B. verarbeitete Dateien, Regeln).
- duration: Gesamtdauer der Analyse (Sekunden).
- ui_completed_ts: Zeit, zu der das UI die Darstellung finalisiert hat.

## Kompatibilität

Ältere Konsumenten, die nur `analysis.done` hören, erhalten weiterhin die bisherigen Felder; `analysis.ui.completed` erweitert dies um UI-spezifische Zeitmessung ohne breaking change.

## Versionierung

Dieses Schema ist v1.1 (Erweiterung um ui_completed_ts). Bei weiteren Änderungen bitte Abschnitt Versionierung erweitern.
