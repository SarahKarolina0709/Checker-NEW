# -*- coding: utf-8 -*-
"""
🎯 Kunden-Utilities für CheckerApp
===================================

Zentrale Sammlung aller Hilfsfunktionen für Kundenmanagement:
- Fuzzy-Matching für Kundennamen
- Kürzel-Generierung und -Verwaltung
- Kundenname-Normalisierung
- Display-Name Formatierung
- Ordnername-Parsing
- Kundendaten-Validierung

Autor: CheckerApp Team
Datum: Juli 2025
"""

import os
import re
import json
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime
from rapidfuzz import process, fuzz


class KundenUtils:
    """
    🏢 Zentrale Utilities für Kundenmanagement
    
    Diese Klasse bietet alle notwendigen Hilfsfunktionen für das
    Kundenmanagement, von der Namens-Normalisierung bis hin zum
    intelligenten Fuzzy-Matching.
    """
    
    def __init__(self):
        """Initialisiert KundenUtils mit Standard-Konfiguration"""
        self.fuzzy_threshold = 70  # Mindest-Ähnlichkeit für Fuzzy-Match
        self.max_code_length = 5   # Maximale Länge für Kundenkürzel
        
    # =============================================================================
    # 🔤 NAMEN-NORMALISIERUNG & VALIDIERUNG
    # =============================================================================
    
    def sanitize_customer_name(self, name: str) -> str:
        """
        Bereinigt Kundennamen von ungültigen Zeichen für Dateinamen
        
        Args:
            name: Roher Kundenname
            
        Returns:
            Bereinigter Name für Dateisystem
        """
        if not name or not isinstance(name, str):
            return "UNBEKANNT"
            
        # Entferne gefährliche Zeichen
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', name.strip())
        
        # Entferne mehrfache Unterstriche
        sanitized = re.sub(r'_+', '_', sanitized)
        
        # Entferne führende/nachfolgende Unterstriche
        sanitized = sanitized.strip('_')
        
        # Fallback wenn alles entfernt wurde
        if not sanitized:
            sanitized = "KUNDE"
            
        return sanitized
    
    def normalize_customer_name(self, name: str) -> str:
        """
        Normalisiert Kundennamen für Vergleiche (lowercase, keine Sonderzeichen)
        
        Args:
            name: Kundenname
            
        Returns:
            Normalisierter Name für Vergleiche
        """
        if not name:
            return ""
            
        # Zu lowercase und Sonderzeichen entfernen
        normalized = name.lower()
        normalized = re.sub(r'[^a-z0-9äöüß\s]', '', normalized)
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    def validate_customer_name(self, name: str) -> Tuple[bool, str]:
        """
        Validiert einen Kundennamen
        
        Args:
            name: Zu validierender Name
            
        Returns:
            Tuple: (ist_gültig, fehlermeldung)
        """
        if not name or not isinstance(name, str):
            return False, "Name darf nicht leer sein"
            
        name = name.strip()
        
        if len(name) < 2:
            return False, "Name muss mindestens 2 Zeichen lang sein"
            
        if len(name) > 100:
            return False, "Name darf maximal 100 Zeichen lang sein"
            
        # Prüfe auf gefährliche Zeichen
        dangerous_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        if any(char in name for char in dangerous_chars):
            return False, f"Name darf keine gefährlichen Zeichen enthalten: {', '.join(dangerous_chars)}"
            
        return True, ""
    
    # =============================================================================
    # 🏷️ KÜRZEL-GENERIERUNG & VERWALTUNG
    # =============================================================================
    
    def generate_customer_code(self, name: str, existing_codes: List[str] = None) -> str:
        """
        Generiert ein eindeutiges Kürzel für einen Kunden
        
        Args:
            name: Kundenname
            existing_codes: Liste bereits verwendeter Kürzel
            
        Returns:
            Eindeutiges Kundenkürzel
        """
        if existing_codes is None:
            existing_codes = []
            
        if not name:
            name = "KUNDE"
            
        # Basis-Kürzel generieren
        base_code = self._generate_base_code(name)
        
        # Prüfe Eindeutigkeit
        if base_code not in existing_codes:
            return base_code
            
        # Generiere Varianten wenn Duplikat
        return self._generate_unique_code(base_code, existing_codes)
    
    def _generate_base_code(self, name: str) -> str:
        """
        Generiert Basis-Kürzel aus Kundenname
        
        Strategien:
        1. Erste Buchstaben der Wörter (max 5)
        2. Erste 3-5 Buchstaben des ersten Worts
        3. Fallback: "KUNDE"
        """
        name = name.strip().upper()
        
        # Strategie 1: Erste Buchstaben der Wörter
        words = re.findall(r'\b[A-ZÄÖÜ]', name)
        if len(words) >= 2:
            code = ''.join(words[:self.max_code_length])
            if len(code) >= 3:
                return code
                
        # Strategie 2: Erste Buchstaben des ersten Worts
        first_word = re.findall(r'\b[A-ZÄÖÜ][A-ZÄÖÜ0-9]*', name)
        if first_word:
            word = first_word[0]
            if len(word) >= 3:
                return word[:self.max_code_length]
                
        # Strategie 3: Zahlen und Buchstaben kombinieren
        alphanumeric = re.findall(r'[A-ZÄÖÜ0-9]', name)
        if len(alphanumeric) >= 3:
            return ''.join(alphanumeric[:self.max_code_length])
            
        # Fallback
        return "KUNDE"
    
    def _generate_unique_code(self, base_code: str, existing_codes: List[str]) -> str:
        """Generiert eindeutiges Kürzel durch Anhängen von Zahlen"""
        for i in range(1, 100):
            candidate = f"{base_code[:3]}{i:02d}"
            if candidate not in existing_codes:
                return candidate
                
        # Notfall-Fallback
        return f"KU{datetime.now().strftime('%m%d')}"
    
    # =============================================================================
    # 🔍 FUZZY-MATCHING & SUCHE
    # =============================================================================
    
    def find_similar_customer(self, search_name: str, customer_list: List[str], 
                            threshold: int = None) -> Optional[Tuple[str, int]]:
        """
        Sucht ähnlichen Kunden mit Fuzzy-Matching
        
        Args:
            search_name: Suchbegriff
            customer_list: Liste aller Kundennamen
            threshold: Mindest-Ähnlichkeit (Standard: self.fuzzy_threshold)
            
        Returns:
            Tuple: (gefundener_name, ähnlichkeit) oder None
        """
        if threshold is None:
            threshold = self.fuzzy_threshold
            
        if not search_name or not customer_list:
            return None
            
        # Normalisiere Suchbegriff
        search_normalized = self.normalize_customer_name(search_name)
        
        # Normalisiere Kundenliste
        normalized_customers = [
            self.normalize_customer_name(customer) 
            for customer in customer_list
        ]
        
        # Führe Fuzzy-Search durch
        try:
            result = process.extractOne(
                search_normalized, 
                normalized_customers,
                scorer=fuzz.WRatio
            )
            
            if result and result[1] >= threshold:
                # Finde Original-Namen
                index = normalized_customers.index(result[0])
                return customer_list[index], result[1]
                
        except Exception as e:
            print(f"Fehler beim Fuzzy-Matching: {e}")
            
        return None
    
    def find_all_similar_customers(self, search_name: str, customer_list: List[str],
                                 threshold: int = None, limit: int = 5) -> List[Tuple[str, int]]:
        """
        Findet alle ähnlichen Kunden sortiert nach Ähnlichkeit
        
        Args:
            search_name: Suchbegriff
            customer_list: Liste aller Kundennamen
            threshold: Mindest-Ähnlichkeit
            limit: Maximale Anzahl Ergebnisse
            
        Returns:
            Liste von (kundenname, ähnlichkeit) Tupeln
        """
        if threshold is None:
            threshold = self.fuzzy_threshold
            
        if not search_name or not customer_list:
            return []
            
        search_normalized = self.normalize_customer_name(search_name)
        results = []
        
        for customer in customer_list:
            normalized_customer = self.normalize_customer_name(customer)
            
            try:
                similarity = fuzz.WRatio(search_normalized, normalized_customer)
                if similarity >= threshold:
                    results.append((customer, similarity))
            except Exception:
                continue
                
        # Sortiere nach Ähnlichkeit (absteigend)
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results[:limit]
    
    # =============================================================================
    # 📁 ORDNERNAME-PARSING & FORMATIERUNG
    # =============================================================================
    
    def extract_date_from_folder(self, folder_name: str) -> Optional[str]:
        """
        Extrahiert Datum aus Ordnername (YYYY-MM-DD oder YYYY-MM-DD_HHMM)
        
        Args:
            folder_name: Name des Ordners
            
        Returns:
            Datum im Format YYYY-MM-DD oder None
        """
        if not folder_name:
            return None
            
        try:
            # Behandle verschiedene Formate
            patterns = [
                r'^(\d{4}-\d{2}-\d{2})(?:_\d{4})?',  # YYYY-MM-DD_HHMM
                r'^(\d{4}-\d{2}-\d{2})(?:_\w+)?',    # YYYY-MM-DD_Text
                r'^(\d{4}-\d{2}-\d{2})$'             # YYYY-MM-DD
            ]
            
            for pattern in patterns:
                match = re.match(pattern, folder_name)
                if match:
                    date_str = match.group(1)
                    # Validiere Datum
                    datetime.strptime(date_str, '%Y-%m-%d')
                    return date_str
                    
        except (ValueError, AttributeError):
            pass
            
        return None
    
    def format_project_display_name(self, folder_name: str) -> str:
        """
        Formatiert Projekt-Anzeigename aus Ordnername
        
        Args:
            folder_name: Ordnername
            
        Returns:
            Formatierter Anzeigename
        """
        if not folder_name:
            return "Unbekanntes Projekt"
            
        try:
            # Entferne Datum-Prefix
            if '_' in folder_name:
                parts = folder_name.split('_', 1)
                if len(parts) > 1 and self.extract_date_from_folder(folder_name):
                    remaining = parts[1]
                    
                    # Prüfe ob es eine Zeit ist (HHMM)
                    if remaining.isdigit() and len(remaining) == 4:
                        return f"Upload {remaining[:2]}:{remaining[2:]}"
                    else:
                        # Formatiere Projektname
                        return remaining.replace('_', ' ').title()
            
            # Fallback: verwende ganzen Namen (formatiert)
            return folder_name.replace('_', ' ').title()
            
        except Exception:
            return folder_name
    
    def parse_project_folder_name(self, folder_name: str) -> Dict[str, Optional[str]]:
        """
        Parst Projekt-Ordnername vollständig
        
        Args:
            folder_name: Ordnername
            
        Returns:
            Dict mit parsed Komponenten: date, time, project_name, display_name
        """
        result = {
            'date': None,
            'time': None,
            'project_name': None,
            'display_name': None,
            'original_name': folder_name
        }
        
        if not folder_name:
            return result
            
        # Extrahiere Datum
        result['date'] = self.extract_date_from_folder(folder_name)
        
        # Parse weitere Komponenten
        if '_' in folder_name:
            parts = folder_name.split('_')
            if len(parts) >= 2 and result['date']:
                second_part = parts[1]
                
                # Prüfe ob zweiter Teil Zeit ist
                if second_part.isdigit() and len(second_part) == 4:
                    result['time'] = f"{second_part[:2]}:{second_part[2:]}"
                    
                    # Projekt-Name aus weiteren Teilen
                    if len(parts) > 2:
                        result['project_name'] = '_'.join(parts[2:])
                else:
                    # Ganzer Rest ist Projekt-Name
                    result['project_name'] = '_'.join(parts[1:])
        
        # Generiere Display-Name
        result['display_name'] = self.format_project_display_name(folder_name)
        
        return result
    
    # =============================================================================
    # 📊 KUNDENDATEN-UTILITIES
    # =============================================================================
    
    def load_customers_from_json(self, file_path: str) -> Dict[str, Dict]:
        """
        Lädt Kundendaten aus JSON-Datei
        
        Args:
            file_path: Pfad zur customers.json
            
        Returns:
            Dict mit Kundendaten
        """
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Fehler beim Laden von {file_path}: {e}")
            
        return {}
    
    def save_customers_to_json(self, customers_data: Dict, file_path: str) -> bool:
        """
        Speichert Kundendaten in JSON-Datei
        
        Args:
            customers_data: Kundendaten
            file_path: Ziel-Pfad
            
        Returns:
            True bei Erfolg
        """
        try:
            # Backup erstellen falls Datei existiert
            if os.path.exists(file_path):
                backup_path = f"{file_path}.backup"
                os.rename(file_path, backup_path)
                
            # Neue Datei schreiben
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(customers_data, f, ensure_ascii=False, indent=2)
                
            return True
            
        except Exception as e:
            print(f"Fehler beim Speichern von {file_path}: {e}")
            return False
    
    def get_customer_display_name(self, customer_code: str, customers_data: Dict) -> str:
        """
        Holt Anzeigename für Kunde aus Kundendaten
        
        Args:
            customer_code: Kundenkürzel oder -code
            customers_data: Geladene Kundendaten
            
        Returns:
            Anzeigename oder Code als Fallback
        """
        if not customer_code:
            return "Unbekannter Kunde"
            
        try:
            # Suche in verschiedenen Feldern
            for customer_data in customers_data.values():
                if isinstance(customer_data, dict):
                    # Direkte Matches
                    if (customer_data.get('code') == customer_code or 
                        customer_data.get('name') == customer_code or
                        customer_data.get('id') == customer_code):
                        return customer_data.get('name', customer_code)
                        
            # Fallback: Fuzzy-Search
            all_codes = []
            all_names = []
            
            for customer_data in customers_data.values():
                if isinstance(customer_data, dict):
                    if customer_data.get('code'):
                        all_codes.append(customer_data['code'])
                    if customer_data.get('name'):
                        all_names.append(customer_data['name'])
            
            # Suche in Codes
            fuzzy_result = self.find_similar_customer(customer_code, all_codes, threshold=80)
            if fuzzy_result:
                # Finde zugehörigen Namen
                for customer_data in customers_data.values():
                    if customer_data.get('code') == fuzzy_result[0]:
                        return customer_data.get('name', customer_code)
                        
        except Exception as e:
            print(f"Fehler beim Abrufen des Display-Names: {e}")
            
        return customer_code
    
    def extract_customer_codes(self, customers_data: Dict) -> List[str]:
        """
        Extrahiert alle Kundenkürzel aus Kundendaten
        
        Args:
            customers_data: Kundendaten
            
        Returns:
            Liste aller Kürzel
        """
        codes = []
        
        try:
            for customer_data in customers_data.values():
                if isinstance(customer_data, dict):
                    code = customer_data.get('code')
                    if code and code not in codes:
                        codes.append(code)
        except Exception:
            pass
            
        return codes
    
    # =============================================================================
    # 🔧 UTILITY-FUNKTIONEN
    # =============================================================================
    
    def suggest_customer_name_corrections(self, name: str) -> List[str]:
        """
        Schlägt Korrekturen für einen Kundennamen vor
        
        Args:
            name: Ursprünglicher Name
            
        Returns:
            Liste mit Korrektur-Vorschlägen
        """
        suggestions = []
        
        if not name:
            return suggestions
            
        # Entferne doppelte Leerzeichen
        corrected = re.sub(r'\s+', ' ', name.strip())
        if corrected != name:
            suggestions.append(corrected)
            
        # Korrigiere Groß-/Kleinschreibung
        title_case = corrected.title()
        if title_case != corrected:
            suggestions.append(title_case)
            
        # Entferne Sonderzeichen
        clean = re.sub(r'[^\w\s-]', '', corrected)
        if clean and clean != corrected:
            suggestions.append(clean)
            
        return list(set(suggestions))  # Entferne Duplikate
    
    def is_valid_customer_code(self, code: str) -> bool:
        """
        Prüft ob ein Kundenkürzel gültig ist
        
        Args:
            code: Zu prüfendes Kürzel
            
        Returns:
            True wenn gültig
        """
        if not code or not isinstance(code, str):
            return False
            
        code = code.strip().upper()
        
        # Länge prüfen
        if len(code) < 2 or len(code) > self.max_code_length:
            return False
            
        # Nur Buchstaben und Zahlen
        if not re.match(r'^[A-Z0-9]+$', code):
            return False
            
        return True


