"""quality_gui_pairing_manager

Kapselt Pairing-spezifische Operationen (Undo/Redo, Similarity, Persistenz).
Schrittweise Extraktion aus quality_gui_main_app zur Reduktion von Komplexität.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple, Callable, Sequence
from contextlib import contextmanager
import json
import time
import os
import tempfile
import logging

_logger = logging.getLogger(__name__)

try:  # Optional externe Utilities
    from pairing_utils import smart_pair_files  # type: ignore
except Exception:  # pragma: no cover
    smart_pair_files = None  # type: ignore

PairDict = Dict[str, Any]

@dataclass
class PairRecord:
    source: str
    translation: str

@dataclass
class PairingState:
    pairs: List[PairRecord] = field(default_factory=list)
    unmatched_sources: List[str] = field(default_factory=list)
    unmatched_translations: List[str] = field(default_factory=list)
    last_update_ts: float = 0.0

class PairingHistoryManager:
    """Verwaltet Undo/Redo Historie für Pairing-Aktionen."""
    def __init__(self, capacity: int = 100):
        self._history: List[PairingState] = []
        self._redo: List[PairingState] = []
        self._capacity = capacity

    def snapshot(self, state: PairingState):
        self._history.append(self._clone(state))
        if len(self._history) > self._capacity:
            self._history.pop(0)
        self._redo.clear()

    def undo(self, current: PairingState) -> PairingState | None:
        # Erwartung: current == letzter Snapshot; gib den vorherigen zurück
        if len(self._history) <= 1:
            return None
        # Aktuellen Stand in den Redo-Stack schieben
        self._redo.append(self._clone(self._history.pop()))
        # Jetzt zeigt -1 auf den vorherigen Zustand
        return self._clone(self._history[-1])

    def redo(self, current: PairingState) -> PairingState | None:
        if not self._redo:
            return None
        nxt = self._redo.pop()
        self._history.append(self._clone(nxt))
        return self._clone(nxt)

    def _clone(self, st: PairingState) -> PairingState:
        return PairingState(
            pairs=[PairRecord(p.source, p.translation) for p in st.pairs],
            unmatched_sources=list(st.unmatched_sources),
            unmatched_translations=list(st.unmatched_translations),
            last_update_ts=st.last_update_ts
        )

class QualityGuiPairingManager:
    """High-Level Pairing Manager (Similarity & Persistenz)."""

    def __init__(self):
        self.state = PairingState()
        self.history = PairingHistoryManager()
        self._legacy_pairs: List[PairDict] = []
        self._legacy_unmatched: Dict[str, List[str]] = {'source': [], 'translation': []}
        # Pfad der letzten Persistenz (für erneutes Speichern ohne Basis-Pfad)
        self._last_persist_path = None  # type: Optional[str]
        # letzter Fehlertext aus load/save
        self._last_error: Optional[str] = None

    # --------------- Transactions & Snapshots ---------------
    def _snapshot(self):
        """Aktualisiert Timestamp, persistiert Snapshot und hält Legacy-Ansichten synchron."""
        self.state.last_update_ts = time.time()
        self.history.snapshot(self.state)
        self._sync_legacy()

    @contextmanager
    def transaction(self):
        """Bündelt mehrere Mutationen zu genau einem Snapshot am Ende."""
        before = self._state_fingerprint()
        try:
            yield
        finally:
            if self._state_fingerprint() != before:
                self._snapshot()

    def _state_fingerprint(self) -> tuple:
        """Erstellt einen leichten Fingerprint des States um No-Op-Transaktionen zu erkennen."""
        return (
            tuple((p.source, p.translation) for p in self.state.pairs),
            tuple(self.state.unmatched_sources),
            tuple(self.state.unmatched_translations),
        )

    # ---------------- Public API ----------------
    def set_pairs(self, pairs: Sequence[Tuple[str, str]]):
        with self.transaction():
            self.state.pairs = [PairRecord(a, b) for a, b in pairs]

    def add_pair(self, source: str, translation: str):
        with self.transaction():
            self.state.pairs.append(PairRecord(source, translation))

    def remove_pair(self, source: str, translation: str):
        with self.transaction():
            self.state.pairs = [p for p in self.state.pairs if not (p.source == source and p.translation == translation)]

    def clear(self):
        """Leert alle Paarungen und unmatched Files (mit History-Snapshot)."""
        with self.transaction():
            self.state.pairs.clear()
            self.state.unmatched_sources.clear()
            self.state.unmatched_translations.clear()
        self._legacy_pairs = []
        self._legacy_unmatched = {'source': [], 'translation': []}

    def undo(self) -> Optional[PairingState]:
        prev = self.history.undo(self.state)
        if prev is None:
            return None
        self.state = prev
        self._sync_legacy()
        return self.state

    def redo(self) -> Optional[PairingState]:
        nxt = self.history.redo(self.state)
        if nxt is None:
            return None
        self.state = nxt
        self._sync_legacy()
        return self.state

    # ---------------- Smart Pairing ----------------
    def run_smart_pairing(self, source_files: List[str], translation_files: List[str], pairing_service_supplier: Optional[Callable[[], object]] = None) -> Tuple[List[PairDict], Dict[str, List[str]]]:
        pairs: List[PairDict] = []
        unmatched: Dict[str, List[str]] = {'source': [], 'translation': []}
        if not source_files and not translation_files:
            # State aktiv leeren + snapshotten für konsistente UI/Persistenz
            self._legacy_pairs = []
            self._legacy_unmatched = unmatched
            with self.transaction():
                self.state.pairs.clear()
                self.state.unmatched_sources.clear()
                self.state.unmatched_translations.clear()
            return [], unmatched
        try:
            # Smart Pairing via PairingService (Score-Matrix + globales Ranking)
            service = None
            if pairing_service_supplier:
                try:
                    service = pairing_service_supplier()
                except Exception:
                    pass
            if not service:
                try:
                    from neutral_pairing_service import get_pairing_service
                    service = get_pairing_service()
                except Exception:
                    service = None

            if service and hasattr(service, 'pair'):
                raw_pairs, um_src, um_trg = service.pair(source_files, translation_files)
                for p in raw_pairs:
                    pairs.append({
                        'source': p.source,
                        'translation': p.translation,
                        'similarity': getattr(p, 'similarity', 0.0),
                        'source_name': getattr(p, 'source_name', os.path.basename(p.source)),
                        'translation_name': getattr(p, 'translation_name', os.path.basename(p.translation)),
                        'source_lang': getattr(p, 'source_lang', None),
                        'translation_lang': getattr(p, 'translation_lang', None),
                    })
                unmatched = {'source': um_src, 'translation': um_trg}
            elif smart_pair_files:
                service_factory = pairing_service_supplier if pairing_service_supplier else (lambda: None)
                raw_pairs, um_src, um_trg = smart_pair_files(source_files, translation_files, service_factory)
                for p in raw_pairs:
                    pairs.append({
                        'source': p.source,
                        'translation': p.translation,
                        'similarity': getattr(p, 'similarity', 0.0),
                        'source_name': getattr(p, 'source_name', os.path.basename(p.source)),
                        'translation_name': getattr(p, 'translation_name', os.path.basename(p.translation)),
                    })
                unmatched = {'source': um_src, 'translation': um_trg}
            else:
                # Letzter Fallback: Similarity-basiert mit eigenem Algorithmus
                from itertools import product
                scored = [(s, t, self.similarity(s, t)) for s, t in product(source_files, translation_files)]
                scored.sort(key=lambda x: x[2], reverse=True)
                used_s, used_t = set(), set()
                for s, t, sim in scored:
                    if s in used_s or t in used_t:
                        continue
                    pairs.append({
                        'source': s, 'translation': t,
                        'similarity': sim,
                        'source_name': os.path.basename(s),
                        'translation_name': os.path.basename(t)
                    })
                    used_s.add(s)
                    used_t.add(t)
                unmatched = {
                    'source': [s for s in source_files if s not in used_s],
                    'translation': [t for t in translation_files if t not in used_t]
                }
        except Exception:
            unmatched = {'source': list(source_files), 'translation': list(translation_files)}
            pairs = []
        # deterministische Sortierung für stabile Anzeige
        try:
            pairs.sort(key=lambda p: (p.get('source_name', '' ).casefold(), p.get('translation_name','').casefold()))
            unmatched['source'].sort(key=lambda s: os.path.basename(s).casefold())
            unmatched['translation'].sort(key=lambda s: os.path.basename(s).casefold())
        except Exception:
            pass
        self._legacy_pairs = pairs
        self._legacy_unmatched = unmatched
        self.state.pairs = [PairRecord(p['source'], p['translation']) for p in pairs]
        self.state.unmatched_sources = list(unmatched['source'])
        self.state.unmatched_translations = list(unmatched['translation'])
        # ein Snapshot für den gesamten Smart-Pairing-Vorgang
        self.state.last_update_ts = time.time()
        self.history.snapshot(self.state)
        self._sync_legacy()
        return pairs, unmatched

    # ---------------- Manual Pairing ----------------
    def add_manual_pair(self, source: str, translation: str, similarity: float = 1.0) -> bool:
        # einfache Validierungen & Dedupe
        if not source or not translation or source == translation:
            return False
        if any(p['source'] == source or p['translation'] == translation for p in self._legacy_pairs):
            return False
        new_pair = {
            'source': source,
            'translation': translation,
            'similarity': similarity,
            'source_name': os.path.basename(source),
            'translation_name': os.path.basename(translation)
        }
        self._legacy_pairs.append(new_pair)
        if source in self._legacy_unmatched.get('source', []):
            self._legacy_unmatched['source'].remove(source)
        if translation in self._legacy_unmatched.get('translation', []):
            self._legacy_unmatched['translation'].remove(translation)
        self._sync_state_from_legacy()
        self.history.snapshot(self.state)
        return True

    def remove_pair_by_index(self, index: int) -> Optional[PairDict]:
        if index < 0 or index >= len(self._legacy_pairs):
            return None
        removed = self._legacy_pairs.pop(index)
        src = removed['source']
        trg = removed['translation']
        if src not in self._legacy_unmatched['source']:
            self._legacy_unmatched['source'].append(src)
        if trg not in self._legacy_unmatched['translation']:
            self._legacy_unmatched['translation'].append(trg)
        # deterministische Sortierung beibehalten
        try:
            self._legacy_unmatched['source'].sort(key=lambda s: os.path.basename(s).casefold())
            self._legacy_unmatched['translation'].sort(key=lambda s: os.path.basename(s).casefold())
        except Exception:
            pass
        self._sync_state_from_legacy()
        self.history.snapshot(self.state)
        return removed
    
    def auto_pair_unmatched(self, threshold: float = 0.7) -> int:
        """🔧 NEU: Versucht automatisch ungematchte Dateien zu paaren.
        
        Args:
            threshold: Mindest-Similarity für automatisches Pairing
            
        Returns:
            Anzahl der neu erstellten Paare
        """
        if not self._legacy_unmatched.get('source') or not self._legacy_unmatched.get('translation'):
            return 0
        
        new_pairs = 0
        sources_to_remove = []
        translations_to_remove = []
        
        # Alle möglichen Paarungen mit Scores berechnen
        candidates: List[Tuple[str, str, float]] = []
        for src in self._legacy_unmatched.get('source', []):
            for trg in self._legacy_unmatched.get('translation', []):
                sim = self.similarity(src, trg)
                if sim >= threshold:
                    candidates.append((src, trg, sim))
        
        # Sortiere nach höchster Similarity
        candidates.sort(key=lambda x: x[2], reverse=True)
        
        # Greedy Matching: Beste Paare zuerst
        used_sources = set()
        used_translations = set()
        
        for src, trg, sim in candidates:
            if src in used_sources or trg in used_translations:
                continue
            
            # Paar erstellen
            new_pair = {
                'source': src,
                'translation': trg,
                'similarity': sim,
                'source_name': os.path.basename(src),
                'translation_name': os.path.basename(trg),
                'auto_paired': True  # 🔧 NEU: Markierung für Auto-Pairing
            }
            self._legacy_pairs.append(new_pair)
            
            used_sources.add(src)
            used_translations.add(trg)
            sources_to_remove.append(src)
            translations_to_remove.append(trg)
            new_pairs += 1
        
        # Aus unmatched entfernen
        for src in sources_to_remove:
            if src in self._legacy_unmatched['source']:
                self._legacy_unmatched['source'].remove(src)
        for trg in translations_to_remove:
            if trg in self._legacy_unmatched['translation']:
                self._legacy_unmatched['translation'].remove(trg)
        
        if new_pairs > 0:
            self._sync_state_from_legacy()
            self.history.snapshot(self.state)
        
        return new_pairs
    
    def get_low_confidence_pairs(self, threshold: float = 0.7) -> List[PairDict]:
        """🔧 NEU: Gibt Paare mit niedriger Similarity zurück (zur Überprüfung).
        
        Returns:
            Liste von Paaren unter dem Threshold
        """
        return [
            p for p in self._legacy_pairs 
            if p.get('similarity', 0.0) < threshold
        ]
    
    def get_pairing_statistics(self) -> Dict[str, Any]:
        """🔧 NEU: Gibt Statistiken über die aktuelle Paarung zurück."""
        pairs = self._legacy_pairs
        unmatched = self._legacy_unmatched
        
        if not pairs:
            return {
                'total_pairs': 0,
                'high_confidence': 0,
                'medium_confidence': 0,
                'low_confidence': 0,
                'avg_similarity': 0.0,
                'unmatched_sources': len(unmatched.get('source', [])),
                'unmatched_translations': len(unmatched.get('translation', [])),
                'auto_paired': 0
            }
        
        similarities = [p.get('similarity', 0.0) for p in pairs]
        high = sum(1 for s in similarities if s >= 0.85)
        medium = sum(1 for s in similarities if 0.7 <= s < 0.85)
        low = sum(1 for s in similarities if s < 0.7)
        auto = sum(1 for p in pairs if p.get('auto_paired', False))
        
        return {
            'total_pairs': len(pairs),
            'high_confidence': high,
            'medium_confidence': medium,
            'low_confidence': low,
            'avg_similarity': sum(similarities) / len(similarities) if similarities else 0.0,
            'min_similarity': min(similarities) if similarities else 0.0,
            'max_similarity': max(similarities) if similarities else 0.0,
            'unmatched_sources': len(unmatched.get('source', [])),
            'unmatched_translations': len(unmatched.get('translation', [])),
            'auto_paired': auto
        }

    # ---------------- Legacy Helpers ----------------
    def get_legacy_pairs(self) -> List[PairDict]:
        return list(self._legacy_pairs)

    def get_legacy_unmatched(self) -> Dict[str, List[str]]:
        return {
            'source': list(self._legacy_unmatched.get('source', [])),
            'translation': list(self._legacy_unmatched.get('translation', []))
        }

    # ---------------- Public Setters (statt direktem _legacy_* Zugriff) ----------------
    def set_legacy_pairs(self, pairs: List[PairDict]) -> None:
        """Öffentlicher Setter für Legacy-Pairs. Synchronisiert internen State."""
        self._legacy_pairs = list(pairs) if pairs else []
        self._sync_state_from_legacy()

    def set_legacy_unmatched(self, unmatched: Dict[str, List[str]]) -> None:
        """Öffentlicher Setter für Legacy-Unmatched. Synchronisiert internen State."""
        self._legacy_unmatched = {
            'source': list(unmatched.get('source', [])) if unmatched else [],
            'translation': list(unmatched.get('translation', [])) if unmatched else []
        }
        self._sync_state_from_legacy()

    def restore_from_snapshot(self, pairs: List[PairDict], unmatched: Dict[str, List[str]]) -> None:
        """Stellt State aus einem Snapshot wieder her (für Undo/Redo).
        
        Args:
            pairs: Liste von Pair-Dictionaries
            unmatched: Dict mit 'source' und 'translation' Listen
        """
        self._legacy_pairs = list(pairs) if pairs else []
        self._legacy_unmatched = {
            'source': list(unmatched.get('source', [])) if unmatched else [],
            'translation': list(unmatched.get('translation', [])) if unmatched else []
        }
        self._sync_state_from_legacy()

    def _sync_state_from_legacy(self):
        self.state.pairs = [PairRecord(p['source'], p['translation']) for p in self._legacy_pairs]
        self.state.unmatched_sources = list(self._legacy_unmatched.get('source', []))
        self.state.unmatched_translations = list(self._legacy_unmatched.get('translation', []))
        self.state.last_update_ts = time.time()

    def _sync_legacy(self):
        # vorhandene Similarities und Namen nach Möglichkeit beibehalten
        sim_map = {
            (p.get('source'), p.get('translation')): (
                p.get('similarity', 0.0),
                p.get('source_name', os.path.basename(p.get('source', '') or '')),
                p.get('translation_name', os.path.basename(p.get('translation', '') or '')),
            )
            for p in self._legacy_pairs
        }

        new_legacy: List[PairDict] = []
        for pr in self.state.pairs:
            key = (pr.source, pr.translation)
            sim, sname, tname = sim_map.get(
                key,
                (0.0, os.path.basename(pr.source), os.path.basename(pr.translation))
            )
            new_legacy.append({
                'source': pr.source,
                'translation': pr.translation,
                'similarity': sim,
                'source_name': sname,
                'translation_name': tname,
            })

        self._legacy_pairs = new_legacy
        self._legacy_unmatched = {
            'source': list(self.state.unmatched_sources),
            'translation': list(self.state.unmatched_translations)
        }

    # ---------------- Similarity Placeholder ----------------
    def similarity(self, a: str, b: str) -> float:
        """🔧 VERBESSERT: Erweiterte Similarity-Berechnung mit mehreren Strategien."""
        if not a or not b:
            return 0.0
        a_s = os.path.splitext(os.path.basename(a).casefold())[0]
        b_s = os.path.splitext(os.path.basename(b).casefold())[0]
        if a_s == b_s:
            return 1.0
        
        import re
        
        # Language-Code entfernen für fairen Vergleich (deckungsgleich mit NeutralPairingService)
        lang_pattern = (
            r'[_\-\.](?:de|en|fr|es|it|nl|pl|pt|ru|zh|ja|ko'
            r'|cs|sv|da|fi|nb|nn|hu|ro|bg|hr|sk|sl|et|lv|lt|el|tr|ar|he)'
            r'(?=[_\-\.]|$)'
        )
        a_clean = re.sub(lang_pattern, '', a_s)
        b_clean = re.sub(lang_pattern, '', b_s)

        # Wenn nach Entfernung der Language-Codes identisch
        if a_clean == b_clean:
            return 0.95

        # Gängige Suffixe entfernen — NUR am Anfang/Ende, sonst werden
        # Tokens wie "transformer_" mit Suffix "trans_" zerstört (-> "former_").
        suffixes = [
            '_source', '_target', '_translation', '_translated', '_trans',
            '_original', '_orig', '_src', '_übersetzung', '_übersetzt',
            '_quelle', '_ziel', '_final', '_korrektur', '_review',
            '_draft', '_v2', '_neu', '_clean', '_edited',
            '_proofread', '_lektoriert',
        ]
        prefixes = ['source_', 'target_', 'trans_', 'orig_']
        def _strip_affixes(s: str) -> str:
            changed = True
            while changed:
                changed = False
                for suf in suffixes:
                    if s.endswith(suf) and len(s) > len(suf):
                        s = s[:-len(suf)]
                        changed = True
                for pre in prefixes:
                    if s.startswith(pre) and len(s) > len(pre):
                        s = s[len(pre):]
                        changed = True
            return s
        a_clean = _strip_affixes(a_clean)
        b_clean = _strip_affixes(b_clean)
        a_clean = re.sub(r'_v?\d+$', '', a_clean).strip('_- ')
        b_clean = re.sub(r'_v?\d+$', '', b_clean).strip('_- ')

        if a_clean == b_clean:
            return 0.9
        
        # Token-basierte Jaccard-Ähnlichkeit
        def tok(s: str) -> set[str]:
            return set(filter(None, re.split(r"[\W_]+", s)))
        
        ta, tb = tok(a_clean), tok(b_clean)
        if not ta or not tb:
            return 0.0
            
        inter = len(ta & tb)
        union = len(ta | tb) or 1
        jaccard = inter / union
        
        # 🔧 NEU: Präfix-Bonus
        prefix_len = 0
        for i, (ca, cb) in enumerate(zip(a_clean, b_clean)):
            if ca == cb:
                prefix_len = i + 1
            else:
                break
        
        prefix_bonus = 0.0
        if prefix_len >= 4:
            prefix_bonus = min(0.15, prefix_len / max(len(a_clean), len(b_clean)) * 0.25)
        
        return min(jaccard + prefix_bonus, 1.0)
    
    def suggest_pairs(self, unmatched_sources: List[str], unmatched_translations: List[str], 
                      top_n: int = 3) -> Dict[str, List[Tuple[str, float]]]:
        """🔧 NEU: Schlägt mögliche Paarungen für ungematchte Dateien vor.
        
        Returns:
            Dict mit source -> [(translation, similarity), ...] Top-N Vorschläge
        """
        suggestions: Dict[str, List[Tuple[str, float]]] = {}
        
        for src in unmatched_sources:
            scores = []
            for trg in unmatched_translations:
                sim = self.similarity(src, trg)
                if sim > 0.3:  # Mindest-Threshold für Vorschläge
                    scores.append((trg, sim))
            
            # Sortiere nach Similarity absteigend
            scores.sort(key=lambda x: x[1], reverse=True)
            suggestions[src] = scores[:top_n]
        
        return suggestions

    # ---------------- Public helpers ----------------
    def update_similarity(self, source: str, translation: str, similarity: float) -> bool:
        """Aktualisiert die Similarity eines vorhandenen Legacy-Paares und persistiert sofort.
        Nützlich nach Re-Scoring oder manueller Korrektur.
        """
        updated = False
        for p in self._legacy_pairs:
            if p.get('source') == source and p.get('translation') == translation:
                p['similarity'] = float(similarity)
                updated = True
                break
        if updated:
            self.state.last_update_ts = time.time()
            # Sofort persistieren, damit Similarity-Korrekturen nicht verloren gehen
            self.save()
        return updated

    def get_last_persist_path(self) -> Optional[str]:
        return self._last_persist_path

    # ---------------- Persistence ----------------
    def _resolve_path(self, base: Optional[str]) -> str:
        """Ermittelt den Zielspeicherpfad.
        - Wenn base ein Ordner ist (oder None): nutze base/pairings.json
        - Wenn base wie eine Datei aussieht (z.B. *.json): nutze base direkt
        """
        try:
            if not base:
                bdir = os.path.join('Checker_Projekte', '_default')
                os.makedirs(bdir, exist_ok=True)
                return os.path.join(bdir, 'pairings.json')

            # Ist es ein existierendes Verzeichnis?
            if os.path.isdir(base) or base.endswith(os.sep):
                os.makedirs(base, exist_ok=True)
                return os.path.join(base, 'pairings.json')

            # Sieht nach Datei aus, wenn eine Extension vorhanden ist
            _, ext = os.path.splitext(base)
            if ext:
                os.makedirs(os.path.dirname(base) or '.', exist_ok=True)
                return base

            # sonst als Verzeichnis behandeln
            os.makedirs(base, exist_ok=True)
            return os.path.join(base, 'pairings.json')
        except Exception:
            # robustes Fallback
            bdir = os.path.join('Checker_Projekte', '_default')
            try:
                os.makedirs(bdir, exist_ok=True)
            except Exception:
                pass
            return os.path.join(bdir, 'pairings.json')

    def load(self, base_path: Optional[str] = None) -> bool:
        """Lädt Persistenz wenn vorhanden. Rückgabe True falls erfolgreich."""
        try:
            p = self._resolve_path(base_path)
            self._last_persist_path = p
            if os.path.exists(p):
                with open(p, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self._legacy_pairs = data.get('pairs', [])
                um = data.get('unmatched', {'source': [], 'translation': []})
                self._legacy_unmatched = {'source': um.get('source', []), 'translation': um.get('translation', [])}
                self._sync_state_from_legacy()
                # Metadaten (weich) übernehmen
                try:
                    self.state.last_update_ts = float(data.get('last_update_ts', self.state.last_update_ts or time.time()))
                except Exception:
                    pass
                self._last_error = None
                _logger.debug("Pairing geladen: %d Paare aus %s", len(self._legacy_pairs), p)
                return True
        except Exception as e:
            self._last_error = f"load failed: {e}"
            return False
        return False

    def save(self, base_path: Optional[str] = None) -> bool:
        """Persistiert aktuellen Zustand atomar. Rückgabe True bei Erfolg."""
        try:
            p = self._resolve_path(base_path) if base_path else (self._last_persist_path or self._resolve_path(base_path))
            os.makedirs(os.path.dirname(p), exist_ok=True)
            fd, tmp_path = tempfile.mkstemp(prefix="pairings.", suffix=".json", dir=os.path.dirname(p))
            try:
                with os.fdopen(fd, 'w', encoding='utf-8') as f:
                    json.dump(
                        {
                            'version': 1,
                            'last_update_ts': self.state.last_update_ts,
                            'pairs': self._legacy_pairs,
                            'unmatched': self._legacy_unmatched
                        },
                        f, ensure_ascii=False, indent=2
                    )
                os.replace(tmp_path, p)
            finally:
                try:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
                except Exception:
                    pass
            self._last_persist_path = p
            self._last_error = None
            _logger.debug("Pairing gespeichert: %d Paare nach %s", len(self._legacy_pairs), p)
            return True
        except Exception as e:
            self._last_error = f"save failed: {e}"
            _logger.warning("Pairing-Speichern fehlgeschlagen: %s", e)
            return False

    def get_last_error(self) -> Optional[str]:
        return self._last_error

__all__ = [
    'QualityGuiPairingManager',
    'PairingState',
    'PairRecord',
    'PairingHistoryManager'
]
