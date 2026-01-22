"""quality_gui_phase3_checkers – finale Migration (ursprünglich qa_phase3_checkers).

Semantik / Stil / Risiko / Lesbarkeit (Phase 3). Optional semantische Ähnlichkeit.
"""
from __future__ import annotations
from typing import Iterable, Tuple, List, Dict, Optional, Any
import re
from collections import Counter

try:
	from quality_gui_grammar import GrammarChecker  # type: ignore
except Exception:  # pragma: no cover - optional dependency
	GrammarChecker = None  # type: ignore

try:
	import language_tool_python  # type: ignore
except Exception:  # pragma: no cover - optional dependency
	language_tool_python = None  # type: ignore

try:
	from spellchecker import SpellChecker  # type: ignore
except Exception:  # pragma: no cover - optional dependency
	SpellChecker = None  # type: ignore

try:
	from quality_gui_phase1_checkers import QAIssue  # type: ignore
except Exception:  # Fallback Mini-Dataclass
	from dataclasses import dataclass
	@dataclass
	class QAIssue:  # type: ignore
		code: str; severity: str; category: str; message: str; source: str; target: str; meta: dict | None = None

ABBR = r"(z\. ?B\.|u\. ?a\.|d\. ?h\.|bzw\.|ca\.|Nr\.|vgl\.)"
ABBR_RX = re.compile(r'\b(?:z\. ?B\.|u\. ?a\.|d\. ?h\.|bzw\.|ca\.|Nr\.|vgl\.)')
PLHDR = '§'
WORD_SPLIT = re.compile(r'[^\W_]+', re.UNICODE)
# Sequenzen direkt im Fließtext finden (beinhaltet + / =, die sonst nicht in \w liegen)
BASE64_SEQ = re.compile(r'(?i)[A-Za-z0-9+/=]{44,}')
BASE64_PATTERN = re.compile(r'(?i)^[A-Za-z0-9+/]{44,}={0,2}$')
LANGUAGE_TOOL_CODES = {
	"de": "de-DE",
	"en": "en-US",
	"fr": "fr-FR",
	"es": "es-ES",
	"it": "it-IT"
}

FALLBACK_LEXICONS: Dict[str, Counter[str]] = {
	"de": Counter({
		"und": 50,
		"der": 45,
		"die": 45,
		"das": 40,
		"hallo": 35,
		"qualität": 20,
		"übersetzung": 20,
		"bitte": 18,
		"danke": 15,
		"kunde": 12,
		"projekt": 12,
		"bericht": 11,
		"prüfung": 10,
		"lieferung": 10,
		"hinweis": 8,
		"analyse": 8,
		"term": 6,
		"liste": 6,
		"schritt": 6
	}),
	"en": Counter({
		"the": 60,
		"and": 50,
		"hello": 35,
		"world": 32,
		"quality": 20,
		"translation": 20,
		"please": 18,
		"thank": 15,
		"customer": 12,
		"project": 12,
		"report": 11,
		"review": 10,
		"delivery": 10,
		"note": 8,
		"analysis": 8,
		"term": 6,
		"list": 6,
		"step": 6
	})
}


