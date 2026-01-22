#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Terminologie-Glossar Regel

Prüft vereinfachten Glossar-Abgleich:
 - Erwartet im Kontext optional context['glossary'] = {source_term: target_term}
 - Falls kein Glossar: versucht 'glossary.json' im Arbeitsverzeichnis zu laden
 - Zählt Vorkommen der Source-Terme und prüft ob jeweilige Zielterm mindestens einmal in einer Übersetzung vorkommt
 - Kennzahlen:
     total_terms, terms_found, terms_missing, coverage_ratio
 - passed wenn coverage_ratio >= 0.7 und keine kritischen fehlenden Pflicht-Terme (falls Glossar-Eintrag flag mandatory=True besitzt)

Glossar-Dateiformat (glossary.json):
{
  "API": {"target": "Schnittstelle", "mandatory": true},
  "Server": {"target": "Server"}
}
Fallback akzeptiert auch einfaches Mapping {"API": "Schnittstelle"}.
"""
from __future__ import annotations
import json, os
from typing import Dict, Any
from plugins.base_rule import BaseRule, RuleResult

class TerminologyGlossaryRule(BaseRule):
    name = "terminology_glossary"
    version = "0.1"

    def _load_external_glossary(self) -> Dict[str, Any]:
        paths = ["glossary.json", os.path.join(os.getcwd(), "glossary.json")]
        for p in paths:
            try:
                if os.path.exists(p) and os.path.isfile(p):
                    with open(p, 'r', encoding='utf-8') as fh:
                        data = json.load(fh)
                        if isinstance(data, dict):
                            return data
            except Exception:
                continue
        return {}

    def _normalize_glossary(self, raw: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        norm: Dict[str, Dict[str, Any]] = {}
        for k, v in raw.items():
            try:
                if isinstance(v, dict):
                    target = v.get('target') or v.get('translation') or next(iter([vv for vv in v.values() if isinstance(vv, str)]), None)
                    if not target:
                        continue
                    norm[k] = {"target": str(target), "mandatory": bool(v.get('mandatory', False))}
                elif isinstance(v, str):
                    norm[k] = {"target": v, "mandatory": False}
            except Exception:
                continue
        return norm

    def analyze(self, context: dict) -> RuleResult:
        glossary_raw = context.get('glossary') or {}
        if not glossary_raw:
            glossary_raw = self._load_external_glossary()
        if not isinstance(glossary_raw, dict) or not glossary_raw:
            return RuleResult(rule=self.name, passed=True, details={"info": "no_glossary"})
        glossary = self._normalize_glossary(glossary_raw)
        if not glossary:
            return RuleResult(rule=self.name, passed=True, details={"info": "glossary_empty"})

        translations = context.get('translation_texts') or []
        if not translations:
            return RuleResult(rule=self.name, passed=False, details={"error": "no_translations", "total_terms": len(glossary)})

        combined = "\n".join(t for t in translations if isinstance(t, str))
        combined_lower = combined.lower()
        terms_found = []
        terms_missing = []
        mandatory_missing = []
        for src_term, meta in glossary.items():
            target = meta.get('target', '')
            mand = bool(meta.get('mandatory'))
            found = False
            try:
                if target and target.lower() in combined_lower:
                    found = True
            except Exception:
                found = False
            if found:
                terms_found.append(src_term)
            else:
                terms_missing.append(src_term)
                if mand:
                    mandatory_missing.append(src_term)

        total_terms = len(glossary)
        coverage_ratio = (len(terms_found) / total_terms) if total_terms else 0.0
        passed = coverage_ratio >= 0.7 and not mandatory_missing
        details = {
            "total_terms": total_terms,
            "terms_found": len(terms_found),
            "terms_missing": len(terms_missing),
            "mandatory_missing": mandatory_missing,
            "coverage_ratio": round(coverage_ratio, 4)
        }
        return RuleResult(rule=self.name, passed=passed, details=details)
