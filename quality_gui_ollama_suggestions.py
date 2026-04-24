#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""quality_gui_ollama_suggestions – KI-gestützte Korrekturvorschläge.

Nutzt Ollama um intelligente Korrekturvorschläge für Übersetzungsfehler zu generieren.

Features:
- Einzelne Finding-Korrektur
- Batch-Korrektur für mehrere Findings
- Kontextbezogene Verbesserungsvorschläge
- Caching von Vorschlägen
"""
from __future__ import annotations
import os
import json
import hashlib
import threading
from typing import Any, Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import time

# ============================================================================
# Ollama Client
# ============================================================================

_ollama_available = False
_call_ollama = None

try:
    from ki_module import _call_ollama as ki_call_ollama
    _call_ollama = ki_call_ollama
    _ollama_available = True
except (ImportError, SyntaxError):
    pass
except Exception:
    pass

if not _ollama_available:
    try:
        from tools.query_ollama_translation import call_ollama as tools_call_ollama
        _call_ollama = tools_call_ollama
        _ollama_available = True
    except (ImportError, SyntaxError):
        pass
    except Exception:
        pass

# Fallback: Direkter Ollama-Aufruf per HTTP
if not _ollama_available:
    import json
    from urllib.request import Request, urlopen
    from urllib.error import URLError
    
    def _direct_ollama_call(prompt: str, model: str = "mistral", timeout: int = 60) -> str:
        """Direkter HTTP-Aufruf an Ollama API."""
        url = "http://localhost:11434/api/generate"
        data = json.dumps({
            "model": model,
            "prompt": prompt,
            "stream": False
        }).encode('utf-8')
        
        req = Request(url, data=data, headers={'Content-Type': 'application/json'})
        try:
            with urlopen(req, timeout=timeout) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                return result.get('response', '')
        except Exception:
            return ""
    
    _call_ollama = _direct_ollama_call
    _ollama_available = True


def is_ollama_available() -> bool:
    """Prüft ob Ollama verfügbar ist."""
    return _ollama_available and _call_ollama is not None


def check_ollama_connection(timeout: float = 3.0) -> Tuple[bool, str]:
    """Prüft ob Ollama erreichbar ist.
    
    Returns:
        (erreichbar, info_text)
    """
    if not is_ollama_available():
        return False, "Ollama-Modul nicht verfügbar"
    
    try:
        import socket
        host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        # Parse host
        if "://" in host:
            host = host.split("://")[1]
        if ":" in host:
            host, port_str = host.split(":")
            port = int(port_str.split("/")[0])
        else:
            host = host.split("/")[0]
            port = 11434
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            return True, f"Ollama erreichbar ({host}:{port})"
        else:
            return False, f"Ollama nicht erreichbar ({host}:{port})"
    except Exception as e:
        return False, f"Verbindungsfehler: {str(e)[:50]}"


# ============================================================================
# Suggestion Cache
# ============================================================================

_suggestion_cache: Dict[str, Dict[str, Any]] = {}
_cache_lock = threading.Lock()


def _cache_key(source: str, target: str, rule_id: str) -> str:
    """Generiert einen Cache-Key für ein Finding."""
    content = f"{source}|{target}|{rule_id}"
    return hashlib.md5(content.encode('utf-8')).hexdigest()[:16]


def get_cached_suggestion(source: str, target: str, rule_id: str) -> Optional[Dict[str, Any]]:
    """Holt gecachten Vorschlag falls vorhanden."""
    key = _cache_key(source, target, rule_id)
    with _cache_lock:
        return _suggestion_cache.get(key)


def cache_suggestion(source: str, target: str, rule_id: str, suggestion: Dict[str, Any]):
    """Speichert Vorschlag im Cache."""
    key = _cache_key(source, target, rule_id)
    with _cache_lock:
        _suggestion_cache[key] = {
            **suggestion,
            'cached_at': datetime.now().isoformat()
        }


# ============================================================================
# Prompt Templates
# ============================================================================

CORRECTION_PROMPT_DE = """Du bist ein Experte für Übersetzungsqualität. Analysiere das folgende Übersetzungsproblem und schlage eine Korrektur vor.

QUELLTEXT (Original):
{source}

AKTUELLE ÜBERSETZUNG:
{target}

ERKANNTES PROBLEM:
{problem}

FEHLERTYP: {rule_id}

Bitte antworte NUR im folgenden JSON-Format:
{{
  "korrigierte_uebersetzung": "Die korrigierte Übersetzung hier",
  "erklaerung": "Kurze Erklärung was falsch war und warum die Korrektur besser ist",
  "konfidenz": 0.95
}}

Antworte NUR mit dem JSON, ohne zusätzlichen Text."""

CORRECTION_PROMPT_EN = """You are a translation quality expert. Analyze the following translation issue and suggest a correction.

SOURCE TEXT (Original):
{source}

