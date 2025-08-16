# -*- coding: utf-8 -*-
"""
CustomerManager – schlanker Business-Logic-Manager für Kundendaten.

Ziele:
- Keine Änderungen am bestehenden Welcome-Screen nötig (API-kompatibel).
- Sichere Datei-IO, robuste Fallbacks, keine externen Abhängigkeiten.
- Light-Mode/Design-System betreffen hier nicht, da rein logische Schicht.

Verwendete Methoden (aus welcome_screen.py):
- customer_exists(name) -> bool im if-Context, und auch (exists, matched_name, score) via Unpacking.
- remove_customer(name) -> (success: bool, message: str)
- ensure_customer_project_structure(name, use_date_folder=True)
- update_customer_activity(name)
- search_customers(text, limit=5|8) -> Liste von Diktaten: { 'name': str, 'score': int }
- Attribut customers_data (Liste)
"""
from __future__ import annotations
import json
import os
from datetime import datetime
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional, Tuple, Iterable
from pathlib import Path


class CustomerExistsResult:
    """Ergebnisobjekt, das sowohl in boolschen Kontexten als auch beim Unpacking funktioniert."""
    __slots__ = ("exists", "matched_name", "score")

    def __init__(self, exists: bool, matched_name: Optional[str] = None, score: int = 0):
        self.exists = bool(exists)
        self.matched_name = matched_name
        self.score = int(score or 0)

    def __bool__(self) -> bool:
        return self.exists

    def __iter__(self) -> Iterable[Any]:
        yield self.exists
        yield self.matched_name
        yield self.score


