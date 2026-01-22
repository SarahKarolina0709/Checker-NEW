"""quality_gui_phase4_checkers – finale Migration (ursprünglich qa_phase4_checkers).
Konsolidierung & Risiko-Bewertung Phase 4.
"""
from __future__ import annotations
from typing import List, Dict, Any
from collections import Counter

try:
	from quality_gui_phase1_checkers import QAIssue  # type: ignore
except Exception:
	from dataclasses import dataclass
	@dataclass
	class QAIssue:  # type: ignore
		code: str; severity: str; category: str; message: str; source_text: str; target_text: str; meta: dict | None = None

SEV_WEIGHTS = {"critical": 1.0, "major": 0.6, "minor": 0.25, "info": 0.1}
GROUP_WEIGHTS = {
	"Sicherheit": 1.25,
	"Integrität": 1.15,
	"Struktur": 1.0,
	"Terminologie": 0.95,
	"Semantik": 0.9,
	"Stil": 0.8,
	"Lesbarkeit": 0.75,
	"Format": 0.7,
	"Zeichensetzung": 0.7,
	"Typografie": 0.7
}
PRIMARY_GROUPS = {
	'placeholders': 'Integrität',
	'references': 'Integrität',
	'structure': 'Struktur',
	'whitespace': 'Format',
	'style': 'Stil',
	'risk': 'Sicherheit',
	'readability': 'Lesbarkeit',
	'semantic': 'Semantik',
	'terminology': 'Terminologie',
}
CATEGORY_ALIASES = {
	'security': 'Sicherheit',
	'risk': 'Sicherheit',
	'html': 'Struktur',
	'markup': 'Struktur',
	'consistency': 'Integrität',
	'integrity': 'Integrität',
	'punctuation': 'Zeichensetzung',
	'quotes': 'Typografie',
	'typography': 'Typografie',
	'whitespace': 'Format',
	'formatting': 'Format',
	'style': 'Stil',
	'readability': 'Lesbarkeit',
	'semantic': 'Semantik',
	'semantics': 'Semantik',
	'terminology': 'Terminologie',
}
def _map_category(cat: str) -> str:
	cat_norm = (cat or '').strip().lower()
	base = PRIMARY_GROUPS.get(cat_norm)
	if base:
		return base
	alias = CATEGORY_ALIASES.get(cat_norm)
	return alias if alias else (cat_norm.capitalize() if cat_norm else 'Sonstiges')