CURRENT TRANSLATION:
{target}

DETECTED PROBLEM:
{problem}

ERROR TYPE: {rule_id}

Please respond ONLY in the following JSON format:
{{
  "corrected_translation": "The corrected translation here",
  "explanation": "Brief explanation of what was wrong and why the correction is better",
  "confidence": 0.95
}}

Respond ONLY with the JSON, no additional text."""

BATCH_CORRECTION_PROMPT = """Du bist ein Experte für Übersetzungsqualität. Korrigiere die folgenden Übersetzungsfehler.

{findings_text}

Antworte NUR im folgenden JSON-Format (Array von Korrekturen):
[
  {{
    "index": 0,
    "korrigierte_uebersetzung": "Korrektur für Segment 0",
    "erklaerung": "Kurze Erklärung"
  }},
  ...
]

Antworte NUR mit dem JSON-Array, ohne zusätzlichen Text."""


# ============================================================================
# Suggestion Generator
# ============================================================================

@dataclass
class CorrectionSuggestion:
    """Ein Korrekturvorschlag von Ollama."""
    original_target: str
    corrected_target: str
    explanation: str
    confidence: float = 0.0
    model: str = ""
    generation_time: float = 0.0
    from_cache: bool = False
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'original_target': self.original_target,
            'corrected_target': self.corrected_target,
            'explanation': self.explanation,
            'confidence': self.confidence,
            'model': self.model,
            'generation_time': self.generation_time,
            'from_cache': self.from_cache,
            'error': self.error
        }


class OllamaSuggestionGenerator:
    """Generiert Korrekturvorschläge mit Ollama."""
    
    def __init__(self, 
                 model: str = "mistral",
                 timeout: int = 60,
                 language: str = "de"):
        """
        Args:
            model: Ollama-Modell (z.B. mistral, llama2, gemma)
            timeout: Timeout in Sekunden
            language: Sprache für Prompts (de/en)
        """
        self.model = model
        self.timeout = timeout
        self.language = language
        self._prompt_template = CORRECTION_PROMPT_DE if language == "de" else CORRECTION_PROMPT_EN
    
    def generate_suggestion(self, 
                           source: str, 
                           target: str, 
                           problem: str,
                           rule_id: str = "",
                           use_cache: bool = True) -> CorrectionSuggestion:
        """Generiert einen Korrekturvorschlag für ein Finding.
        
        Args:
            source: Quelltext
            target: Aktuelle Übersetzung
            problem: Beschreibung des Problems
            rule_id: Fehlertyp/Regel-ID
            use_cache: Cache nutzen
            
        Returns:
            CorrectionSuggestion mit Korrektur oder Fehler
        """
        # Cache prüfen
        if use_cache:
            cached = get_cached_suggestion(source, target, rule_id)
            if cached:
                return CorrectionSuggestion(
                    original_target=target,
                    corrected_target=cached.get('corrected_target', ''),
                    explanation=cached.get('explanation', ''),
                    confidence=cached.get('confidence', 0.0),
                    model=cached.get('model', self.model),
                    generation_time=0.0,
                    from_cache=True
                )
        
        # Ollama verfügbar?
        if not is_ollama_available():
            return CorrectionSuggestion(
                original_target=target,
                corrected_target="",
                explanation="",
                error="Ollama nicht verfügbar"
            )
        
        # Prompt erstellen
        prompt = self._prompt_template.format(
            source=source[:500],  # Limit
            target=target[:500],
            problem=problem[:300],
            rule_id=rule_id or "UNKNOWN"
        )
        
        # Ollama anfragen
        start_time = time.time()
        try:
            response = _call_ollama(prompt, model=self.model, timeout=self.timeout)
            generation_time = time.time() - start_time
            
            if not response:
                return CorrectionSuggestion(
                    original_target=target,
                    corrected_target="",
                    explanation="",
                    error="Keine Antwort von Ollama"
                )
            
            # JSON parsen
            result = self._parse_response(response)
            
            if result.get('error'):
                return CorrectionSuggestion(
                    original_target=target,
                    corrected_target="",
                    explanation="",
                    error=result['error']
                )
            
            suggestion = CorrectionSuggestion(
                original_target=target,
                corrected_target=result.get('corrected_target', ''),
                explanation=result.get('explanation', ''),
                confidence=float(result.get('confidence', 0.8)),
                model=self.model,
                generation_time=generation_time
            )
            
            # Cache speichern
            if use_cache and suggestion.corrected_target:
                cache_suggestion(source, target, rule_id, suggestion.to_dict())
            
            return suggestion
            
        except Exception as e:
            return CorrectionSuggestion(
                original_target=target,
                corrected_target="",
                explanation="",
                error=f"Fehler: {str(e)[:100]}"
            )
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parst die Ollama-Antwort."""
        try:
            # JSON extrahieren
            text = response.strip()
            
            # Versuche JSON zu finden
            start_idx = text.find('{')
            end_idx = text.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                json_str = text[start_idx:end_idx + 1]
                data = json.loads(json_str)
                
                # Normalisiere Feldnamen (DE/EN)
                return {
                    'corrected_target': data.get('korrigierte_uebersetzung') or data.get('corrected_translation', ''),
                    'explanation': data.get('erklaerung') or data.get('explanation', ''),
                    'confidence': data.get('konfidenz') or data.get('confidence', 0.8)
                }
            
            # Fallback: Gesamte Antwort als Korrektur
            return {
                'corrected_target': text[:500],
                'explanation': 'Direkte Antwort (kein JSON)',
                'confidence': 0.5
            }
            
        except json.JSONDecodeError as e:
            return {'error': f'JSON-Parsing fehlgeschlagen: {str(e)[:50]}'}
        except Exception as e:
            return {'error': f'Parsing-Fehler: {str(e)[:50]}'}
    
    def generate_batch_suggestions(self,
                                   findings: List[Dict[str, Any]],
                                   max_batch_size: int = 5,
                                   callback: Optional[Callable[[int, int], None]] = None
                                   ) -> List[CorrectionSuggestion]:
        """Generiert Korrekturvorschläge für mehrere Findings.
        
        Args:
            findings: Liste von Finding-Dicts
            max_batch_size: Max Findings pro Batch
            callback: Progress-Callback (current, total)
            
        Returns:
            Liste von CorrectionSuggestion
        """
        results: List[CorrectionSuggestion] = []
        total = len(findings)
        
        for i, finding in enumerate(findings):
            if callback:
                callback(i, total)
            
            source = finding.get('source') or finding.get('source_text') or ''
            target = finding.get('target') or finding.get('target_text') or ''
            problem = finding.get('message') or ''
            rule_id = finding.get('rule_id') or finding.get('rule') or ''
            
            suggestion = self.generate_suggestion(source, target, problem, rule_id)
            results.append(suggestion)
        
        if callback:
            callback(total, total)
        
        return results