class CustomerManager:
    def __init__(self, customers_file: str = "customers.json", projects_base_path: Optional[str] = None):
        self.customers_file = customers_file
        self.projects_base_path = projects_base_path or os.path.join(os.getcwd(), "Checker_Projekte")
        self.customers_data: List[Any] = []
        self._load()

    # ------------------------------- Persistence -------------------------------
    def _load(self) -> None:
        try:
            if os.path.exists(self.customers_file):
                with open(self.customers_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                # Accept either {"customers": [...]} or list directly
                if isinstance(data, dict) and "customers" in data:
                    self.customers_data = list(data.get("customers") or [])
                elif isinstance(data, list):
                    self.customers_data = list(data)
                else:
                    self.customers_data = []
            else:
                self.customers_data = []
        except Exception:
            # Robust fallback: Leere Liste
            self.customers_data = []

    def _save(self) -> None:
        try:
            payload: Dict[str, Any] = {
                "customers": self.customers_data,
                "last_updated": datetime.now().isoformat(timespec="seconds"),
            }
            with open(self.customers_file, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=4)
        except Exception:
            # Keine harten Fehler werfen – UI funktioniert weiter.
            pass

    # ------------------------------- Utilities --------------------------------
    @staticmethod
    def _normalize_name(name: Any) -> str:
        try:
            return str(name or "").strip().lower()
        except Exception:
            return ""

    @staticmethod
    def _extract_customer_name(customer: Any) -> str:
        if isinstance(customer, str):
            return customer
        if isinstance(customer, dict):
            return str(customer.get("name", ""))
        return str(customer)

    def _best_match(self, query: str) -> Tuple[Optional[str], int]:
        """Findet den besten Fuzzy-Match und gibt (name, score 0-100) zurück."""
        qn = self._normalize_name(query)
        best_name: Optional[str] = None
        best_score: int = 0
        for c in self.customers_data:
            name = self._extract_customer_name(c)
            cn = self._normalize_name(name)
            if not cn:
                continue
            if qn == cn:
                return (name, 100)
            score = int(round(SequenceMatcher(None, qn, cn).ratio() * 100))
            if score > best_score:
                best_score = score
                best_name = name
        return (best_name, best_score)

    # --------------------------------- API -------------------------------------
    def customer_exists(self, name: str) -> CustomerExistsResult:
        """API-kompatibel: im boolschen Kontext ≙ exists; beim Unpacking (exists, matched_name, score)."""
        if not name:
            return CustomerExistsResult(False, None, 0)
        matched, score = self._best_match(name)
        exists = (score == 100)
        return CustomerExistsResult(exists, matched if matched else None, score)

    def search_customers(self, text: str, limit: int = 5) -> List[Dict[str, Any]]:
        text_n = self._normalize_name(text)
        if not text_n:
            # Keine Suche → leere Liste
            return []
        results: List[Tuple[str, int]] = []
        for c in self.customers_data:
            name = self._extract_customer_name(c)
            cn = self._normalize_name(name)
            if not cn:
                continue
            score = int(round(SequenceMatcher(None, text_n, cn).ratio() * 100))
            if score > 0:
                results.append((name, score))
        # Score absteigend sortiert, stabil
        results.sort(key=lambda t: t[1], reverse=True)
        limited = results[: max(0, int(limit or 0)) or 5]
        return [{"name": n, "score": s} for n, s in limited]

    def remove_customer(self, customer_name: str) -> Tuple[bool, str]:
        target_n = self._normalize_name(customer_name)
        if not target_n:
            return False, "Ungültiger Kundenname"
        idx_to_remove: Optional[int] = None
        for i, c in enumerate(self.customers_data):
            name = self._extract_customer_name(c)
            if self._normalize_name(name) == target_n:
                idx_to_remove = i
                break
        if idx_to_remove is None:
            return False, f"Kunde '{customer_name}' nicht gefunden"
        try:
            self.customers_data.pop(idx_to_remove)
            self._save()
            return True, f"Kunde '{customer_name}' entfernt"
        except Exception:
            return False, "Entfernen fehlgeschlagen"

    def ensure_customer_project_structure(self, customer_name: str, use_date_folder: bool = True) -> str:
        """Erstellt die Standard-Projektstruktur für den Kunden (idempotent). Rückgabe: Basispfad."""
        safe_name = customer_name.strip().replace("/", "_").replace("\\", "_") or "Unbekannt"
        base = os.path.join(self.projects_base_path, safe_name)
        try:
            os.makedirs(base, exist_ok=True)
            folder = base
            if use_date_folder:
                date_str = datetime.now().strftime("%Y-%m-%d")
                folder = os.path.join(base, date_str)
                os.makedirs(folder, exist_ok=True)
            # Standard-Struktur anlegen
            structure = [
                "01_Ausgangstext",
                "02_Angebot",
                "03_Prüfung",
                "04_Finalisierung",
            ]
            for d in structure:
                try:
                    os.makedirs(os.path.join(folder, d), exist_ok=True)
                except Exception:
                    pass
            return folder
        except Exception:
            return base

    def update_customer_activity(self, customer_name: str) -> None:
        target_n = self._normalize_name(customer_name)
        now = datetime.now().isoformat()
        try:
            for c in self.customers_data:
                if self._normalize_name(self._extract_customer_name(c)) == target_n:
                    if isinstance(c, dict):
                        c["last_activity"] = now
                        c["last_activity_type"] = "selected_from_favorites"
                    break
            self._save()
        except Exception:
            pass

    # ------------------------------- Public API: Add/Get -------------------------------
    def add_customer(self, customer_name: str):
        """
        Fügt einen neuen Kunden hinzu und liefert ein 3-Tupel zurück:
        (success: bool, message: str, similar_customers: List[Dict[str, Any]]).

        - Bei exakter Existenz: success=False, Meldung, similar_customers=[].
        - Bei ähnlichen Treffern (Score ≥ 80): success=False, Meldung, similar_customers=[...].
        - Bei Erfolg: success=True, Meldung, similar_customers=[].
        """
        try:
            name = (customer_name or "").strip()
            if not name:
                return False, "Ungültiger Kundenname", []

            # Exakt bereits vorhanden?
            target_n = self._normalize_name(name)
            for c in self.customers_data:
                if self._normalize_name(self._extract_customer_name(c)) == target_n:
                    return False, f"Kunde '{name}' existiert bereits", []

            # Ähnliche Kunden (Fuzzy) ermitteln
            sims = [s for s in (self.search_customers(name, limit=5) or []) if s.get("name")]
            similar_customers = [s for s in sims if int(s.get("score", 0)) >= 80 and self._normalize_name(s["name"]) != target_n]
            if similar_customers:
                return False, "Ähnlicher Kunde gefunden", similar_customers[:3]

            # Neuen Kunden anlegen (als Dict für Erweiterbarkeit)
            entry = {
                "name": name,
                "created_at": datetime.now().isoformat(timespec="seconds"),
                "last_activity": None,
                "last_activity_type": None,
            }
            self.customers_data.append(entry)
            self._save()
            return True, f"Kunde '{name}' hinzugefügt", []
        except Exception:
            return False, "Hinzufügen fehlgeschlagen", []

    def get_all_customers(self):
        """Gibt die Kundenliste als Liste von Dikten mit mindestens dem Key 'name' zurück."""
        try:
            result = []
            for c in self.customers_data:
                if isinstance(c, dict):
                    result.append({"name": c.get("name", "")})
                elif isinstance(c, str):
                    result.append({"name": c})
                else:
                    result.append({"name": self._extract_customer_name(c)})
            return result
        except Exception:
            return [{"name": self._extract_customer_name(c)} for c in (self.customers_data or [])]

    # ------------------------------- UI Helper Methods -------------------------------
    
    def remove_customer(self, customer_name: str):
        """
        Entfernt einen Kunden.
        Returns: (success: bool, message: str)
        """
        try:
            name = (customer_name or "").strip()
            if not name:
                return False, "Ungültiger Kundenname"
            
            target_n = self._normalize_name(name)
            original_count = len(self.customers_data)
            
            # Entferne alle Einträge mit diesem Namen
            self.customers_data = [c for c in self.customers_data 
                                 if self._normalize_name(self._extract_customer_name(c)) != target_n]
            
            if len(self.customers_data) < original_count:
                self._save()
                return True, f"Kunde '{name}' entfernt"
            else:
                return False, f"Kunde '{name}' nicht gefunden"
                
        except Exception as e:
            return False, f"Fehler beim Entfernen: {str(e)}"
    
    def get_customer_stats(self, customer_name: str = None):
        """
        Gibt Kunden-Statistiken zurück.
        Returns: Dict mit Stats
        """
        try:
            stats = {
                'total_customers': len(self.customers_data),
                'has_customers': len(self.customers_data) > 0
            }
            
            if customer_name:
                stats['current_customer'] = customer_name
                # Prüfe ob Kunde existiert
                exists, _, _ = self.customer_exists(customer_name)
                stats['customer_exists'] = exists
            else:
                stats['current_customer'] = None
                stats['customer_exists'] = False
                
            return stats
            
        except Exception:
            return {
                'total_customers': 0,
                'has_customers': False,
                'current_customer': customer_name,
                'customer_exists': False
            }
    
    def get_recent_customers(self, limit: int = 5):
        """
        Gibt die letzten Kunden zurück (basierend auf Reihenfolge).
        Returns: List[Dict] mit Kundendaten
        """
        try:
            # Nehme die letzten 'limit' Kunden
            recent = self.customers_data[-limit:] if len(self.customers_data) > limit else self.customers_data
            
            result = []
            for customer in reversed(recent):  # Neueste zuerst
                customer_name = self._extract_customer_name(customer)
                if customer_name:
                    result.append({
                        'name': customer_name,
                        'created_at': customer.get('created_at', '') if isinstance(customer, dict) else '',
                        'last_activity': customer.get('last_activity', '') if isinstance(customer, dict) else ''
                    })
            
            return result
            
        except Exception:
            return []
    
    def validate_customer_name(self, customer_name: str):
        """
        Validiert einen Kundennamen.
        Returns: (is_valid: bool, message: str)
        """
        try:
            name = (customer_name or "").strip()
            
            if not name:
                return False, "Kundenname darf nicht leer sein"
            
            if len(name) < 2:
                return False, "Kundenname muss mindestens 2 Zeichen haben"
            
            if len(name) > 100:
                return False, "Kundenname darf maximal 100 Zeichen haben"
            
            # Prüfe auf unerlaubte Zeichen (für Dateisystem-Kompatibilität)
            forbidden_chars = '<>:"/\\|?*'
            if any(char in name for char in forbidden_chars):
                return False, f"Kundenname darf keine der folgenden Zeichen enthalten: {forbidden_chars}"
            
            return True, "Kundenname ist gültig"
            
        except Exception:
            return False, "Validierung fehlgeschlagen"

    # =============================================================================
    # 🚀 PERFORMANCE BOOST - AUTO-COMPLETE & QUICK ACCESS
    # =============================================================================
    
    def search_customers_with_autocomplete(self, query: str, limit: int = 8) -> List[Dict[str, Any]]:
        """🔍 Enhanced search with auto-complete suggestions"""
        try:
            if not query or len(query.strip()) < 1:
                # Return recent customers for empty query
                return self.get_recent_customers(limit)
            
            query = query.strip().lower()
            results = []
            
            # Exact matches first (highest priority)
            for customer in self.customers_data:
                customer_name = customer.get('name', '') if isinstance(customer, dict) else str(customer)
                if customer_name.lower() == query:
                    results.append({
                        'name': customer_name,
                        'score': 100,
                        'match_type': 'exact',
                        'highlight_start': 0,
                        'highlight_end': len(customer_name)
                    })
            
            # Prefix matches (starts with)
            for customer in self.customers_data:
                customer_name = customer.get('name', '') if isinstance(customer, dict) else str(customer)
                if customer_name.lower().startswith(query) and customer_name.lower() != query:
                    score = 90 + (len(query) / len(customer_name)) * 10  # Boost longer matches
                    results.append({
                        'name': customer_name,
                        'score': int(score),
                        'match_type': 'prefix',
                        'highlight_start': 0,
                        'highlight_end': len(query)
                    })
            
            # Contains matches
            for customer in self.customers_data:
                customer_name = customer.get('name', '') if isinstance(customer, dict) else str(customer)
                if query in customer_name.lower() and not customer_name.lower().startswith(query):
                    start_pos = customer_name.lower().find(query)
                    score = 70 + (len(query) / len(customer_name)) * 20
                    results.append({
                        'name': customer_name,
                        'score': int(score),
                        'match_type': 'contains',
                        'highlight_start': start_pos,
                        'highlight_end': start_pos + len(query)
                    })
            
            # Fuzzy matches for typo tolerance
            for customer in self.customers_data:
                customer_name = customer.get('name', '') if isinstance(customer, dict) else str(customer)
                if customer_name.lower() not in [r['name'].lower() for r in results]:
                    similarity = self._calculate_similarity(query, customer_name.lower())
                    if similarity > 0.6:  # 60% similarity threshold
                        score = int(similarity * 60)  # Max 60 points for fuzzy
                        results.append({
                            'name': customer_name,
                            'score': score,
                            'match_type': 'fuzzy',
                            'highlight_start': 0,
                            'highlight_end': len(customer_name)
                        })
            
            # Sort by score (highest first) and limit results
            results.sort(key=lambda x: x['score'], reverse=True)
            return results[:limit]
            
        except Exception as e:
            print(f"⚠️ Auto-complete search error: {e}")
            return []
    
    def get_recent_customers(self, limit: int = 5) -> List[Dict[str, Any]]:
        """📋 Get recently used customers with activity info"""
        try:
            # Check if we have activity data
            recent_customers = []
            
            # First try to get from activity data if available
            try:
                import os
                projects_path = Path(self.projects_base_path)
                if projects_path.exists():
                    customer_folders = []
                    for folder in projects_path.iterdir():
                        if folder.is_dir():
                            stat = folder.stat()
                            customer_folders.append({
                                'name': folder.name,
                                'last_modified': stat.st_mtime,
                                'score': 100,
                                'match_type': 'recent'
                            })
                    
                    # Sort by last modified time (most recent first)
                    customer_folders.sort(key=lambda x: x['last_modified'], reverse=True)
                    recent_customers = customer_folders[:limit]
            except Exception:
                pass
            
            # Fallback: Return first customers from data
            if not recent_customers:
                for i, customer in enumerate(self.customers_data[:limit]):
                    customer_name = customer.get('name', '') if isinstance(customer, dict) else str(customer)
                    recent_customers.append({
                        'name': customer_name,
                        'score': 100 - i * 5,  # Slight score decrease for order
                        'match_type': 'recent'
                    })
            
            return recent_customers
            
        except Exception as e:
            print(f"⚠️ Error getting recent customers: {e}")
            return []
    
    def get_customer_quick_stats(self, customer_name: str) -> Dict[str, Any]:
        """📊 Get quick stats for customer preview"""
        try:
            stats = {
                'project_count': 0,
                'last_activity': 'Unbekannt',
                'total_files': 0,
                'folder_exists': False
            }
            
            # Check customer folder
            customer_path = Path(self.projects_base_path) / customer_name
            if customer_path.exists():
                stats['folder_exists'] = True
                
                # Count project folders (date-based folders)
                project_folders = [f for f in customer_path.iterdir() if f.is_dir()]
                stats['project_count'] = len(project_folders)
                
                # Get last activity (most recent folder)
                if project_folders:
                    most_recent = max(project_folders, key=lambda x: x.stat().st_mtime)
                    last_mod = datetime.fromtimestamp(most_recent.stat().st_mtime)
                    stats['last_activity'] = last_mod.strftime('%d.%m.%Y')
                
                # Count total files
                total_files = 0
                for project_folder in project_folders:
                    try:
                        for file_path in project_folder.rglob('*'):
                            if file_path.is_file():
                                total_files += 1
                    except Exception:
                        continue
                stats['total_files'] = total_files
            
            return stats
            
        except Exception as e:
            print(f"⚠️ Error getting customer stats: {e}")
            return {'project_count': 0, 'last_activity': 'Fehler', 'total_files': 0, 'folder_exists': False}
    
    def _calculate_similarity(self, a: str, b: str) -> float:
        """Calculate similarity between two strings using SequenceMatcher"""
        try:
            return SequenceMatcher(None, a, b).ratio()
        except Exception:
            return 0.0
