import os
import datetime
import re
import json
import shutil
from rapidfuzz import process, fuzz
from typing import List, Dict, Optional, Tuple

class KundenManager:
    """
    Verbesserte Version des KundenManagers mit projekt-zentrierter Struktur.
    
    Neue Struktur:
    Kunde_Mueller/
    ├── 2025-07-06_Projekt_A/
    │   ├── Ausgangstexte/
    │   ├── Angebot/
    │   ├── Pruefung/
    │   └── Finalisierung/
    └── 2025-07-08_Projekt_B/
        ├── Ausgangstexte/
        ├── Angebot/
        ├── Pruefung/
        └── Finalisierung/
    """
    
    def __init__(self, base_dir="Checker_Projekte"):
        self.base_dir = base_dir
        self.workflows = ["Ausgangstexte", "Angebot", "Pruefung", "Finalisierung"]
        os.makedirs(self.base_dir, exist_ok=True)

    def _sanitize_name(self, name):
        """Bereinigt Namen von ungültigen Zeichen für Dateinamen"""
        if not name:
            return "Unbenannt"
        # Ersetze ungültige Zeichen durch Unterstriche
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', name)
        # Entferne mehrfache Unterstriche
        sanitized = re.sub(r'_+', '_', sanitized)
        # Entferne führende/nachfolgende Unterstriche
        sanitized = sanitized.strip('_')
        return sanitized

    def _generate_project_id(self, projektname=None, datum=None):
        """Generiert eine eindeutige Projekt-ID basierend auf Datum und Projektname"""
        if datum is None:
            datum = datetime.date.today().isoformat()
        
        project_id = datum
        if projektname:
            safe_projektname = self._sanitize_name(projektname)
            project_id += f"_{safe_projektname.replace(' ', '_')}"
        
        return project_id

    def kunden_ordner(self, kundenname):
        """Gibt den Pfad zum Kundenordner zurück"""
        safe_name = self._sanitize_name(kundenname)
        return os.path.join(self.base_dir, safe_name)

    def erstelle_kundenstruktur(self, kundenname):
        """Erstellt die Basis-Kundenstruktur (nur der Hauptordner)"""
        safe_name = self._sanitize_name(kundenname)
        kundenpfad = self.kunden_ordner(safe_name)
        os.makedirs(kundenpfad, exist_ok=True)
        return kundenpfad

    def erstelle_projekt_ordner(self, kundenname, projektname=None, datum=None):
        """
        Erstellt einen neuen Projekt-Ordner für einen Kunden mit vollständiger Workflow-Struktur
        
        Args:
            kundenname: Name des Kunden
            projektname: Name des Projekts (optional)
            datum: Datum für das Projekt (optional, Standard: heute)
            
        Returns:
            Tuple: (projekt_pfad, projekt_id) - Pfad zum erstellten Projekt-Ordner und Projekt-ID
        """
        # Stelle sicher, dass der Kunde existiert
        self.erstelle_kundenstruktur(kundenname)
        
        # Generiere Projekt-ID
        project_id = self._generate_project_id(projektname, datum)
        
        # Erstelle Projekt-Ordner
        safe_customer = self._sanitize_name(kundenname)
        projekt_pfad = os.path.join(self.kunden_ordner(safe_customer), project_id)
        
        # Erstelle Workflow-Unterordner
        for workflow in self.workflows:
            workflow_pfad = os.path.join(projekt_pfad, workflow)
            os.makedirs(workflow_pfad, exist_ok=True)
        
        return projekt_pfad, project_id

    def get_projekt_pfad(self, kundenname, projekt_id):
        """Gibt den Pfad zu einem spezifischen Projekt zurück"""
        safe_customer = self._sanitize_name(kundenname)
        return os.path.join(self.kunden_ordner(safe_customer), projekt_id)

    def get_projekt_workflow_ordner(self, kundenname, projekt_id, workflow):
        """Gibt den Pfad zu einem Workflow-Ordner innerhalb eines Projekts zurück"""
        projekt_pfad = self.get_projekt_pfad(kundenname, projekt_id)
        return os.path.join(projekt_pfad, workflow)

    def liste_kundenprojekte(self, kundenname):
        """Listet alle Projekte eines Kunden auf"""
        safe_customer = self._sanitize_name(kundenname)
        kunden_pfad = self.kunden_ordner(safe_customer)
        
        if not os.path.exists(kunden_pfad):
            return []
        
        projekte = []
        for item in os.listdir(kunden_pfad):
            item_path = os.path.join(kunden_pfad, item)
            if os.path.isdir(item_path):
                projekte.append(item)
        
        # Sortiere nach Datum (neueste zuerst)
        projekte.sort(reverse=True)
        return projekte

    def get_neuestes_projekt(self, kundenname):
        """Gibt das neueste Projekt eines Kunden zurück"""
        projekte = self.liste_kundenprojekte(kundenname)
        return projekte[0] if projekte else None

    def alle_kunden(self):
        """Gibt alle Kunden zurück"""
        return [d for d in os.listdir(self.base_dir) if os.path.isdir(os.path.join(self.base_dir, d))]

    def fuzzy_kundenname_suche(self, kundenname, threshold=70):
        """Sucht den ähnlichsten Kundenordnernamen (fuzzy) und gibt ihn zurück"""
        kunden_liste = self.alle_kunden()
        if not kunden_liste:
            return None
        
        # Bereite den Suchbegriff vor (normalisiert)
        search_normalized = kundenname.lower().replace(' ', '_').replace('-', '_')
        
        # Bereite die Kundenliste vor (normalisiert für Vergleich)
        kunden_normalized = [k.lower().replace(' ', '_').replace('-', '_') for k in kunden_liste]
        
        # Fuzzy-Matching
        match, score, idx = process.extractOne(search_normalized, kunden_normalized, scorer=fuzz.WRatio)
        
        if score >= threshold:
            return kunden_liste[idx]  # Gib den ursprünglichen Kundennamen zurück
        return None

    def find_customer_fuzzy(self, search_name, threshold=70):
        """Alias für fuzzy_kundenname_suche für Rückwärtskompatibilität"""
        return self.fuzzy_kundenname_suche(search_name, threshold)

    def customer_exists(self, kundenname):
        """
        Prüft, ob ein Kunde bereits existiert (mit verbessertem Fuzzy Matching)
        
        Returns:
            tuple: (exists: bool, matched_customer: str or None, similarity_score: float)
        """
        try:
            existing_customers = self.alle_kunden()
            
            if not existing_customers:
                return False, None, 0.0
            
            # Normalisiere den Suchbegriff
            search_normalized = kundenname.lower().strip()
            
            # 1. Prüfe auf exakte Übereinstimmung (case-insensitive)
            for customer in existing_customers:
                if customer.lower() == search_normalized:
                    return True, customer, 100.0
            
            # 2. Prüfe auf exakte Übereinstimmung nach Normalisierung
            search_clean = re.sub(r'[^\w\s]', '', search_normalized).replace(' ', '_')
            for customer in existing_customers:
                customer_clean = re.sub(r'[^\w\s]', '', customer.lower()).replace(' ', '_')
                if customer_clean == search_clean:
                    return True, customer, 95.0
            
            # 3. Fuzzy-Matching für ähnliche Namen
            fuzzy_match = self.find_customer_fuzzy(kundenname, threshold=70)
            if fuzzy_match:
                # Berechne Similarity Score
                search_for_score = kundenname.lower().replace(' ', '_').replace('-', '_')
                match_for_score = fuzzy_match.lower().replace(' ', '_').replace('-', '_')
                
                # Verwende rapidfuzz für genauen Score
                from rapidfuzz import fuzz
                score = fuzz.WRatio(search_for_score, match_for_score)
                
                return True, fuzzy_match, score
            
            return False, None, 0.0
            
        except Exception as e:
            self.logger.error(f"Error in customer_exists: {e}") if hasattr(self, 'logger') else None
            return False, None, 0.0

    def neuer_kunde(self, kundenname):
        """Erstellt einen neuen Kunden"""
        try:
            # Prüfe ob Kunde bereits existiert
            if kundenname in self.alle_kunden():
                return False  # Kunde existiert bereits
            
            # Erstelle die Kundenstruktur
            kundenpfad = self.erstelle_kundenstruktur(kundenname)
            
            # Prüfe ob die Erstellung erfolgreich war
            return os.path.exists(kundenpfad)
            
        except Exception:
            return False

    # Rückwärtskompatibilität: Methoden für alte Struktur
    def neuer_anfrage_ordner(self, kundenname, workflow, projektname=None):
        """
        Erstellt einen neuen Anfrage-Ordner in der neuen Struktur
        (Rückwärtskompatibilität für alte API)
        """
        # Erstelle ein neues Projekt
        result = self.erstelle_projekt_ordner(kundenname, projektname)
        
        if result:
            projekt_pfad, projekt_id = result
            # Gib den Workflow-Ordner zurück
            return self.get_projekt_workflow_ordner(kundenname, projekt_id, workflow)
        return None

    def get_ordner_fuer_workflow(self, kundenname, workflow):
        """
        Rückwärtskompatibilität: Gibt den Workflow-Ordner für das neueste Projekt zurück
        """
        neuestes_projekt = self.get_neuestes_projekt(kundenname)
        if not neuestes_projekt:
            # Erstelle ein neues Projekt
            projekt_pfad = self.erstelle_projekt_ordner(kundenname)
            neuestes_projekt = os.path.basename(projekt_pfad)
        
        return self.get_projekt_workflow_ordner(kundenname, neuestes_projekt, workflow)

    def migrate_from_old_structure(self, kundenname):
        """
        Migriert einen Kunden von der alten zur neuen Struktur
        """
        safe_customer = self._sanitize_name(kundenname)
        kunden_pfad = self.kunden_ordner(safe_customer)
        
        if not os.path.exists(kunden_pfad):
            return False
        
        # Prüfe ob bereits neue Struktur
        items = os.listdir(kunden_pfad)
        old_workflows = ["Angebot", "Pruefung", "Finalisierung", "Ausgangstexte"]
        
        # Wenn alte Workflow-Ordner direkt im Kundenordner existieren
        if any(item in old_workflows for item in items):
            # Erstelle ein Standard-Projekt für Migration
            migration_project = self.erstelle_projekt_ordner(
                kundenname, 
                "Migration_Projekt",
                datetime.date.today().isoformat()
            )
            
            # Verschiebe alte Ordner in das neue Projekt
            import shutil
            for workflow in old_workflows:
                old_path = os.path.join(kunden_pfad, workflow)
                if os.path.exists(old_path):
                    new_path = os.path.join(migration_project, workflow)
                    if os.path.exists(new_path):
                        shutil.rmtree(new_path)  # Entferne leeren neuen Ordner
                    shutil.move(old_path, new_path)
            
            return True
        
        return False

# Beispiel-Nutzung:
if __name__ == "__main__":
    manager = KundenManager()
    
    # Neues Projekt erstellen
    projekt_pfad, projekt_id = manager.erstelle_projekt_ordner("Kunde_Mueller", "Website_Übersetzung")
    print(f"Projekt erstellt: {projekt_pfad}")
    
    # Projekte auflisten
    projekte = manager.liste_kundenprojekte("Kunde_Mueller")
    print(f"Projekte: {projekte}")
    
    # Workflow-Ordner für Upload
    upload_ordner = manager.get_projekt_workflow_ordner("Kunde_Mueller", projekte[0], "Ausgangstexte")
    print(f"Upload-Ordner: {upload_ordner}")