# ============================================================================
# Convenience Functions
# ============================================================================

_default_generator: Optional[OllamaSuggestionGenerator] = None


def get_suggestion(finding: Dict[str, Any],
                   model: str = "mistral",
                   language: str = "de") -> CorrectionSuggestion:
    """Generiert einen Korrekturvorschlag für ein Finding.
    
    Args:
        finding: Finding-Dict mit source, target, message, rule_id
        model: Ollama-Modell
        language: Sprache (de/en)
        
    Returns:
        CorrectionSuggestion
    """
    global _default_generator
    
    if _default_generator is None or _default_generator.model != model:
        _default_generator = OllamaSuggestionGenerator(model=model, language=language)
    
    source = finding.get('source') or finding.get('source_text') or ''
    target = finding.get('target') or finding.get('target_text') or ''
    problem = finding.get('message') or ''
    rule_id = finding.get('rule_id') or finding.get('rule') or ''
    
    return _default_generator.generate_suggestion(source, target, problem, rule_id)


def get_suggestion_async(finding: Dict[str, Any],
                         callback: Callable[[CorrectionSuggestion], None],
                         model: str = "mistral",
                         language: str = "de"):
    """Generiert Korrekturvorschlag asynchron.
    
    Args:
        finding: Finding-Dict
        callback: Wird mit Ergebnis aufgerufen
        model: Ollama-Modell
        language: Sprache
    """
    def _worker():
        result = get_suggestion(finding, model, language)
        callback(result)
    
    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()


# ============================================================================
# Test
# ============================================================================

if __name__ == '__main__':
    print("=== Ollama Suggestion Generator Test ===\n")
    
    available, info = check_ollama_connection()
    print(f"Ollama Status: {info}")
    
    if available:
        # Test-Finding
        test_finding = {
            'source': 'Click the button to continue.',
            'target': 'Klicken Sie den Button um fortzufahren.',
            'message': 'Fehlende Übersetzung von "button" - sollte "Schaltfläche" sein',
            'rule_id': 'TERMINOLOGY_LOW'
        }
        
        print(f"\nTest-Finding:")
        print(f"  Quelle: {test_finding['source']}")
        print(f"  Ziel: {test_finding['target']}")
        print(f"  Problem: {test_finding['message']}")
        
        print("\nGeneriere Korrekturvorschlag...")
        suggestion = get_suggestion(test_finding, model="mistral")
        
        if suggestion.error:
            print(f"Fehler: {suggestion.error}")
        else:
            print(f"\nKorrektur: {suggestion.corrected_target}")
            print(f"Erklärung: {suggestion.explanation}")
            print(f"Konfidenz: {suggestion.confidence:.0%}")
            print(f"Zeit: {suggestion.generation_time:.2f}s")
    else:
        print("\nOllama nicht verfügbar - Test übersprungen")