# =============================================================================
# 🏭 FACTORY & CONVENIENCE FUNCTIONS
# =============================================================================

# Globale Instanz für einfache Nutzung
_kunden_utils_instance = None

def get_kunden_utils() -> KundenUtils:
    """Holt globale KundenUtils-Instanz (Singleton Pattern)"""
    global _kunden_utils_instance
    if _kunden_utils_instance is None:
        _kunden_utils_instance = KundenUtils()
    return _kunden_utils_instance

# Convenience Functions für häufige Aufgaben
def sanitize_name(name: str) -> str:
    """Schneller Zugriff auf Name-Sanitization"""
    return get_kunden_utils().sanitize_customer_name(name)

def generate_code(name: str, existing_codes: List[str] = None) -> str:
    """Schneller Zugriff auf Code-Generierung"""
    return get_kunden_utils().generate_customer_code(name, existing_codes)

def find_similar(search_name: str, customer_list: List[str], threshold: int = 70) -> Optional[Tuple[str, int]]:
    """Schneller Zugriff auf Fuzzy-Matching"""
    return get_kunden_utils().find_similar_customer(search_name, customer_list, threshold)

def extract_date(folder_name: str) -> Optional[str]:
    """Schneller Zugriff auf Datum-Extraktion"""
    return get_kunden_utils().extract_date_from_folder(folder_name)