QUICK_FIX_HINTS: Dict[str,str] = {
	# Whitespace & Invisible
	'WS_DOUBLE_SPACE':     "Doppelte Leerzeichen zu einem reduzieren.",
	'WS_TRAILING':         "Trailing Whitespace entfernen.",
	'WS_LEADING':          "Führende Leerzeichen entfernen.",
	'ZERO_WIDTH_CHAR':     "Unsichtbare Zeichen (ZWSP/FEFF) entfernen.",
	'PLACEHOLDER_MISSING': "Fehlende Platzhalter 1:1 übernehmen (Typ & Reihenfolge).",
	'PLACEHOLDER_EXTRA':   "Überzählige Platzhalter entfernen.",
	'PLACEHOLDER_ORDER':   "Reihenfolge der Platzhalter an Quelle angleichen.",
	'URL_MISSING':         "Fehlende URL aus Quelle übernehmen.",
	'URL_EXTRA':           "Nicht in Quelle vorkommende URL entfernen.",
	'URL_ORDER':           "URL-Reihenfolge an Quelle angleichen.",
	'EMAIL_MISSING':       "Fehlende E-Mail übernehmen.",
	'EMAIL_EXTRA':         "Überflüssige E-Mail entfernen.",
	'EMAIL_ORDER':         "E-Mail-Reihenfolge an Quelle angleichen.",
	'BRACKET_UNCLOSED':    "Offene Klammern/Tags schließen.",
	'BRACKET_MISMATCH':    "Tag-/Klammer-Paare korrigieren.",
	'BRACKET_UNBALANCED':  "Schließende Klammer ohne Öffnung korrigieren/entfernen.",
	'HTML_UNBALANCED':     "HTML-Struktur balancieren (öffnend/schließend).",
	'HTML_TAG_MISSING':    "Fehlende Tags aus Quelle ergänzen.",
	'HTML_TAG_EXTRA':      "Zusätzliche Tags entfernen.",
	'HTML_ATTR_MISSING':   "Fehlende Attribute ergänzen.",
	'HTML_ATTR_EXTRA':     "Überflüssige Attribute entfernen.",
	'SECURITY_JS_LINK':    "javascript:-Links entfernen oder entschärfen.",
	'SECURITY_EVENT_HANDLER': "Neue Event-Handler (onclick/...) entfernen.",
	'SECURITY_SCRIPT_TAG': "Neue <script>-Tags entfernen.",
	'SECURITY_DATA_URI':   "data:-URI prüfen/entfernen (Security/Privacy).",
	'RISK_DATA_URI':       "data:-URI prüfen/entfernen (Security/Privacy).",
	'RISK_NEW_DOMAIN':     "Neue Domain verifizieren oder entfernen.",
	'RISK_BASE64_SUSPECT': "Base64-Block prüfen (versteckte Payload?).",
	'RISK_INLINE_STYLE':   "Inline-Style vermeiden; Stylesheet nutzen.",
	'TERM_PREFERRED_MISSING': "Glossar-Sollform einsetzen (Flexion).",
	'DUPLICATE_INCONSISTENT': "Duplikat auf erste Übersetzung angleichen.",
	'PUNCT_MISSING_END':   "Satzendzeichen ergänzen.",
	'PUNCT_DOUBLE':        "Doppelte Satzzeichen reduzieren.",
	'QUOTE_PLAIN':         "Typografische Anführungszeichen („…“) nutzen.",
	'QUOTE_MIX':           "Einheitlichen Anführungsstil wählen.",
	'S_CASE_INCONSISTENT': "Satzanfang groß schreiben.",
	'NUMBER_MISSING':      "Zahlen aus Quelle übernehmen.",
	'NUMBER_ADDED':        "Nicht vorhandene Zahlen entfernen.",
	'UNIT_DRIFT':          "Einheiten an Quelle angleichen.",
	'STYLE_LONG_SENTENCE': "Sehr lange Sätze teilen (<180 Zeichen).",
	'STYLE_PASSIVE_HEAVY_DE': "Passiv reduzieren – aktiver formulieren.",
	'STYLE_PASSIVE_HEAVY_EN': "Passiv (EN) reduzieren – Aktiv bevorzugen.",
	'READABILITY_TOO_LONG': "Durchschnittliche Satzlänge reduzieren.",
	'READABILITY_MANY_LONG': "Sehr lange Sätze kürzen.",
	'READABILITY_STACCATTO': "Viele Kurzsätze zusammenfassen.",
	'READABILITY_LIX_HIGH': "Komplexität senken (LIX reduzieren).",
	'SEMANTIC_LOW':        "Semantisch abweichende Segmente angleichen.",
	'SEMANTIC_GLOBAL_LOW': "Globale Semantik verbessern (breite Abweichung)."
}