class _SpellcheckEngine:
	"""Kapselt optionale Spell-/Grammar-Prüfung mit Fallback."""

	def __init__(self, config: Dict[str, Any]):
		self.config = config
		self.language = (config.get("target_language") or "de").lower()
		self.max_issues = int(config.get("max_issues_per_segment", 3) or 3)
		self.use_language_tool = bool(config.get("use_language_tool", False))
		self.custom_words = {w.lower(): True for w in config.get("custom_dictionary", []) if isinstance(w, str)}
		self._engine = None
		self._backend = "fallback"
		self._init_backend()

	def _init_backend(self) -> None:
		if self.use_language_tool and language_tool_python:
			code = LANGUAGE_TOOL_CODES.get(self.language, self.language)
			try:
				self._engine = language_tool_python.LanguageTool(code)  # type: ignore
				self._backend = "language_tool"
				return
			except Exception:
				self._engine = None
		if SpellChecker:
			try:
				checker = SpellChecker(language=self.language)
				for word in self.custom_words:
					checker.word_frequency.add(word)
				self._engine = checker
				self._backend = "spellchecker"
				return
			except Exception:
				self._engine = None
		self._backend = "fallback"

	def _tokenize(self, text: str) -> List[str]:
		return [w.lower() for w in WORD_SPLIT.findall(text or "") if len(w) > 1]

	def _fallback_unknown(self, tokens: List[str]) -> List[str]:
		lexicon = FALLBACK_LEXICONS.get(self.language, FALLBACK_LEXICONS.get("en", Counter()))
		unknown = []
		for token in tokens:
			if token in self.custom_words:
				continue
			if token not in lexicon:
				unknown.append(token)
		return unknown

	def analyze(self, text: str) -> List[Dict[str, Any]]:
		if not text or not text.strip():
			return []
		if self._backend == "language_tool" and self._engine:
			try:
				matches = self._engine.check(text)  # type: ignore[attr-defined]
				recommendations: List[Dict[str, Any]] = []
				for match in matches[: self.max_issues]:
					word = text[match.offset : match.offset + match.errorLength]  # type: ignore[index]
					recommendations.append({
						"word": word,
						"message": match.message,  # type: ignore[attr-defined]
						"suggestions": list(match.replacements)[:3]  # type: ignore[attr-defined]
					})
				return recommendations
			except Exception:
				pass
		if self._backend == "spellchecker" and self._engine:
			tokens = self._tokenize(text)
			try:
				unknown = list(self._engine.unknown(tokens))  # type: ignore[attr-defined]
			except Exception:
				unknown = []
			issues: List[Dict[str, Any]] = []
			for token in unknown[: self.max_issues]:
				suggest = []
				try:
					suggest = self._engine.candidates(token)  # type: ignore[attr-defined]
				except Exception:
					suggest = []
				issues.append({
					"word": token,
					"message": "Möglicher Rechtschreibfehler",
					"suggestions": list(suggest)[:3]
				})
			return issues
		tokens = self._tokenize(text)
		unknown = self._fallback_unknown(tokens)
		return [
			{"word": token, "message": "Unbekanntes Wort erkannt", "suggestions": []}
			for token in unknown[: self.max_issues]
		]

# Ausschlüsse für Base64 False Positives
HEX_LONG = re.compile(r'^[0-9a-fA-F]{40,}$')
JWT_PATTERN = re.compile(r'^[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+$')

DOMAIN_PATTERN = re.compile(r'https?://([^\s/):]+)(?::\d+)?', re.IGNORECASE)
ATTR_STYLE_PATTERN = re.compile(r'<[^>]*\sstyle\s*=', re.IGNORECASE)
DATA_URI_PATTERN = re.compile(r'data:\s*[a-z]+/[a-z0-9+.-]+(?:;base64)?', re.IGNORECASE)
# engeres werden-Passiv (kein sein+Partizip)
PASSIVE_DE_WERDEN = re.compile(r'\b(wird|wurden|wurde|werden)\b(?:\s+\w+){0,3}\s+ge\w+(?:t|en)\b', re.IGNORECASE)
PASSIVE_DE_SEIN_WORDEN = re.compile(r'\b(ist|sind|war|waren|sei|seien|gewesen)\b(?:\s+\w+){0,4}\s+ge\w+(?:t|en)\s+worden\b', re.IGNORECASE)
PASSIVE_EN_PATTERN = re.compile(r'\b(?:was|were|is|are|been|being)\b(?:\s+\w+){0,2}\s+\w+(?:ed|en)\b', re.IGNORECASE)

def _clean_domains(domains: Iterable[str]) -> List[str]:
	cleaned: List[str] = []
	for d in domains:
		if not d:
			continue
		x = d.strip().lower()
		# Nur Randzeichen gezielt entfernen (keine Zeichenmengen via lstrip/rstrip)
		while x and x[0] in "([{\"'":
			x = x[1:]
		while x and x[-1] in "),.;:'\"}]":
			x = x[:-1]
		if x.startswith('www.'):
			x = x[4:]
		cleaned.append(x)
	return cleaned