def format_display_name(folder_name: str) -> str:
    """Schneller Zugriff auf Display-Name Formatierung"""
    return get_kunden_utils().format_project_display_name(folder_name)


# =============================================================================
# 📝 BEISPIEL-VERWENDUNG
# =============================================================================

if __name__ == "__main__":
    # Demo der KundenUtils
    utils = KundenUtils()
    
    print("🎯 KundenUtils Demo")
    print("=" * 50)
    
    # Test Name-Sanitization
    test_names = ["Müller & Co. GmbH", "Schmidt/Weber AG", "Test<>Company"]
    print("\n📝 Name-Sanitization:")
    for name in test_names:
        sanitized = utils.sanitize_customer_name(name)
        print(f"  '{name}' → '{sanitized}'")
    
    # Test Code-Generierung
    print("\n🏷️ Code-Generierung:")
    for name in test_names:
        code = utils.generate_customer_code(name)
        print(f"  '{name}' → '{code}'")
    
    # Test Fuzzy-Matching
    customer_list = ["Müller GmbH", "Schmidt AG", "Weber & Co", "Test Company"]
    search_terms = ["Mueller", "Shmidt", "Webber"]
    
    print("\n🔍 Fuzzy-Matching:")
    for term in search_terms:
        result = utils.find_similar_customer(term, customer_list)
        if result:
            print(f"  '{term}' → '{result[0]}' ({result[1]}% Ähnlichkeit)")
        else:
            print(f"  '{term}' → Keine Übereinstimmung")
    
    print("\n✅ Demo abgeschlossen!")
