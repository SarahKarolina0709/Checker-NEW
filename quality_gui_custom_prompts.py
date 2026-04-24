#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""quality_gui_custom_prompts – Benutzerdefinierte KI-Prüfungen.

Ermöglicht es, spezifische Fragen an die KI zu stellen,
die den gesamten Text daraufhin untersucht.

Beispiele:
- "Prüfe ob alle Produktnamen korrekt übersetzt wurden"
- "Achte besonders auf formelle/informelle Anrede"
- "Gibt es Anglizismen die vermieden werden sollten?"
- "Sind technische Fachbegriffe konsistent übersetzt?"
"""
from __future__ import annotations
import os
import json
import threading
import time
from typing import Any, Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

# ============================================================================
# Ollama Integration
# ============================================================================

_call_ollama = None

try:
    from quality_gui_ollama_suggestions import _call_ollama as suggestions_call
    _call_ollama = suggestions_call
except Exception:
    pass

if _call_ollama is None:
    # Direkter Fallback
    from urllib.request import Request, urlopen
    
    def _direct_call(prompt: str, model: str = "mistral", timeout: int = 120) -> str:
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
    
    _call_ollama = _direct_call


# ============================================================================
# Vordefinierte Prüfungs-Templates
# ============================================================================

PREDEFINED_CHECKS = {
    'terminology': {
        'name': 'Terminologie-Konsistenz',
        'description': 'Prüft ob Fachbegriffe konsistent übersetzt wurden',
        'prompt': '''Analysiere die folgenden Übersetzungspaare auf Terminologie-Konsistenz.
Finde Fachbegriffe die unterschiedlich übersetzt wurden.
Liste jeden inkonsistenten Begriff mit den verschiedenen Übersetzungen auf.'''
    },
    'formality': {
        'name': 'Anrede-Konsistenz',
        'description': 'Prüft ob formelle/informelle Anrede konsistent ist',
        'prompt': '''Analysiere die Übersetzungen auf Konsistenz der Anrede.
Prüfe ob durchgehend "Sie" (formell) oder "du" (informell) verwendet wird.
Liste alle Stellen auf wo die Anrede wechselt oder inkonsistent ist.'''
    },
    'anglicisms': {
        'name': 'Anglizismen',
        'description': 'Findet unnötige Anglizismen in der Übersetzung',
        'prompt': '''Finde englische Wörter oder Anglizismen in den deutschen Übersetzungen,
die durch deutsche Begriffe ersetzt werden könnten.
Liste jeden Anglizismus mit einem deutschen Alternativvorschlag auf.'''
    },
    'product_names': {
        'name': 'Produktnamen',
        'description': 'Prüft ob Produktnamen korrekt behandelt wurden',
        'prompt': '''Analysiere die Übersetzungen auf Produktnamen, Markennamen und Eigennamen.
Prüfe ob diese korrekt beibehalten oder angemessen angepasst wurden.
Liste problematische Fälle auf.'''
    },
    'numbers_units': {
        'name': 'Zahlen & Einheiten',
        'description': 'Prüft Zahlen, Währungen und Maßeinheiten',
        'prompt': '''Prüfe alle Zahlen, Währungen und Maßeinheiten in den Übersetzungen.
Achte auf: korrekte Übernahme, richtige Formatierung (Dezimaltrennzeichen),
und korrekte Einheiten-Konvertierung falls nötig.'''
    },
    'style': {
        'name': 'Stil & Ton',
        'description': 'Bewertet den Schreibstil und Ton',
        'prompt': '''Bewerte den Schreibstil und Ton der Übersetzungen.
Ist der Stil konsistent? Passt der Ton zum Ausgangstext?
Gibt es Stellen die zu formell, zu umgangssprachlich oder unpassend klingen?'''
    },
    'completeness': {
        'name': 'Vollständigkeit',
        'description': 'Prüft ob alle Inhalte übersetzt wurden',
        'prompt': '''Prüfe ob die Übersetzungen vollständig sind.
Finde fehlende Inhalte, ausgelassene Sätze oder nicht übersetzte Passagen.
Liste alle unvollständigen Übersetzungen auf.'''
    },
    'cultural': {
        'name': 'Kulturelle Anpassung',
        'description': 'Prüft kulturelle Angemessenheit',
        'prompt': '''Analysiere die Übersetzungen auf kulturelle Angemessenheit.
Gibt es Redewendungen, Metaphern oder kulturelle Referenzen die nicht passend übersetzt wurden?
Schlage bessere Alternativen vor.'''
    }
}


# ============================================================================
# Custom Check Result
# ============================================================================

@dataclass
class CustomCheckResult:
    """Ergebnis einer benutzerdefinierten Prüfung."""
    question: str
    answer: str
    findings: List[Dict[str, Any]] = field(default_factory=list)
    model: str = ""
    generation_time: float = 0.0
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'question': self.question,
            'answer': self.answer,
            'findings': self.findings,
            'model': self.model,
            'generation_time': self.generation_time,
            'error': self.error,
            'timestamp': self.timestamp
        }


# ============================================================================
# Custom Check Analyzer
# ============================================================================

class CustomCheckAnalyzer:
    """Führt benutzerdefinierte KI-Prüfungen durch."""
    
    def __init__(self, model: str = "mistral", timeout: int = 120):
        self.model = model
        self.timeout = timeout
    
    def analyze(self, 
                question: str,
                pairs: List[Tuple[str, str]],
                max_pairs: int = 50) -> CustomCheckResult:
        """Führt eine benutzerdefinierte Prüfung durch.
        
        Args:
            question: Die Frage/Prüfanweisung
            pairs: Liste von (source, target) Paaren
            max_pairs: Maximale Anzahl zu prüfender Paare
            
        Returns:
            CustomCheckResult mit Antwort und Findings
        """
        if not pairs:
            return CustomCheckResult(
                question=question,
                answer="",
                error="Keine Textpaare zum Analysieren"
            )
        
        # Paare für Prompt vorbereiten (limitiert)
        selected_pairs = pairs[:max_pairs]
        pairs_text = self._format_pairs(selected_pairs)
        
        # Prompt erstellen
        prompt = self._build_prompt(question, pairs_text, len(pairs))
        
        # Ollama anfragen
        start_time = time.time()
        try:
            response = _call_ollama(prompt, model=self.model, timeout=self.timeout)
            generation_time = time.time() - start_time
            
            if not response:
                return CustomCheckResult(
                    question=question,
                    answer="",
                    error="Keine Antwort von Ollama erhalten"
                )
            
            # Antwort parsen
            findings = self._parse_findings(response)
            
            return CustomCheckResult(
                question=question,
                answer=response,
                findings=findings,
                model=self.model,
                generation_time=generation_time
            )
            
        except Exception as e:
            return CustomCheckResult(
                question=question,
                answer="",
                error=f"Fehler: {str(e)[:100]}"
            )
    
    def _format_pairs(self, pairs: List[Tuple[str, str]]) -> str:
        """Formatiert Paare für den Prompt."""
        lines = []
        for i, (src, tgt) in enumerate(pairs, 1):
            src_clean = (src or "").strip()[:200]
            tgt_clean = (tgt or "").strip()[:200]
            lines.append(f"[{i}] Quelle: {src_clean}")
            lines.append(f"    Übersetzung: {tgt_clean}")
            lines.append("")
        return "\n".join(lines)
    
    def _build_prompt(self, question: str, pairs_text: str, total_count: int) -> str:
        """Erstellt den Analyse-Prompt."""
        return f'''Du bist ein Experte für Übersetzungsqualität. 
Analysiere die folgenden Übersetzungspaare basierend auf dieser Frage/Anweisung:

=== PRÜFANWEISUNG ===
{question}

=== ÜBERSETZUNGSPAARE ({total_count} Segmente) ===
{pairs_text}

=== AUFGABE ===
1. Analysiere alle Paare gemäß der Prüfanweisung
2. Liste konkrete Probleme mit Segment-Nummer auf
3. Gib für jedes Problem einen Verbesserungsvorschlag

Antworte auf Deutsch in diesem Format:

## Zusammenfassung
[Kurze Zusammenfassung der Ergebnisse]

## Gefundene Probleme
- [Segment X]: [Problem] → Vorschlag: [Verbesserung]
- [Segment Y]: [Problem] → Vorschlag: [Verbesserung]
...

## Empfehlung
[Abschließende Empfehlung]'''
    
    def _parse_findings(self, response: str) -> List[Dict[str, Any]]:
        """Extrahiert strukturierte Findings aus der Antwort."""
        findings = []
        
        try:
            lines = response.split('\n')
            in_problems = False
            
            for line in lines:
                line = line.strip()
                
                if 'Gefundene Probleme' in line or 'Probleme' in line:
                    in_problems = True
                    continue
                
                if line.startswith('## ') and 'Probleme' not in line:
                    in_problems = False
                    continue
                
                if in_problems and line.startswith('- ['):
                    # Parse: "- [Segment X]: Problem → Vorschlag: Verbesserung"
                    try:
                        # Segment-Nummer extrahieren
                        seg_match = line.split(']')[0].replace('- [', '').replace('Segment ', '')
                        seg_num = int(''.join(filter(str.isdigit, seg_match))) if seg_match else 0
                        
                        # Rest der Zeile
                        rest = line.split(']:')[-1].strip() if ']:' in line else line
                        
                        # Problem und Vorschlag trennen
                        if '→' in rest or '->' in rest:
                            parts = rest.replace('->', '→').split('→')
                            problem = parts[0].strip()
                            suggestion = parts[1].replace('Vorschlag:', '').strip() if len(parts) > 1 else ''
                        else:
                            problem = rest
                            suggestion = ''
                        
                        findings.append({
                            'segment_index': seg_num,
                            'rule_id': 'CUSTOM_CHECK',
                            'severity': 'minor',
                            'category': 'custom',
                            'message': problem,
                            'suggestion': suggestion,
                            'checker': 'ollama'
                        })
                    except Exception:
                        continue
        except Exception:
            pass
        
        return findings
    
    def analyze_async(self,
                      question: str,
                      pairs: List[Tuple[str, str]],
                      callback: Callable[[CustomCheckResult], None],
                      max_pairs: int = 50):
        """Führt Prüfung asynchron durch."""
        def _worker():
            result = self.analyze(question, pairs, max_pairs)
            callback(result)
        
        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()


# ============================================================================
# Convenience Functions
# ============================================================================

def run_custom_check(question: str,
                     pairs: List[Tuple[str, str]],
                     model: str = "mistral") -> CustomCheckResult:
    """Führt eine benutzerdefinierte Prüfung durch."""
    analyzer = CustomCheckAnalyzer(model=model)
    return analyzer.analyze(question, pairs)


def run_predefined_check(check_id: str,
                         pairs: List[Tuple[str, str]],
                         model: str = "mistral") -> CustomCheckResult:
    """Führt eine vordefinierte Prüfung durch."""
    if check_id not in PREDEFINED_CHECKS:
        return CustomCheckResult(
            question=check_id,
            answer="",
            error=f"Unbekannte Prüfung: {check_id}"
        )
    
    check = PREDEFINED_CHECKS[check_id]
    analyzer = CustomCheckAnalyzer(model=model)
    return analyzer.analyze(check['prompt'], pairs)


def get_predefined_checks() -> Dict[str, Dict[str, str]]:
    """Gibt alle vordefinierten Prüfungen zurück."""
    return {
        k: {'name': v['name'], 'description': v['description']}
        for k, v in PREDEFINED_CHECKS.items()
    }


# ============================================================================
# Test
# ============================================================================

if __name__ == '__main__':
    print("=== Custom Prompts Test ===\n")
    
    # Test-Paare
    test_pairs = [
        ("Click the Save button to continue.", "Klicken Sie den Save Button um fortzufahren."),
        ("Please enter your email address.", "Bitte geben Sie Ihre E-Mail-Adresse ein."),
        ("The file has been uploaded successfully.", "Die Datei wurde erfolgreich hochgeladen."),
        ("Click here to download the PDF.", "Klicke hier um das PDF herunterzuladen."),
        ("Your order has been confirmed.", "Ihre Bestellung wurde bestätigt."),
    ]
    
    print("Vordefinierte Prüfungen:")
    for check_id, info in get_predefined_checks().items():
        print(f"  - {check_id}: {info['name']}")
    
    print("\n--- Test: Anglizismen-Prüfung ---")
    print("(Ollama muss laufen für echten Test)")
    
    # Simulierter Test ohne Ollama
    result = CustomCheckResult(
        question="Finde Anglizismen",
        answer="## Zusammenfassung\nEs wurden 2 Anglizismen gefunden.\n\n## Gefundene Probleme\n- [Segment 1]: 'Save Button' ist ein Anglizismus → Vorschlag: 'Speichern-Schaltfläche'\n- [Segment 4]: 'PDF' könnte als 'PDF-Datei' verdeutlicht werden → Vorschlag: 'die PDF-Datei'",
        findings=[
            {'segment_index': 1, 'message': "'Save Button' ist ein Anglizismus", 'suggestion': "'Speichern-Schaltfläche'"},
            {'segment_index': 4, 'message': "'PDF' könnte verdeutlicht werden", 'suggestion': "'die PDF-Datei'"}
        ],
        model="mistral",
        generation_time=5.2
    )
    
    print(f"\nFrage: {result.question}")
    print(f"Findings: {len(result.findings)}")
    for f in result.findings:
        print(f"  - Segment {f['segment_index']}: {f['message']}")