def _split_sentences(text: str) -> List[str]:
	if not text:
		return []
	t = text.replace("“ ", "“").replace("„ ", "„")
	protected = ABBR_RX.sub(lambda m: m.group(0).replace('.', PLHDR), t.strip())
	parts = re.split(r'(?<=[.!?])\s+', protected)
	return [p.replace(PLHDR, '.').strip() for p in parts if p.strip()]

def _avg(values: List[float]) -> float:
	return sum(values)/len(values) if values else 0.0

def check_style(src: str, tgt: str) -> List[QAIssue]:
	issues: List[QAIssue] = []
	sents = _split_sentences(tgt)
	if not sents:
		return issues
	long_sents = [s for s in sents if len(s) > 220]
	if long_sents:
		issues.append(QAIssue("STYLE_LONG_SENTENCE", "minor", "style",
							 f"{len(long_sents)} sehr lange Sätze (>220 Zeichen)", src, tgt, {"examples": long_sents[:3]}))
	# DE Passiv (werden + sein+worden)
	passive_hits_de = PASSIVE_DE_WERDEN.findall(tgt) + PASSIVE_DE_SEIN_WORDEN.findall(tgt)
	if len(passive_hits_de) >= 3 and len(passive_hits_de) / max(1, len(sents)) > 0.4:
		issues.append(QAIssue("STYLE_PASSIVE_HEAVY_DE", "minor", "style",
							 "Hoher Anteil Passiv (DE)", src, tgt, {"count": len(passive_hits_de)}))
	tokens = WORD_SPLIT.findall(tgt)
	if tokens:
		ascii_ratio = sum(1 for t in tokens if re.fullmatch(r'[a-zA-Z]+', t)) / len(tokens)
		if ascii_ratio > 0.55:
			passive_hits_en = PASSIVE_EN_PATTERN.findall(tgt)
			if len(passive_hits_en) >= 3 and len(passive_hits_en) / max(1, len(sents)) > 0.35:
				issues.append(QAIssue("STYLE_PASSIVE_HEAVY_EN", "minor", "style",
							 "Hoher Anteil Passiv (EN)", src, tgt, {"count": len(passive_hits_en)}))
	return issues

def check_risk(src: str, tgt: str, *, complement_phase2: bool = True) -> List[QAIssue]:
	issues: List[QAIssue] = []
	src_domains = set(_clean_domains(DOMAIN_PATTERN.findall(src or '')))
	tgt_domains = set(_clean_domains(DOMAIN_PATTERN.findall(tgt or '')))
	new_domains = [d for d in tgt_domains if d not in src_domains]
	if new_domains:
		issues.append(QAIssue("RISK_NEW_DOMAIN", "major", "risk", f"Neue Domain(s) im Ziel: {new_domains[:5]}", src, tgt, {"domains": new_domains[:10]}))
	# Base64 Sequenzen prüfen – Quelle als Rohtext berücksichtigen
	src_text = src or ''
	for m in BASE64_SEQ.finditer(tgt or ''):
		_tok = m.group(0)
		if token_is_base64_suspect(_tok, src_text):
			issues.append(QAIssue("RISK_BASE64_SUSPECT", "major", "risk", "Verdächtiger Base64-ähnlicher Block", src, tgt, {"token": _tok[:60]}))
			break
	if complement_phase2:
		# Inline-Style nur werten, wenn echtes HTML-Attribut
		if ATTR_STYLE_PATTERN.search(tgt) and not ATTR_STYLE_PATTERN.search(src_text):
			issues.append(QAIssue("RISK_INLINE_STYLE", "minor", "risk", "Neues inline style Attribut", src, tgt))
		if DATA_URI_PATTERN.search(tgt) and not DATA_URI_PATTERN.search(src_text):
			issues.append(QAIssue("RISK_DATA_URI", "major", "risk", "Neuer data: URI im Ziel", src, tgt))
	return issues

