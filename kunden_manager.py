import os
import datetime
import re
from rapidfuzz import process, fuzz

class KundenManager:
    def __init__(self, base_dir="Checker_Projekte"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def _sanitize_name(self, name):
        """Bereinigt Namen von ungültigen Zeichen für Dateinamen"""
        # Ersetze ungültige Zeichen durch Unterstriche
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', name)
        # Entferne mehrfache Unterstriche
        sanitized = re.sub(r'_+', '_', sanitized)
        # Entferne führende/nachfolgende Unterstriche
        sanitized = sanitized.strip('_')
        return sanitized

    def kunden_ordner(self, kundenname):
        safe_name = self._sanitize_name(kundenname)
        return os.path.join(self.base_dir, safe_name)

    def erstelle_kundenstruktur(self, kundenname):
        safe_name = self._sanitize_name(kundenname)
        kundenpfad = self.kunden_ordner(safe_name)
        unterordner = ["Angebot", "Pruefung", "Finalisierung", "Ausgangstexte"]
        for unter in unterordner:
            os.makedirs(os.path.join(kundenpfad, unter), exist_ok=True)
        return kundenpfad

    def alle_kunden(self):
        return [d for d in os.listdir(self.base_dir) if os.path.isdir(os.path.join(self.base_dir, d))]

    def get_all_customers(self):
        """Alias für alle_kunden() für bessere Kompatibilität"""
        return self.alle_kunden()

    def find_customer_fuzzy(self, search_name, threshold=70):
        """
        Sucht nach einem Kunden mit unscharfer Suche (Fuzzy Search).
        Hilfreich für ähnliche Kundennamen oder Tippfehler.
        """
        try:
            existing_customers = self.alle_kunden()
            if not existing_customers:
                return None
            
            # Verwende rapidfuzz für intelligente Suche
            result = process.extractOne(
                search_name, 
                existing_customers, 
                scorer=fuzz.ratio, 
                score_cutoff=threshold
            )
            
            if result:
                return result[0]  # Bester Match
            return None
            
        except Exception:
            return None
    
    def customer_exists(self, kundenname):
        """
        Prüft, ob ein Kunde bereits existiert.
        Zusätzlich mit Fuzzy-Matching für ähnliche Namen.
        """
        try:
            existing_customers = self.alle_kunden()
            
            # Exakte Übereinstimmung
            if kundenname in existing_customers:
                return True, kundenname
            
            # Fuzzy-Matching für ähnliche Namen
            fuzzy_match = self.find_customer_fuzzy(kundenname)
            if fuzzy_match:
                return True, fuzzy_match
            
            return False, None
            
        except Exception:
            return False, None

    def neuer_kunde(self, kundenname):
        """Erstellt einen neuen Kunden mit der vollständigen Ordnerstruktur"""
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

    def kunden_unterordner(self, kundenname):
        safe_name = self._sanitize_name(kundenname)
        pfad = self.kunden_ordner(safe_name)
        if not os.path.exists(pfad):
            return []
        return [d for d in os.listdir(pfad) if os.path.isdir(os.path.join(pfad, d))]

    def get_ordner_fuer_workflow(self, kundenname, workflow):
        """Gibt den Pfad zum Workflow-Ordner für einen Kunden zurück."""
        safe_name = self._sanitize_name(kundenname)
        return os.path.join(self.kunden_ordner(safe_name), workflow)

    def fuzzy_kundenname_suche(self, kundenname, threshold=70):
        """Sucht den ähnlichsten Kundenordnernamen (fuzzy) und gibt ihn zurück, falls ähnlich genug.
        Threshold reduziert für bessere Matches."""
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

    def neuer_anfrage_ordner(self, kundenname, workflow, projektname=None):
        """Erzeugt einen neuen Unterordner für eine Anfrage (z.B. Angebot) nach Datum und optional Projekttitel.
        Nutzt fuzzy matching für die Kundenzuordnung."""
        # Fuzzy-Matching für Kundennamen
        existierender_kunde = self.fuzzy_kundenname_suche(kundenname)
        if existierender_kunde:
            kundenname = existierender_kunde
        else:
            # Falls kein ähnlicher Kunde gefunden, neuen Kundenordner anlegen
            kundenname = self._sanitize_name(kundenname)
            self.erstelle_kundenstruktur(kundenname)
        
        datum = datetime.date.today().isoformat()
        ordnername = datum
        if projektname:
            safe_projektname = self._sanitize_name(projektname)
            ordnername += f"_{safe_projektname.replace(' ', '_')}"
        
        pfad = os.path.join(self.get_ordner_fuer_workflow(kundenname, workflow), ordnername)
        os.makedirs(pfad, exist_ok=True)
        return pfad
    
    def speichere_datei_mit_datum(self, kundenname, workflow, datei_pfad, projekt_name=None):
        """
        Speichert eine Datei in einem datumsorganisierten Unterordner.
        Nutzt automatisches Fuzzy-Matching für Kundennamen.
        
        Args:
            kundenname: Name des Kunden (kann ungenau sein)
            workflow: Workflow-Name (Angebot, Pruefung, etc.)
            datei_pfad: Pfad zur zu speichernden Datei
            projekt_name: Optional: Projektname für Unterordner
            
        Returns:
            Dict mit Speicher-Informationen oder None bei Fehler
        """
        try:
            # Fuzzy-Matching für Kundennamen
            existierender_kunde = self.fuzzy_kundenname_suche(kundenname)
            if existierender_kunde:
                kundenname = existierender_kunde
            else:
                # Neuen Kunden anlegen
                kundenname = self._sanitize_name(kundenname)
                self.erstelle_kundenstruktur(kundenname)
            
            # Datums-Ordner erstellen
            heute = datetime.date.today().isoformat()
            
            # Zielordner bestimmen
            workflow_ordner = self.get_ordner_fuer_workflow(kundenname, workflow)
            
            ordnername = heute
            if projekt_name:
                safe_projekt = self._sanitize_name(projekt_name)
                ordnername += f"_{safe_projekt}"
            
            ziel_ordner = os.path.join(workflow_ordner, ordnername)
            os.makedirs(ziel_ordner, exist_ok=True)
            
            # Datei kopieren
            datei_name = os.path.basename(datei_pfad)
            ziel_pfad = os.path.join(ziel_ordner, datei_name)
            
            import shutil
            shutil.copy2(datei_pfad, ziel_pfad)
            
            # Relativer Pfad für Rückgabe
            relativer_pfad = os.path.relpath(ziel_pfad, self.base_dir)
            
            return {
                'original_file': datei_pfad,
                'saved_file': ziel_pfad,
                'relative_path': relativer_pfad,
                'customer': kundenname,
                'workflow': workflow,
                'date': heute,
                'project': projekt_name
            }
            
        except Exception as e:
            print(f"Fehler beim Speichern der Datei: {e}")
            return None

    def erstelle_projektstruktur(self, kundenname, projektname):
        """
        Erstellt eine Projektstruktur für einen Kunden
        
        Args:
            kundenname: Name des Kunden
            projektname: Name des Projekts
            
        Returns:
            Pfad zum erstellten Projekt-Ordner
        """
        safe_customer = self._sanitize_name(kundenname)
        safe_project = self._sanitize_name(projektname)
        
        # Stelle sicher, dass der Kunde existiert
        if not os.path.exists(self.kunden_ordner(safe_customer)):
            self.erstelle_kundenstruktur(safe_customer)
        
        # Erstelle Projekt-Ordner in allen Workflow-Ordnern
        workflows = ["Angebot", "Pruefung", "Finalisierung"]
        project_paths = []
        
        for workflow in workflows:
            workflow_path = self.get_ordner_fuer_workflow(safe_customer, workflow)
            project_path = os.path.join(workflow_path, safe_project)
            os.makedirs(project_path, exist_ok=True)
            project_paths.append(project_path)
        
        # Gib den Hauptprojekt-Pfad zurück (Pruefung als Standard)
        main_project_path = os.path.join(
            self.get_ordner_fuer_workflow(safe_customer, "Pruefung"),
            safe_project
        )
        
        return main_project_path

    def projekt_ordner(self, kundenname, projektname):
        """
        Gibt den Pfad zum Projekt-Ordner zurück (ohne ihn zu erstellen)
        
        Args:
            kundenname: Name des Kunden
            projektname: Name des Projekts
            
        Returns:
            Pfad zum Projekt-Ordner im Pruefung-Workflow
        """
        safe_customer = self._sanitize_name(kundenname)
        safe_project = self._sanitize_name(projektname)
        
        return os.path.join(
            self.get_ordner_fuer_workflow(safe_customer, "Pruefung"),
            safe_project
        )

    def get_datum_ordner(self) -> str:
        """
        Gibt den standardmäßigen Datumsordner-Namen für heute zurück.
        
        Returns:
            Ordnername im Format YYYY-MM-DD
        """
        return datetime.date.today().isoformat()
    
    def get_ordner_mit_datum(self, kundenname: str, workflow: str, projekt_name: str = None) -> str:
        """
        Erstellt oder gibt den Pfad zu einem datumsbasierten Ordner zurück.
        
        Args:
            kundenname: Name des Kunden
            workflow: Workflow-Name
            projekt_name: Optional: Projektname für Unterordner
            
        Returns:
            Vollständiger Pfad zum datumsbasierten Ordner
        """
        try:
            # Basis-Workflow-Ordner
            workflow_ordner = self.get_ordner_fuer_workflow(kundenname, workflow)
            
            # Datumsordner
            datum_ordner = self.get_datum_ordner()
            
            if projekt_name:
                safe_projekt = self._sanitize_name(projekt_name)
                ordnername = f"{datum_ordner}_{safe_projekt}"
            else:
                ordnername = datum_ordner
            
            vollständiger_pfad = os.path.join(workflow_ordner, ordnername)
            os.makedirs(vollständiger_pfad, exist_ok=True)
            
            return vollständiger_pfad
            
        except Exception as e:
            print(f"Fehler beim Erstellen des Datumsordners: {e}")
            # Fallback: Basis-Workflow-Ordner
            return self.get_ordner_fuer_workflow(kundenname, workflow)

# Beispiel-Nutzung:
# manager = KundenManager()
# manager.erstelle_kundenstruktur("Kunde_Mueller")
# print(manager.alle_kunden())
# print(manager.kunden_unterordner("Kunde_Mueller"))
# print(manager.get_ordner_fuer_workflow("Kunde_Mueller", "Angebot"))
# print(manager.neuer_anfrage_ordner("Kunde_Mueller", "Angebot", "Neues_Projekt"))
# print(manager.erstelle_projektstruktur("Kunde_Mueller", "Neues_Projekt"))
# print(manager.projekt_ordner("Kunde_Mueller", "Neues_Projekt"))