def consolidate_issues(*issue_lists: List[QAIssue]) -> Dict[str, Any]:
	issues: List[QAIssue] = []
	for lst in issue_lists:
		if lst:
			issues.extend(lst)
	dedup: List[QAIssue] = []
	seen = set()
	for it in issues:
		src = getattr(it, 'source_text', getattr(it, 'source', '')) or ''
		tgt = getattr(it, 'target_text', getattr(it, 'target', '')) or ''
		# message bewusst weggelassen, um nahezu identische Funde zusammenzuführen
		key = (it.code, _map_category(it.category), src[:60], tgt[:60])
		if key in seen:
			continue
		seen.add(key)
		dedup.append(it)
	issues = dedup
	if not issues:
		return {
			'total': 0,
			'risk_score': 0.0,
			'primary_focus': None,
			'recommendations': [],
			'groups': {},
			'severity_distribution': {},
			'skipped': False
		}
	sev_dist: Dict[str,int] = {}
	group_counts: Dict[str,int] = {}
	examples: Dict[str,list] = {}
	code_counter: Counter = Counter()
	weighted_sum = 0.0
	weighted_sum_group = 0.0
	for iss in issues:
		sev = (iss.severity or '').lower()
		sev_dist[sev] = sev_dist.get(sev,0)+1
		w = SEV_WEIGHTS.get(sev,0.2)
		grp = _map_category(iss.category)
		gw = GROUP_WEIGHTS.get(grp,1.0)
		weighted_sum += w
		weighted_sum_group += w * gw
		code_counter[iss.code] += 1
		group_counts[grp] = group_counts.get(grp,0)+1
		if grp not in examples:
			examples[grp] = []
		if len(examples[grp]) < 5:
			examples[grp].append(iss.message[:140])
	total = len(issues)
	base = weighted_sum / max(1,total)
	gw_avg = weighted_sum_group / max(1,total)
	risk_score = min(1.0, round(0.5*base + 0.5*min(1.0, gw_avg),4))
	primary_focus = None
	if group_counts:
		# deterministischer Tiebreaker: count, Gruppen-Gewicht, Name
		primary_focus = max(
			group_counts.items(),
			key=lambda kv: (kv[1], GROUP_WEIGHTS.get(kv[0], 1.0), kv[0])
		)[0]
	recommendations: List[str] = []
	crit = sev_dist.get('critical',0)
	maj = sev_dist.get('major',0)
	if crit:
		recommendations.append('Kritische Befunde zuerst (Integrität/Sicherheit) beheben')
	if group_counts.get('Sicherheit'):
		recommendations.append('Sicherheits-/Risiko-Befunde prüfen (Domains, Base64, Inline-Style, Event-Handler)')
	if group_counts.get('Integrität'):
		recommendations.append('Integrität: Platzhalter/Referenzen/Tags 1:1 angleichen')
	if group_counts.get('Terminologie'):
		recommendations.append('Terminologie konsolidieren (Glossar-Sollformen einsetzen)')
	if group_counts.get('Semantik'):
		recommendations.append('Semantisch abweichende Segmente prüfen & korrigieren')
	if group_counts.get('Stil') and (crit+maj) < 3:
		recommendations.append('Stil optimieren (lange Sätze, Passiv) nach Blockern')
	if not recommendations:
		recommendations.append('Keine priorisierten Probleme – Abschlussreview durchführen')
	quick_fixes: Dict[str, Any] = {}
	for grp, cnt in sorted(group_counts.items(), key=lambda x: -x[1]):
		grp_codes = [i.code for i in issues if _map_category(i.category) == grp]
		top_codes = [c for c,_ in Counter(grp_codes).most_common(3)]
		actions = [QUICK_FIX_HINTS[c] for c in top_codes if c in QUICK_FIX_HINTS]
		quick_fixes[grp] = {
			'count': cnt,
			'top_codes': top_codes,
			'actions': actions,
			'examples': examples.get(grp, [])[:5]
		}
	top_codes_global = [c for c, _ in code_counter.most_common(5)]
	return {
		'total': total,
		'risk_score': risk_score,
		'primary_focus': primary_focus,
		'recommendations': recommendations[:6],
		'groups': {k:{'count':v,'examples':examples.get(k,[])} for k,v in group_counts.items()},
		'quick_fixes': quick_fixes,
		'severity_distribution': sev_dist,
		'top_issue_codes': top_codes_global,
		'skipped': False
	}

__all__ = ['consolidate_issues']