def _compute_lix(text: str) -> Optional[float]:
	sents = _split_sentences(text)
	words = WORD_SPLIT.findall(text)
	if not sents or not words:
		return None
	long_words = sum(1 for w in words if len(w) > 6)
	return (len(words)/len(sents)) + (long_words * 100.0 / len(words))

def check_readability(src: str, tgt: str, *,
					  avg_len_thr: int = 140,
					  very_long_len: int = 180,
					  very_long_ratio: float = 0.30,
					  staccato_short_len: int = 25,
					  staccato_min_short: int = 3,
					  staccato_ratio: float = 0.60,
					  lix_thr: float = 55.0,
					  staccato_gate_qe_ratio: float = 0.40) -> List[QAIssue]:
	issues: List[QAIssue] = []
	sents = _split_sentences(tgt)
	if not sents:
		return issues
	lengths = [len(s) for s in sents]
	avg_len = _avg(lengths)
	very_short = sum(1 for l in lengths if l < staccato_short_len)
	very_long = sum(1 for l in lengths if l > very_long_len)
	if avg_len > avg_len_thr:
		issues.append(QAIssue("READABILITY_TOO_LONG", "minor", "readability", f"Hohe durchschnittliche Satzlänge ({int(avg_len)})", src, tgt))
	if very_long >= 2 and very_long / max(1,len(sents)) > very_long_ratio:
		issues.append(QAIssue("READABILITY_MANY_LONG", "minor", "readability", f"Viele sehr lange Sätze ({very_long})", src, tgt))
	qe_ratio = (tgt.count('?') + tgt.count('!')) / max(1, len(sents))
	if qe_ratio < staccato_gate_qe_ratio:
		if (any(l > 60 for l in lengths) or avg_len > 60) and very_short >= staccato_min_short and very_short / max(1,len(sents)) > staccato_ratio:
			issues.append(QAIssue("READABILITY_STACCATTO", "minor", "readability", "Viele extrem kurze Sätze (Stakkato)", src, tgt))
	lix = _compute_lix(tgt)
	if lix and lix > lix_thr:
		issues.append(QAIssue("READABILITY_LIX_HIGH", "minor", "readability", f"Hoher LIX Index ({lix:.1f})", src, tgt, {"lix": round(lix,1)}))
	return issues

def token_is_base64_suspect(tok: str, src_text: str) -> bool:
	if not tok:
		return False
	if tok in (src_text or ''):
		return False
	# Mindestlänge höher für geringere False Positives
	if len(tok) < 44 or len(tok) % 4 != 0:
		return False
	# Ausschlüsse: HEX-IDs, JWTs
	if HEX_LONG.match(tok) or JWT_PATTERN.match(tok):
		return False
	if not BASE64_PATTERN.match(tok):
		return False
	return True

