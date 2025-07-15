"""
Vereinfachter Upload-Manager für die Checker-App
================================================

Direkte Integration mit customer_management_utils.
"""

import os
import shutil
from datetime import datetime
from typing import List, Optional, Any
from tkinter import filedialog, messagebox


class UploadManager:
    """
    Vereinfachter Upload-Manager für direkte Integration.
    """
    
    def __init__(self, app_instance=None, kunden_manager=None):
        """
        Initialisiert den Upload-Manager.
        
        Args:
            app_instance: Referenz zur Hauptanwendung (optional)
            kunden_manager: Instanz des KundenManagers (optional)
        """
        self.app = app_instance
        self.kunden_manager = kunden_manager
        self.logger = getattr(app_instance, 'logger', None) if app_instance else None
        
        # Upload-Daten
        self.uploaded_files: List[str] = []
        self.current_customer: Optional[str] = None
        
        self._log_info("Upload-Manager initialisiert (vereinfacht)")
    
    def _log_info(self, message: str):
        """Hilfsmethode für Logging."""
        if self.logger:
            self.logger.info(message)
        else:
            print(f"[UPLOAD] {message}")
    
    def _log_error(self, message: str, error: Exception = None):
        """Hilfsmethode für Error-Logging."""
        if self.logger:
            if error:
                self.logger.error(f"{message}: {error}")
            else:
                self.logger.error(message)
        else:
            print(f"[UPLOAD ERROR] {message}")
    
    def select_files(self) -> List[str]:
        """
        Öffnet Dateiauswahl-Dialog und gibt ausgewählte Dateien zurück.
        
        Returns:
            Liste der ausgewählten Dateipfade
        """
        try:
            files = filedialog.askopenfilenames(
                title="Dateien für Upload auswählen",
                filetypes=[
                    ("Alle Dateien", "*.*"),
                    ("PDF Dateien", "*.pdf"),
                    ("Word Dokumente", "*.docx;*.doc"),
                    ("Text Dateien", "*.txt"),
                    ("Excel Dateien", "*.xlsx;*.xls"),
                    ("PowerPoint", "*.pptx;*.ppt")
                ]
            )
            
            if files:
                # Füge neue Dateien hinzu (vermeide Duplikate)
                new_files = [f for f in files if f not in self.uploaded_files]
                self.uploaded_files.extend(new_files)
                
                self._log_info(f"{len(new_files)} neue Datei(en) zur Upload-Liste hinzugefügt")
                return list(files)
            
            return []
            
        except Exception as e:
            self._log_error("Fehler bei Dateiauswahl", e)
            return []
    
    def upload_files_to_customer(self, customer_id: str, files: List[str], 
                                customer_manager, workflow: str = "Ausgangstexte") -> dict:
        """
        Lädt Dateien zu einem Kunden hoch.
        
        Args:
            customer_id: ID des Kunden
            files: Liste der Dateipfade
            customer_manager: CustomerManager Instanz
            workflow: Workflow-Ordner (default: "Ausgangstexte")
            
        Returns:
            Dictionary mit Upload-Ergebnis
        """
        try:
            # Upload-Ordner erstellen
            upload_folder_result = customer_manager.create_upload_folder(customer_id, files)
            
            # Je nach Rückgabetyp behandeln
            if isinstance(upload_folder_result, tuple):
                upload_folder, is_new = upload_folder_result
            else:
                upload_folder = upload_folder_result
                is_new = True
            
            # Workflow-Unterordner für Upload
            workflow_folder = os.path.join(upload_folder, workflow)
            os.makedirs(workflow_folder, exist_ok=True)
            
            # Dateien kopieren
            copied_files = []
            failed_files = []
            
            for file_path in files:
                try:
                    filename = os.path.basename(file_path)
                    dest_path = os.path.join(workflow_folder, filename)
                    
                    # Bei doppelten Dateinamen nummerieren
                    counter = 1
                    base_name, ext = os.path.splitext(filename)
                    while os.path.exists(dest_path):
                        new_name = f"{base_name}_{counter}{ext}"
                        dest_path = os.path.join(workflow_folder, new_name)
                        counter += 1
                    
                    shutil.copy2(file_path, dest_path)
                    copied_files.append(dest_path)
                    self._log_info(f"Datei kopiert: {filename} -> {dest_path}")
                    
                except Exception as e:
                    failed_files.append({"file": file_path, "error": str(e)})
                    self._log_error(f"Fehler beim Kopieren von {file_path}", e)
            
            # Ergebnis zusammenstellen
            result = {
                "success": len(failed_files) == 0,
                "upload_folder": upload_folder,
                "workflow_folder": workflow_folder,
                "copied_files": copied_files,
                "failed_files": failed_files,
                "total_files": len(files),
                "copied_count": len(copied_files),
                "failed_count": len(failed_files),
                "is_new_folder": is_new
            }
            
            self._log_info(f"Upload abgeschlossen: {len(copied_files)}/{len(files)} Dateien erfolgreich")
            return result
            
        except Exception as e:
            self._log_error("Fehler beim Upload", e)
            return {
                "success": False,
                "error": str(e),
                "upload_folder": None,
                "copied_files": [],
                "failed_files": [{"file": f, "error": str(e)} for f in files],
                "total_files": len(files),
                "copied_count": 0,
                "failed_count": len(files)
            }
    
    def clear_upload_list(self):
        """Leert die Upload-Liste."""
        self.uploaded_files.clear()
        self.current_customer = None
        self._log_info("Upload-Liste geleert")
    
    def get_upload_summary(self) -> dict:
        """
        Gibt eine Zusammenfassung der aktuellen Upload-Session zurück.
        
        Returns:
            Dictionary mit Upload-Statistiken
        """
        return {
            "files_count": len(self.uploaded_files),
            "current_customer": self.current_customer,
            "files": self.uploaded_files.copy()
        }
