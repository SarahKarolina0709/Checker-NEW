import os
import json
from typing import Dict, List, Optional

class ProjectDataManager:
    """
    Manager für Projektdaten mit JSON-basierter Persistierung
    """
    
    def __init__(self, base_dir: str = None):
        """
        Initialisiert den ProjectDataManager
        
        Args:
            base_dir: Basisverzeichnis für die Datenspeicherung
        """
        if base_dir:
            self.base_dir = base_dir
        else:
            self.base_dir = os.path.dirname(__file__)
        
        self.data_dir = os.path.join(self.base_dir, "project_data")
        self.data_file = os.path.join(self.data_dir, "projects.json")
        
        # Erstelle Datenverzeichnis falls es nicht existiert
        os.makedirs(self.data_dir, exist_ok=True)
    
    def load_projects(self) -> List[Dict]:
        """Lädt alle Projekte aus der JSON-Datei"""
        try:
            if not os.path.exists(self.data_file):
                return []
            
            with open(self.data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[PROJECT_DATA] Error loading projects: {e}")
            return []
    
    def save_projects(self, projects: List[Dict]):
        """Speichert alle Projekte in die JSON-Datei"""
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(projects, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[PROJECT_DATA] Error saving projects: {e}")
    
    def add_or_update_project(self, details: Dict):
        """Fügt ein neues Projekt hinzu oder aktualisiert ein bestehendes"""
        projects = self.load_projects()
        project_id = details.get("project_id")
        
        updated = False
        for idx, proj in enumerate(projects):
            if proj.get("project_id") == project_id:
                projects[idx] = details
                updated = True
                break
        
        if not updated:
            projects.append(details)
        
        self.save_projects(projects)
    
    def get_project_by_id(self, project_id: str) -> Optional[Dict]:
        """Holt ein Projekt anhand der ID"""
        projects = self.load_projects()
        for proj in projects:
            if proj.get("project_id") == project_id:
                return proj
        return None
    
    def speichere_projektdaten(self, customer_name: str, project_name: str, project_data: Dict):
        """
        Speichert Projektdaten für einen Kunden und ein Projekt
        
        Args:
            customer_name: Name des Kunden
            project_name: Name des Projekts
            project_data: Projektdaten als Dictionary
        """
        # Erstelle einzigartige Projekt-ID
        project_id = f"{customer_name}_{project_name}".replace(" ", "_").replace("/", "_")
        
        # Erweitere Projektdaten
        full_data = {
            "project_id": project_id,
            "customer_name": customer_name,
            "project_name": project_name,
            **project_data
        }
        
        self.add_or_update_project(full_data)
    
    def lade_projektdaten(self, customer_name: str, project_name: str) -> Optional[Dict]:
        """
        Lädt Projektdaten für einen Kunden und ein Projekt
        
        Args:
            customer_name: Name des Kunden
            project_name: Name des Projekts
            
        Returns:
            Projektdaten als Dictionary oder None
        """
        project_id = f"{customer_name}_{project_name}".replace(" ", "_").replace("/", "_")
        return self.get_project_by_id(project_id)
    
    def loesche_projektdaten(self, customer_name: str, project_name: str):
        """
        Löscht Projektdaten für einen Kunden und ein Projekt
        
        Args:
            customer_name: Name des Kunden
            project_name: Name des Projekts
        """
        project_id = f"{customer_name}_{project_name}".replace(" ", "_").replace("/", "_")
        projects = self.load_projects()
        
        projects = [proj for proj in projects if proj.get("project_id") != project_id]
        self.save_projects(projects)
    
    def alle_projekte_fuer_kunde(self, customer_name: str) -> List[Dict]:
        """
        Gibt alle Projekte für einen bestimmten Kunden zurück
        
        Args:
            customer_name: Name des Kunden
            
        Returns:
            Liste aller Projekte für diesen Kunden
        """
        projects = self.load_projects()
        return [proj for proj in projects if proj.get("customer_name") == customer_name]


# Legacy-Funktionen für Rückwärtskompatibilität
DATA_FILE = os.path.join(os.path.dirname(__file__), "project_data", "projects.json")

def load_projects():
    """Legacy-Funktion - verwende ProjectDataManager stattdessen"""
    manager = ProjectDataManager()
    return manager.load_projects()

def add_or_update_project(details):
    """Legacy-Funktion - verwende ProjectDataManager stattdessen"""
    manager = ProjectDataManager()
    manager.add_or_update_project(details)

def get_project_by_id(project_id):
    """Legacy-Funktion - verwende ProjectDataManager stattdessen"""
    manager = ProjectDataManager()
    return manager.get_project_by_id(project_id)