def check_semantic_similarity(pairs: Iterable[Tuple[str,str]], threshold: float = 0.70, *,
							  use_ollama: bool = False,
							  ollama_model: str = 'nomic-embed-text') -> List[QAIssue]:
	issues: List[QAIssue] = []
	try:
		import hashlib, json, os, time as _t
		cache_dir = os.environ.get('QUALITY_GUI_SEMANTIC_CACHE_DIR') or os.path.join(os.getcwd(), 'semantic_cache')
		try:
			if not os.path.isdir(cache_dir):
				os.makedirs(cache_dir, exist_ok=True)
		except Exception:
			cache_dir = None
		memory_cache = getattr(check_semantic_similarity, '_mem', None)
		if memory_cache is None:
			memory_cache = {}
			setattr(check_semantic_similarity, '_mem', memory_cache)
		# Optional Netzwerk komplett deaktivieren
		if os.environ.get('QUALITY_GUI_DISABLE_NETWORK', '0') == '1':
			use_ollama = False
		backend = 'st'
		model = None; tok = None; mdl = None; use_util = True
		if use_ollama:
			try:
				import requests
				_host = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')
				_resp = requests.post(f"{_host}/api/embeddings", json={"model": ollama_model, "prompt": "test"}, timeout=4)
				if _resp.ok:
					backend = 'ollama'
					def _ollama_embed(texts):
						out = []
						for _t_text in texts:
							r = requests.post(f"{_host}/api/embeddings", json={"model": ollama_model, "prompt": _t_text}, timeout=30)
							if r.ok:
								data = r.json(); out.append(data.get('embedding'))
							else:
								out.append(None)
						return out
			except Exception:
				backend = 'st'
		if backend == 'st':
			try:
				from sentence_transformers import SentenceTransformer  # type: ignore
				# Device-Auswahl (env override)
				_device = None
				try:
					import torch  # type: ignore
					if os.environ.get('QUALITY_GUI_DEVICE'):
						_device = os.environ['QUALITY_GUI_DEVICE']
					else:
						_device = 'cuda' if torch.cuda.is_available() else 'cpu'
				except Exception:
					_device = 'cpu'
				model = SentenceTransformer('paraphrase-MiniLM-L6-v2', device=_device)
				use_util = True
			except Exception:
				try:
					from transformers import AutoTokenizer, AutoModel  # type: ignore
					import torch  # type: ignore
					tok = AutoTokenizer.from_pretrained('sentence-transformers/paraphrase-MiniLM-L6-v2')
					mdl = AutoModel.from_pretrained('sentence-transformers/paraphrase-MiniLM-L6-v2')
					if os.environ.get('QUALITY_GUI_DEVICE'):
						_dev = os.environ['QUALITY_GUI_DEVICE']
					else:
						_dev = 'cuda' if torch.cuda.is_available() else 'cpu'
					mdl.to(_dev)
					use_util = False
				except Exception:
					return []
		def _embed_pair(s: str, t: str) -> Optional[float]:
			try:
				model_id = f"{backend}:{ollama_model if backend=='ollama' else 'paraphrase-MiniLM-L6-v2'}"
				key_raw = f"{len(s)}:{len(t)}::{s[:1024]}|||{t[:1024]}|{model_id}".encode('utf-8','ignore')
				key = hashlib.sha256(key_raw).hexdigest()
				if key in memory_cache:
					return memory_cache[key]
				if cache_dir:
					disk_path = os.path.join(cache_dir, key[:2] + '.json')
					try:
						if os.path.isfile(disk_path):
							with open(disk_path, 'r', encoding='utf-8') as _rf:
								bucket = json.load(_rf)
							if key in bucket:
								memory_cache[key] = float(bucket[key]['sim']); return memory_cache[key]
					except Exception:
						pass
				if backend == 'ollama':
					vecs = _ollama_embed([s, t])  # type: ignore
					if not vecs[0] or not vecs[1]:
						return None
					# Pure-Python Cosine ohne NumPy
					def _cos(u, v):
						dot = 0.0
						ss_u = 0.0; ss_v = 0.0
						for x, y in zip(u, v):
							dot += x * y
							ss_u += x * x
							ss_v += y * y
						nu = ss_u ** 0.5; nv = ss_v ** 0.5
						den = (nu * nv) or 1.0
						return float(dot / den)
					sim_val = _cos(vecs[0], vecs[1])
				else:
					if use_util:
						emb = model.encode([s, t], convert_to_tensor=True, normalize_embeddings=True)
						sim_val = float((emb[0] @ emb[1]).item())
					else:
						try:
							import torch  # type: ignore
						except Exception:
							return None
						with torch.no_grad():
							a_ids = tok(s, return_tensors='pt', truncation=True, max_length=256)
							b_ids = tok(t, return_tensors='pt', truncation=True, max_length=256)
							a_out = mdl(**a_ids).last_hidden_state.mean(dim=1)
							b_out = mdl(**b_ids).last_hidden_state.mean(dim=1)
							a_n = a_out / a_out.norm(dim=1, keepdim=True)
							b_n = b_out / b_out.norm(dim=1, keepdim=True)
							sim_val = float((a_n * b_n).sum())
				memory_cache[key] = sim_val
				if cache_dir:
					try:
						disk_path = os.path.join(cache_dir, key[:2] + '.json')
						bucket = {}
						if os.path.isfile(disk_path):
							try:
								with open(disk_path,'r',encoding='utf-8') as _rf:
									bucket = json.load(_rf)
							except Exception:
								bucket = {}
						bucket[key] = {'sim': sim_val, 'ts': int(_t.time())}
						if len(bucket) > 400:
							try:
								items = sorted(bucket.items(), key=lambda x: x[1].get('ts',0), reverse=True)[:350]
								bucket = {k:v for k,v in items}
							except Exception:
								pass
						with open(disk_path,'w',encoding='utf-8') as _f:
							import json as _json
							_json.dump(bucket, _f, ensure_ascii=False)
					except Exception:
						pass
				return sim_val
			except Exception:
				return None
		similarities: List[float] = []
		below_threshold = 0
		# Sampling / Pair Cap
		max_pairs = int(os.getenv("QUALITY_GUI_SEMANTIC_MAX_PAIRS", "400"))
		pairs_list = list(pairs)
		if len(pairs_list) > max_pairs:
			step = max(1, len(pairs_list) // (max_pairs - 20))
			pairs_list = pairs_list[:10] + pairs_list[10::step][:max_pairs-10]
		for src, tgt in pairs_list:
			if not src or not tgt or len(src) < 15:
				continue
			sl = len(src)
			dyn = 0.65 if sl < 60 else (0.70 if sl < 120 else 0.75)
			eff_thr = max(threshold, dyn)
			try:
				sim = _embed_pair(src, tgt)
				if sim is None:
					continue
				similarities.append(sim)
				if sim < eff_thr:
					below_threshold += 1
					issues.append(QAIssue("SEMANTIC_LOW", "minor", "semantic", f"Semantische Ähnlichkeit niedrig ({sim:.2f} < {eff_thr:.2f})", src[:120], tgt[:120], {"similarity": round(sim,3), "threshold": eff_thr}))
			except Exception:
				continue
		if similarities:
			avg_sim = sum(similarities)/len(similarities)
			ratio_low = below_threshold / len(similarities)
			if avg_sim < 0.72 and ratio_low > 0.35 and len(similarities) >= 5:
				issues.append(QAIssue("SEMANTIC_GLOBAL_LOW", "minor", "semantic", f"Globale Semantik schwach: Schnitt {avg_sim:.2f}, {ratio_low*100:.0f}% unter Schwelle", "", "", {"avg": round(avg_sim,3), "low_ratio": round(ratio_low,3), "count": len(similarities)}))
	except Exception:
		return []
	return issues

def run_phase3_checks(pairs: Iterable[Tuple[str,str]], *, enable_semantic: bool = True,
						  semantic_use_ollama: bool = False,
						  semantic_ollama_model: str = 'nomic-embed-text',
						  risk_complement_phase2: bool = True,
						  semantic_threshold: float = 0.70,
						  # Readability tuning (optional)
						  avg_len_thr: int = 140,
						  very_long_len: int = 180,
						  very_long_ratio: float = 0.30,
						  staccato_short_len: int = 25,
						  staccato_min_short: int = 3,
						  staccato_ratio: float = 0.60,
						  lix_thr: float = 55.0,
						  staccato_gate_qe_ratio: float = 0.40,
						  spellcheck_config: Optional[Dict[str, Any]] = None,
						  pair_infos: Optional[List[Dict[str, Any]]] = None) -> List[QAIssue]:
	all_pairs = list(pairs)
	issues: List[QAIssue] = []
	grammar_checker = None
	grammar_findings: Dict[int, List[Dict[str, Any]]] = {}
	spell_engine: Optional[_SpellcheckEngine] = None
	grammar_limit = 0
	if spellcheck_config and spellcheck_config.get("enabled", True):
		grammar_limit = int(spellcheck_config.get("max_issues_per_segment", 0) or 0)
		if GrammarChecker is not None:
			try:
				grammar_checker = GrammarChecker(
					enable_languagetool=bool(spellcheck_config.get("use_language_tool", True)),
					enable_hunspell=bool(spellcheck_config.get("use_hunspell", True)),
					enable_ollama=bool(spellcheck_config.get("use_ollama", True)),
					ratio_threshold=float(spellcheck_config.get("ratio_threshold", 0.15) or 0.15),
					batch_lt_min_segments=int(spellcheck_config.get("batch_lt_min_segments", 40) or 40)
				)
				target_segments = [tgt if isinstance(tgt, str) else str(tgt or "") for _, tgt in all_pairs]
				target_lang = spellcheck_config.get("target_language") or spellcheck_config.get("language") or spellcheck_config.get("locale")
				if isinstance(target_lang, dict):
					target_lang = target_lang.get("target") or target_lang.get("language")
				language = str(target_lang or "auto")
				raw_grammar = grammar_checker.analyze_segments(target_segments, language=language)
				for entry in raw_grammar:
					idx = entry.get("segment_index")
					if not isinstance(idx, int) or idx < 0 or idx >= len(all_pairs):
						continue
					bucket = grammar_findings.setdefault(idx, [])
					if grammar_limit and len(bucket) >= grammar_limit:
						continue
					bucket.append(entry)
			except Exception:
				grammar_checker = None
				grammar_findings.clear()
	if spellcheck_config and not grammar_checker:
		try:
			if spellcheck_config.get("enabled", True):
				spell_engine = _SpellcheckEngine(spellcheck_config)
		except Exception:
			spell_engine = None
	for idx, (src, tgt) in enumerate(all_pairs):
		pair_meta: Dict[str, Any] = {}
		if pair_infos and idx < len(pair_infos):
			candidate = pair_infos[idx]
			if isinstance(candidate, dict):
				pair_meta = candidate
		issues.extend(check_style(src, tgt))
		issues.extend(check_risk(src, tgt, complement_phase2=risk_complement_phase2))
		issues.extend(check_readability(
			src, tgt,
			avg_len_thr=avg_len_thr,
			very_long_len=very_long_len,
			very_long_ratio=very_long_ratio,
			staccato_short_len=staccato_short_len,
			staccato_min_short=staccato_min_short,
			staccato_ratio=staccato_ratio,
			lix_thr=lix_thr,
			staccato_gate_qe_ratio=staccato_gate_qe_ratio,
		))
		if grammar_checker:
			for entry in grammar_findings.get(idx, []):
				severity = str(entry.get("severity", "minor") or "minor").lower()
				if severity not in ("minor", "major", "critical"):
					severity = "minor"
				meta_payload: Dict[str, Any] = {
					"checker": entry.get("checker"),
					"suggestion": entry.get("suggestion"),
					"excerpt": entry.get("source_excerpt")
				}
				if pair_meta:
					meta_payload["pair"] = {
						"index": pair_meta.get("index", idx),
						"source": pair_meta.get("source_name"),
						"target": pair_meta.get("translation_name")
					}
				issues.append(QAIssue(
					entry.get("rule_id", "GRAMMAR"),
					severity,
					"grammar",
					entry.get("message", ""),
					src,
					tgt,
					meta_payload
				))
		elif spell_engine:
			for finding in spell_engine.analyze(tgt):
				meta_payload = {"details": finding}
				if pair_meta:
					meta_payload["pair"] = {
						"index": pair_meta.get("index", idx),
						"source": pair_meta.get("source_name"),
						"target": pair_meta.get("translation_name")
					}
				issues.append(QAIssue(
					"SPELLING_ERROR",
					"major",
					"orthografie",
					f"Möglicher Rechtschreib-/Grammatikfehler: {finding.get('word', '')}",
					src,
					tgt,
					meta_payload
				))
	if enable_semantic:
		issues.extend(check_semantic_similarity(all_pairs, threshold=semantic_threshold, use_ollama=semantic_use_ollama, ollama_model=semantic_ollama_model))
	return issues

__all__ = [
	'run_phase3_checks',
	'check_style',
	'check_risk',
	'check_readability',
	'check_semantic_similarity'
]
