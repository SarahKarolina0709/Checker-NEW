"""quality_gui_phase5_enforcer – finale Migration (Phase 5 Enforcement & Auto-Fix).

Enforcement: Auto-Fixes, Structural Guard, CI-Gate, Baseline Waiver, Artefakte.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Iterable, Tuple, Optional
import difflib, json, os, time, hashlib
import re

try:
	from quality_gui_phase1_checkers import QAIssue  # type: ignore
except Exception:
	@dataclass
	class QAIssue:  # type: ignore
		code: str; severity: str; category: str; message: str; source: str; target: str; meta: dict | None = None

@dataclass
class AppliedFix:
	code: str
	description: str
	before: str
	after: str
	changed: bool

# --- Schutz: Tags & Platzhalter nie anfassen ------------------------------- #
# Platzhalter/ICU/printf/$VAR/:slug (vereinfachte Superset-Regex)
_PROTECT_SUBPATTERNS: List[str] = [
	# HTML-Tags
	r"<[^>]+>",
	# ICU plural/select/selectordinal (vereinfachtes, robustes Muster)
	r"\{\w+,\s*(?:plural|select|selectordinal)\s*,[^{}]*\{[^{}]*\}[^}]*\}",
	# Platzhalter {0} bzw. {name}
	r"\{\d+\}",
	r"\{[^{}]+\}",
	# printf / %@ mit gängigen Modifizierern
	r"%(?:\d+\$)?[+#0\- ]?(?:\d+|\*)?(?:\.(?:\d+|\*))?(?:hh|h|l|ll|L)?[@sdifuxX]",
	# $VARS
	r"\$[A-Za-z_][A-Za-z0-9_]*\b",
	# :slug (z. B. :customer-id)
	r":[A-Za-z_][\w-]*",
]

# Zusammenführen zum finalen Schutz-Pattern (kein re.VERBOSE, da wir bewusst einfache Join-Variante nutzen)
_PROTECT_RE = re.compile("(" + ")|(".join(_PROTECT_SUBPATTERNS) + ")")

def _apply_safely(text: str, fix_fn):
	"""Wendet fix_fn(nur_text)->(neu,changed,tag) auf Nicht-Tag/Nicht-Platzhalter Segmente an.

	Rückgabe: (joined_text, changed_any, tags: List[str])
	"""
	parts = _PROTECT_RE.split(text or "")
	out: List[str] = []
	changed_any: bool = False
	tags: List[str] = []
	for p in parts:
		if not p:
			continue
		if _PROTECT_RE.fullmatch(p):   # geschütztes Stück
			out.append(p)
			continue
		new, changed, t = fix_fn(p)
		if changed and t:
			tags.append(t)
		changed_any = changed_any or changed
		out.append(new)
	return "".join(out), changed_any, tags

# --- Einzelne, sichere Fixer ---------------------------------------------- #
def _fix_ws(text: str):
	# Reduziert Mehrfach-Leerzeichen + Leading/Trailing je Zeile
	new = re.sub(r"[ \t]{2,}", " ", text)
	new = re.sub(r"[ \t]+$", "", new, flags=re.MULTILINE)
	new = re.sub(r"^[ \t]+", "", new, flags=re.MULTILINE)
	return new, new != text, "WS_MULTI"

def _fix_punct(text: str):
	# !!, ??, ;;, ,, → Einzelzeichen; Ellipsen bleiben erhalten
	new = re.sub(r"!{2,}", "!", text)
	new = re.sub(r"\?{2,}", "?", new)
	new = re.sub(r";{2,}", ";", new)
	new = re.sub(r",{2,}", ",", new)
	# Punkte: "...." → "..." ; ".." → "."
	new = re.sub(r"\.{4,}", "...", new)
	new = re.sub(r"(?<!\.)\.\.(?!\.)", ".", new)
	return new, new != text, "PUNCT_MULTI"

def _fix_quotes_de(text: str):
	# Nur gerade "…", und nur bei gerader Anzahl, zu „…“
	if text.count('"') >= 2 and text.count('"') % 2 == 0:
		out, openq = [], True
		for ch in text:
			if ch == '"':
				out.append("„" if openq else "“")
				openq = not openq
			else:
				out.append(ch)
		new = "".join(out)
		return new, new != text, "QUOTE_SIMPLE"
	return text, False, "QUOTE_SIMPLE"

def _fix_units_nbsp(text: str):
	# NBSP (\u00A0) zwischen Zahl und Einheit/%, kein normaler Space
	new = re.sub(r"(?<=\d)\s*(%|€|EUR|kg|g|ms|s|cm|mm|km)\b", r"\u00A0\1", text)
	return new, new != text, "UNIT_SPACE"

def _fix_markdown_like(text: str):
	# (Text)[http...] -> [Text](http...)
	pattern = re.compile(r'\(([^)\[]+?)\)\[(https?://[^]\s]+)\]')
	def _repl(m): return f"[{m.group(1).strip()}]({m.group(2).strip()})"
	new = pattern.sub(_repl, text)
	return new, new != text, 'MD_LINK_SWAP'

AUTO_FIXES = [
	("Normalize Mehrfach-Leerzeichen",           lambda t: _apply_safely(t, _fix_ws)),
	("Doppelte Satzzeichen reduzieren",          lambda t: _apply_safely(t, _fix_punct)),
	("Gerade → typografische Anführungszeichen", lambda t: _apply_safely(t, _fix_quotes_de)),
	("NBSP vor %/Einheiten",                     lambda t: _apply_safely(t, _fix_units_nbsp)),
	("Markdown Link Reparatur",                  lambda t: _apply_safely(t, _fix_markdown_like)),
]

def _apply_regex(text: str, pattern: str, repl: str, tag: str):
	new = re.sub(pattern, repl, text)
	return new, new != text, tag

def generate_structural_fingerprint(src: str) -> Dict[str,int]:
	# Zähle Platzhalter/ICU/printf/$VAR/:slug konsistent mit _PROTECT_RE
	ph = len([m.group(0) for m in _PROTECT_RE.finditer(src or "") if m.group(0) and not m.group(0).startswith("<")])
	fp = {
		'placeholders': ph,
		'urls': len(re.findall(r'https?://', src)),
		'emails': len(re.findall(r'[\w.+-]+@[\w.-]+', src)),
		'digits': sum(c.isdigit() for c in src),
		'brackets': sum(src.count(x) for x in ['<','>','[',']','(',')','{','}'])
	}
	return fp

def compare_fingerprint(src_fp: Dict[str,int], tgt_fp: Dict[str,int], *, threshold: float = 0.35) -> List[str]:
	problems: List[str] = []
	thr = max(0.0, float(threshold))
	for k, v in src_fp.items():
		tv = tgt_fp.get(k, 0)
		try:
			if v and abs(v - tv) / max(v, 1) > thr:
				problems.append(k)
		except Exception:
			# Defensive: ignoriere ungewöhnliche Fälle
			continue
	return problems

def apply_auto_fixes(target: str) -> Tuple[str, List[AppliedFix], Dict[str,int]]:
	applied: List[AppliedFix] = []
	current = target
	telemetry: Dict[str, int] = {}
	for desc, func in AUTO_FIXES:
		before = current
		after, changed, tags = func(current)
		if changed:
			# AppliedFix erwartet einen einzelnen Tag – verwende den ersten; Telemetrie sammelt alle
			tag0 = tags[0] if isinstance(tags, list) and tags else desc.split(" ")[0].upper()
			applied.append(AppliedFix(tag0, desc, before[:4000], after[:4000], True))
			current = after
			for t in (tags or []):
				telemetry[t] = telemetry.get(t, 0) + 1
	return current, applied, telemetry

def _severity_rank(sev: str) -> int:
	order = {"critical":3, "major":2, "minor":1, "info":0}
	return order.get(sev.lower(), 0)

def _issue_key(issue: QAIssue) -> str:
	src = getattr(issue, 'source_text', getattr(issue, 'source', '')) or ''
	tgt = getattr(issue, 'target_text', getattr(issue, 'target', '')) or ''
	base = f"{getattr(issue,'code','')}|{getattr(issue,'message','')}|{getattr(issue,'category','')}|{src[:60]}|{tgt[:60]}"
	return hashlib.md5(base.encode('utf-8','ignore')).hexdigest()

def load_baseline(path: str) -> Dict[str,dict]:
	if not path or not os.path.isfile(path):
		return {}
	try:
		return json.loads(open(path,'r',encoding='utf-8').read()).get('waived', {})
	except Exception:
		return {}

def save_baseline(path: str, waived: Dict[str,dict]):
	try:
		with open(path,'w',encoding='utf-8') as f:
			json.dump({'waived': waived, 'ts': int(time.time())}, f, ensure_ascii=False, indent=2)
	except Exception:
		pass

def enforce_phase5(pairs: Iterable[Tuple[str,str]], issues: List[QAIssue], *,
				   enable_auto_fix: bool = True,
				   structural_guard: bool = True,
				   phase1_guard: bool = True,
				   ci_gate: Optional[Dict[str,int]] = None,
				   baseline_path: Optional[str] = None,
				   update_baseline: bool = False,
				   artifact_dir: Optional[str] = None,
				   structural_guard_threshold: float = 0.35) -> Dict[str,object]:
	pairs_list = list(pairs)
	fixed_pairs: List[Tuple[str,str]] = []
	fixes: Dict[int, List[AppliedFix]] = {}
	autofix_stats_global: Dict[str,int] = {}
	if enable_auto_fix:
		for idx, (src, tgt) in enumerate(pairs_list):
			new_tgt, applied, telemetry = apply_auto_fixes(tgt)
			if applied:
				fixes[idx] = applied
				for k, v in telemetry.items():
					autofix_stats_global[k] = autofix_stats_global.get(k, 0) + int(v)
			fixed_pairs.append((src, new_tgt))
	else:
		fixed_pairs = pairs_list
	structural_problems: Dict[int,List[str]] = {}
	if structural_guard:
		for idx,(src,tgt) in enumerate(fixed_pairs):
			src_fp = generate_structural_fingerprint(src)
			tgt_fp = generate_structural_fingerprint(tgt)
			probs = compare_fingerprint(src_fp, tgt_fp, threshold=structural_guard_threshold)
			if probs:
				structural_problems[idx] = probs
	# Phase-1 Guard (optional): wenn verfügbar, sicherstellen, dass Integrität nicht gebrochen wurde
	reverted_pairs: Dict[int, str] = {}
	if phase1_guard:
		try:
			from quality_gui_phase1_checkers import check_placeholders, check_brackets_basic, check_urls_emails
			guarded_pairs = []
			for idx,(src,tgt) in enumerate(fixed_pairs):
				new_issues = check_placeholders(src, tgt) + check_brackets_basic(src, tgt) + check_urls_emails(src, tgt)
				# Wenn durch Auto-Fix neue Integritätsfehler entstanden: Änderung verwerfen
				if any(getattr(i,'severity','info') in ("critical","major") for i in new_issues):
					guarded_pairs.append((src, pairs_list[idx][1]))  # revert to original target
					try:
						reverted_pairs[idx] = ",".join(sorted({getattr(i,'code','') for i in new_issues})) or 'phase1_guard_violation'
					except Exception:
						reverted_pairs[idx] = 'phase1_guard_violation'
				else:
					guarded_pairs.append((src, tgt))
			fixed_pairs = guarded_pairs
		except Exception:
			pass
	gated = False
	gate_reasons: List[str] = []
	dist = {k:0 for k in ['critical','major','minor','info']}
	for iss in issues:
		sev = getattr(iss, 'severity', 'info') or 'info'
		dist[sev.lower()] = dist.get(sev.lower(),0)+1
	if ci_gate:
		crit_max = ci_gate.get('critical_max',0)
		maj_max = ci_gate.get('major_max',5)
		risk_max = ci_gate.get('risk_score_max', 100)
		# risk_score placeholder (Phase4 liefert sonst). Hier einfacher Proxy.
		proxy_risk = dist['critical']*50 + dist['major']*20 + dist['minor']*5
		if dist['critical'] > crit_max:
			gated = True; gate_reasons.append(f"critical>{crit_max}")
		if dist['major'] > maj_max:
			gated = True; gate_reasons.append(f"major>{maj_max}")
		if proxy_risk > risk_max:
			gated = True; gate_reasons.append(f"risk>{risk_max}")
		block_on = ci_gate.get('block_on_patterns') or []
		for patt in block_on:
			if any(patt in iss.code for iss in issues):
				gated = True; gate_reasons.append(f"pattern:{patt}")
				break
	baseline = load_baseline(baseline_path) if baseline_path else {}
	current_issue_keys = {_issue_key(i): i for i in issues}
	waived = {}
	remaining_issues: List[QAIssue] = []
	for k, iss in current_issue_keys.items():
		if k in baseline:
			meta = baseline[k]
			exp = meta.get('expires')
			if not exp or exp > int(time.time()):
				waived[k] = meta
				continue
			else:
				# Abgelaufene Waiver entfernen, um Datei klein zu halten
				try:
					baseline.pop(k, None)
				except Exception:
					pass
		remaining_issues.append(iss)
	if update_baseline and baseline_path:
		for k in current_issue_keys:
			if k not in baseline:
				baseline[k] = {'added': int(time.time()), 'expires': int(time.time()) + 30*86400}
		save_baseline(baseline_path, baseline)
	artifacts = {}
	if artifact_dir:
		try:
			os.makedirs(artifact_dir, exist_ok=True)
			# diff artifact
			diff_lines = []
			for (s0,t0),(s1,t1) in zip(pairs_list, fixed_pairs):
				if t0 != t1:
					diff_lines.extend(difflib.unified_diff(t0.splitlines(), t1.splitlines(), fromfile='target_before', tofile='target_after', lineterm=''))
			with open(os.path.join(artifact_dir,'autofix.diff'),'w',encoding='utf-8') as f:
				f.write('\n'.join(diff_lines))
			# vollständige Pairs sichern
			with open(os.path.join(artifact_dir,'pairs.json'),'w',encoding='utf-8') as f:
				json.dump({'original': pairs_list, 'fixed': fixed_pairs}, f, ensure_ascii=False, indent=2)
			with open(os.path.join(artifact_dir,'issues.json'),'w',encoding='utf-8') as f:
				json.dump([i.__dict__ for i in remaining_issues], f, ensure_ascii=False, indent=2)
			artifacts['paths'] = ['autofix.diff','issues.json']
		except Exception:
			pass
	return {
		'fixed_pairs': fixed_pairs,
		'applied_fixes': {k:[f.__dict__ for f in v] for k,v in sorted(fixes.items())},
		'structural_problems': {k: structural_problems[k] for k in sorted(structural_problems.keys())},
		'gated': gated,
		'gate_reasons': gate_reasons,
		'issues_remaining': remaining_issues,
		'waived': waived,
		'severity_distribution': dist,
		'artifacts': artifacts,
		'autofix_stats': dict(sorted(autofix_stats_global.items())),
		'reverted_pairs': reverted_pairs,
	}

__all__ = ['enforce_phase5','AppliedFix','apply_auto_fixes']
