"""
Upload-Manager für die Checker-App
==================================

Dieser Manager integriert das erweiterte Upload-System in die Hauptanwendung.
Er bietet automatische Kundenablage, Fuzzy-Matching und Datumssortierung.
"""

import os
import shutil
import datetime
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from tkinter import filedialog, messagebox, simpledialog

from kunden_manager import KundenManager


class UploadManager:
    """
    Manager für erweiterte Upload-Funktionalität in der Checker-App.
    
    Features:
    - Automatische Kundenablage mit Datumsorganisation
    - Fuzzy-Matching für Kundenerkennung
    - Intelligente Kundenvorschläge aus Dateinamen
    - Integration mit bestehenden Workflows
    """
    
    def __init__(self, app_instance, kunden_manager: KundenManager):
        """
        Initialisiert den Upload-Manager.
        
        Args:
            app_instance: Referenz zur Hauptanwendung
            kunden_manager: Instanz des KundenManagers
        """
        self.app = app_instance
        self.kunden_manager = kunden_manager
        self.logger = getattr(app_instance, 'logger', None)
        
        # Upload-Daten
        self.uploaded_files: List[str] = []
        self.processed_files: List[Dict[str, Any]] = []
        self.current_customer: Optional[str] = None
        
        # Konfiguration
        self.fuzzy_threshold = 70  # Prozent für Fuzzy-Matching
        
        self._log_info("Upload-Manager initialisiert")
    
    def _log_info(self, message: str, extra_data: Dict = None):
        """Hilfsmethode für Logging."""
        if self.logger:
            if extra_data:
                self.logger.info(message, extra_data)
            else:
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
        Öffnet Dateiauswahl-Dialog und fügt Dateien zur Upload-Liste hinzu.
        
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
                    ("Excel Dateien", "*.xlsx;*.xls")
                ]
            )
            
            if files:
                # Füge neue Dateien hinzu (vermeide Duplikate)
                new_files = [f for f in files if f not in self.uploaded_files]
                self.uploaded_files.extend(new_files)
                
                self._log_info(f"{len(new_files)} neue Datei(en) zur Upload-Liste hinzugefügt", {
                    'total_files': len(self.uploaded_files),
                    'new_files': len(new_files)
                })
                
                # Zeige Toast-Benachrichtigung
                if hasattr(self.app, 'enhanced_ui') and self.app.enhanced_ui:
                    try:
                        self.app.enhanced_ui.show_toast(
                            f"{len(new_files)} Datei(en) hinzugefügt (Gesamt: {len(self.uploaded_files)})",
                            duration=2000
                        )
                    except Exception as e:
                        self._log_error("Toast-Fehler", e)
            
            return list(files) if files else []
            
        except Exception as e:
            self._log_error("Fehler bei Dateiauswahl", e)
            messagebox.showerror("Fehler", f"Dateiauswahl fehlgeschlagen: {e}")
            return []
    
    def clear_file_list(self):
        """Löscht die Upload-Liste."""
        self.uploaded_files.clear()
        self.processed_files.clear()
        self._log_info("Upload-Liste geleert")
        
        # Toast-Benachrichtigung
        if hasattr(self.app, 'enhanced_ui') and self.app.enhanced_ui:
            try:
                self.app.enhanced_ui.show_toast("Upload-Liste geleert", duration=1500)
            except Exception as e:
                self._log_error("Toast-Fehler", e)
    
    def get_customer_suggestions(self) -> List[Dict[str, str]]:
        """
        Analysiert Dateinamen und gibt Kundenvorschläge zurück.
        
        Returns:
            Liste von Dictionaries mit Dateiname und Kundenvorschlag
        """
        suggestions = []
        
        for file_path in self.uploaded_files:
            filename = os.path.basename(file_path)
            customer_suggestion = self._extract_customer_from_filename(filename)
            
            if customer_suggestion:
                suggestions.append({
                    'file': filename,
                    'suggestion': customer_suggestion,
                    'type': 'auto'  # Automatisch erkannt
                })
        
        self._log_info(f"Kundenvorschläge generiert: {len(suggestions)} aus {len(self.uploaded_files)} Dateien")
        return suggestions
    
    def _extract_customer_from_filename(self, filename: str) -> Optional[str]:
        """
        Extrahiert potenzielle Kundennamen aus Dateinamen.
        
        Args:
            filename: Name der Datei
            
        Returns:
            Kundenname oder None wenn nicht erkannt
        """
        # Entferne Dateiendung
        name_without_ext = os.path.splitext(filename)[0]
        
        # Muster für Kundennamen-Erkennung
        patterns = [
            r'([A-Za-z][A-Za-z0-9_\-\s]+)_[Aa]ngebot',           # Kunde_Angebot
            r'[Aa]ngebot_([A-Za-z][A-Za-z0-9_\-\s]+)',           # Angebot_Kunde
            r'([A-Za-z][A-Za-z0-9_\-\s]+)_[Pp]ruefung',          # Kunde_Pruefung
            r'[Pp]ruefung_([A-Za-z][A-Za-z0-9_\-\s]+)',          # Pruefung_Kunde
            r'^([A-Za-z][A-Za-z0-9_\-\s]+)_20\d{2}',             # Kunde_2024
            r'^([A-Za-z][A-Za-z0-9_\-\s]{2,})_\d+',              # Kunde_123
            r'^([A-Za-z][A-Za-z0-9_\-\s]{3,})_[A-Z]{2,3}$',      # Kunde_DE, Kunde_GER
        ]
        
        for pattern in patterns:
            match = re.search(pattern, name_without_ext, re.IGNORECASE)
            if match:
                potential_customer = match.group(1).strip()
                
                # Bereinige den Namen
                clean_name = re.sub(r'[_\-]+', '_', potential_customer)
                clean_name = clean_name.strip('_-')
                
                # Prüfe Fuzzy-Match mit bestehenden Kunden
                fuzzy_match = self.kunden_manager.find_customer_fuzzy(clean_name, self.fuzzy_threshold)
                if fuzzy_match:
                    return f"{fuzzy_match} (Fuzzy-Match)"
                else:
                    return f"{clean_name} (Neu)"
        
        return None
    
    def process_files_with_customer(self, customer_name: str, workflow: str = "Ausgangstexte") -> Dict[str, Any]:
        """
        Verarbeitet alle Upload-Dateien für einen bestimmten Kunden und Workflow.
        
        Args:
            customer_name: Name des Kunden
            workflow: Ziel-Workflow (Standard: Ausgangstexte)
            
        Returns:
            Dictionary mit Verarbeitungsstatistiken
        """
        if not self.uploaded_files:
            return {'success': False, 'error': 'Keine Dateien zum Verarbeiten vorhanden'}
        
        # Stelle sicher, dass der Kunde existiert oder verwende Fuzzy-Matching
        final_customer = self._resolve_customer_name(customer_name)
        if not final_customer:
            return {'success': False, 'error': f'Kunde "{customer_name}" konnte nicht aufgelöst werden'}
        
        # Verarbeite Dateien
        self.processed_files.clear()
        success_count = 0
        errors = []
        
        for file_path in self.uploaded_files:
            try:
                result = self._save_file_to_customer(file_path, final_customer, workflow)
                if result:
                    self.processed_files.append(result)
                    success_count += 1
                    self._log_info(f"Datei verarbeitet: {result['file']} → {result['relative_path']}")
                else:
                    error_msg = f"Unbekannter Fehler bei {os.path.basename(file_path)}"
                    errors.append(error_msg)
                    self._log_error(error_msg)
            except Exception as e:
                error_msg = f"Fehler bei {os.path.basename(file_path)}: {e}"
                errors.append(error_msg)
                self._log_error(error_msg, e)
        
        # Statistiken erstellen
        stats = {
            'success': success_count > 0,
            'total_files': len(self.uploaded_files),
            'success_count': success_count,
            'error_count': len(errors),
            'errors': errors,
            'customer': final_customer,
            'workflow': workflow,
            'processed_files': self.processed_files.copy()
        }
        
        # Toast-Benachrichtigung
        if hasattr(self.app, 'enhanced_ui') and self.app.enhanced_ui:
            try:
                if success_count > 0:
                    self.app.enhanced_ui.show_toast(
                        f"{success_count}/{len(self.uploaded_files)} Datei(en) erfolgreich für '{final_customer}' gespeichert",
                        duration=3000
                    )
                else:
                    self.app.enhanced_ui.show_toast(
                        "Keine Dateien konnten verarbeitet werden",
                        duration=3000
                    )
            except Exception as e:
                self._log_error("Toast-Fehler", e)
        
        self._log_info(f"Upload-Verarbeitung abgeschlossen", stats)
        return stats
    
    def _resolve_customer_name(self, customer_input: str) -> Optional[str]:
        """
        Löst einen Kundennamen auf - mit Fuzzy-Matching oder Neuanlage.
        
        Args:
            customer_input: Eingabe-Kundenname
            
        Returns:
            Finaler Kundenname oder None bei Fehler
        """
        if not customer_input or not customer_input.strip():
            return None
        
        customer_input = customer_input.strip()
        
        # Prüfe exakte Übereinstimmung oder Fuzzy-Match
        exists, matched_customer = self.kunden_manager.customer_exists(customer_input)
        
        if exists:
            if matched_customer != customer_input:
                # Fuzzy-Match gefunden - frage Benutzer
                result = messagebox.askyesno(
                    "Ähnlicher Kunde gefunden",
                    f"Ähnlicher Kunde gefunden: '{matched_customer}'\n\nSoll dieser verwendet werden?",
                    parent=getattr(self.app, 'root', None)
                )
                if result:
                    return matched_customer
                else:
                    # Benutzer möchte neuen Kunden anlegen
                    return self._create_new_customer(customer_input)
            else:
                # Exakter Match
                return matched_customer
        else:
            # Kein Match - neuen Kunden erstellen
            return self._create_new_customer(customer_input)
    
    def _create_new_customer(self, customer_name: str) -> Optional[str]:
        """
        Erstellt einen neuen Kunden nach Benutzerbestätigung.
        
        Args:
            customer_name: Name des neuen Kunden
            
        Returns:
            Kundenname oder None bei Abbruch
        """
        create_new = messagebox.askyesno(
            "Neuer Kunde",
            f"Kunde '{customer_name}' existiert nicht.\n\nSoll ein neuer Kunde erstellt werden?",
            parent=getattr(self.app, 'root', None)
        )
        
        if create_new:
            try:
                customer_path = self.kunden_manager.erstelle_kundenstruktur(customer_name)
                self._log_info(f"Neuer Kunde für Upload erstellt: {customer_name} → {customer_path}")
                
                # Toast-Benachrichtigung
                if hasattr(self.app, 'enhanced_ui') and self.app.enhanced_ui:
                    try:
                        self.app.enhanced_ui.show_toast(
                            f"Neuer Kunde '{customer_name}' erstellt",
                            duration=2000
                        )
                    except Exception as e:
                        self._log_error("Toast-Fehler", e)
                
                return customer_name
            except Exception as e:
                self._log_error(f"Fehler beim Erstellen des Kunden {customer_name}", e)
                messagebox.showerror("Fehler", f"Kunde konnte nicht erstellt werden: {e}")
                return None
        
        return None
    
    def _save_file_to_customer(self, file_path: str, customer_name: str, workflow: str) -> Optional[Dict[str, Any]]:
        """
        Speichert eine Datei im Kundenordner mit Datumsorganisation.
        
        Args:
            file_path: Pfad zur Quelldatei
            customer_name: Name des Kunden
            workflow: Workflow-Name
            
        Returns:
            Dictionary mit Speicher-Informationen oder None bei Fehler
        """
        try:
            # Stelle sicher, dass der Kunde existiert
            if not os.path.exists(self.kunden_manager.kunden_ordner(customer_name)):
                self.kunden_manager.erstelle_kundenstruktur(customer_name)
            
            # Datums-basierte Ordnerstruktur
            heute = datetime.date.today().isoformat()
            
            # Zielordner bestimmen
            workflow_ordner = self.kunden_manager.get_ordner_fuer_workflow(customer_name, workflow)
            datums_ordner = os.path.join(workflow_ordner, heute)
            
            # Ordner erstellen
            os.makedirs(datums_ordner, exist_ok=True)
            
            # Dateiname und Ziel
            original_filename = os.path.basename(file_path)
            ziel_pfad = os.path.join(datums_ordner, original_filename)
            
            # Datei kopieren (nicht verschieben, falls Original erhalten bleiben soll)
            shutil.copy2(file_path, ziel_pfad)
            
            # Relative Pfad für Anzeige
            relative_path = os.path.relpath(ziel_pfad, self.kunden_manager.base_dir)
            
            return {
                'file': original_filename,
                'source_path': file_path,
                'destination': ziel_pfad,
                'relative_path': relative_path,
                'customer': customer_name,
                'workflow': workflow,
                'date': heute,
                'size': os.path.getsize(file_path) if os.path.exists(file_path) else 0
            }
            
        except Exception as e:
            self._log_error(f"Fehler beim Speichern der Datei {file_path}", e)
            return None
    
    def interactive_upload_workflow(self) -> Optional[Dict[str, Any]]:
        """
        Führt einen interaktiven Upload-Workflow durch.
        
        Returns:
            Verarbeitungsstatistiken oder None bei Abbruch
        """
        if not self.uploaded_files:
            messagebox.showwarning(
                "Keine Dateien", 
                "Bitte wählen Sie zuerst Dateien aus.",
                parent=getattr(self.app, 'root', None)
            )
            return None
        
        # Schritt 1: Kundenvorschläge anzeigen
        suggestions = self.get_customer_suggestions()
        if suggestions:
            suggestion_text = "\n".join([f"• {s['file']} → {s['suggestion']}" for s in suggestions])
            messagebox.showinfo(
                "Kundenvorschläge",
                f"Automatische Kundenvorschläge:\n\n{suggestion_text}",
                parent=getattr(self.app, 'root', None)
            )
        
        # Schritt 2: Kunde bestimmen
        customer_name = self._get_customer_for_upload()
        if not customer_name:
            return None
        
        # Schritt 3: Workflow auswählen
        workflow = self._get_workflow_for_upload()
        if not workflow:
            return None
        
        # Schritt 4: Dateien verarbeiten
        return self.process_files_with_customer(customer_name, workflow)
    
    def _get_customer_for_upload(self) -> Optional[str]:
        """
        Ermittelt den Kunden für den Upload - interaktiv.
        
        Returns:
            Kundenname oder None bei Abbruch
        """
        # Kunde eingeben
        customer_input = simpledialog.askstring(
            "Kunde für Upload",
            "Kundenname eingeben (bei ähnlichen Namen wird automatisch zugeordnet):",
            parent=getattr(self.app, 'root', None)
        )
        
        if not customer_input or not customer_input.strip():
            return None
        
        return self._resolve_customer_name(customer_input.strip())
    
    def _get_workflow_for_upload(self) -> Optional[str]:
        """
        Ermittelt den Workflow für den Upload - interaktiv.
        
        Returns:
            Workflow-Name oder None bei Abbruch
        """
        workflows = ["Ausgangstexte", "Angebot", "Pruefung", "Finalisierung"]
        
        # Einfache Workflow-Auswahl
        workflow_text = "\n".join([f"{i+1}. {w}" for i, w in enumerate(workflows)])
        
        selection = simpledialog.askstring(
            "Workflow auswählen",
            f"Workflow-Nummer eingeben:\n\n{workflow_text}\n\n(Standard: 1 - Ausgangstexte)",
            parent=getattr(self.app, 'root', None)
        )
        
        if not selection or not selection.strip():
            return "Ausgangstexte"  # Standard
        
        try:
            index = int(selection.strip()) - 1
            if 0 <= index < len(workflows):
                return workflows[index]
            else:
                return "Ausgangstexte"
        except ValueError:
            return "Ausgangstexte"
    
    def get_upload_statistics(self) -> Dict[str, Any]:
        """
        Gibt Statistiken über die aktuellen Uploads zurück.
        
        Returns:
            Dictionary mit Upload-Statistiken
        """
        total_size = 0
        for file_path in self.uploaded_files:
            if os.path.exists(file_path):
                total_size += os.path.getsize(file_path)
        
        return {
            'uploaded_files_count': len(self.uploaded_files),
            'processed_files_count': len(self.processed_files),
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'current_customer': self.current_customer,
            'has_files': len(self.uploaded_files) > 0,
            'has_processed': len(self.processed_files) > 0
        }
    
    def open_customer_folder(self, customer_name: Optional[str] = None) -> bool:
        """
        Öffnet den Kundenordner im Datei-Explorer.
        
        Args:
            customer_name: Name des Kunden (optional, verwendet aktuellen Kunden)
            
        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        if not customer_name:
            customer_name = self.current_customer
        
        if not customer_name:
            messagebox.showwarning(
                "Kein Kunde", 
                "Kein Kunde ausgewählt.",
                parent=getattr(self.app, 'root', None)
            )
            return False
        
        customer_path = self.kunden_manager.kunden_ordner(customer_name)
        
        if not os.path.exists(customer_path):
            messagebox.showerror(
                "Fehler", 
                f"Kundenordner nicht gefunden: {customer_path}",
                parent=getattr(self.app, 'root', None)
            )
            return False
        
        try:
            # Windows-spezifisch - kann erweitert werden für andere OS
            os.startfile(customer_path)
            
            self._log_info(f"Kundenordner geöffnet: {customer_path}")
            
            # Toast-Benachrichtigung
            if hasattr(self.app, 'enhanced_ui') and self.app.enhanced_ui:
                try:
                    self.app.enhanced_ui.show_toast(
                        f"Ordner für '{customer_name}' geöffnet",
                        duration=2000
                    )
                except Exception as e:
                    self._log_error("Toast-Fehler", e)
            
            return True
            
        except Exception as e:
            self._log_error(f"Fehler beim Öffnen des Ordners {customer_path}", e)
            messagebox.showerror(
                "Fehler", 
                f"Ordner konnte nicht geöffnet werden: {e}",
                parent=getattr(self.app, 'root', None)
            )
            return False
    
    def suggest_workflow_from_filename(self, filename: str) -> Optional[str]:
        """
        Schlägt einen Workflow basierend auf dem Dateinamen vor.
        
        Args:
            filename: Der Dateiname für die Analyse
            
        Returns:
            Vorgeschlagener Workflow oder None
        """
        try:
            filename_lower = filename.lower()
            
            # Workflow-Schlüsselwörter
            workflow_keywords = {
                'Angebot': ['angebot', 'quote', 'proposal', 'offerte', 'kostenvoranschlag'],
                'Pruefung': ['pruef', 'check', 'review', 'korrektur', 'revision', 'quality'],
                'Finalisierung': ['final', 'delivery', 'lieferung', 'abschluss', 'fertig']
            }
            
            # Prüfe Schlüsselwörter
            for workflow, keywords in workflow_keywords.items():
                if any(keyword in filename_lower for keyword in keywords):
                    return workflow
            
            # Standard-Fallback basierend auf Dateityp
            if filename_lower.endswith(('.pdf', '.docx', '.doc')):
                return 'Pruefung'  # Dokumente meist zur Prüfung
            elif filename_lower.endswith(('.xlsx', '.xls')):
                return 'Angebot'   # Excel meist für Angebote
            
            return None
            
        except Exception as e:
            self._log_error("Fehler bei Workflow-Vorschlag", e)
            return None
    
    def get_customer_upload_stats(self, customer_name: str) -> Dict[str, Any]:
        """
        Holt Upload-Statistiken für einen bestimmten Kunden.
        
        Args:
            customer_name: Name des Kunden
            
        Returns:
            Dictionary mit Upload-Statistiken
        """
        try:
            customer_path = self.kunden_manager.kunden_ordner(customer_name)
            
            if not os.path.exists(customer_path):
                return {'total_uploads': 0, 'total_size_mb': 0}
            
            total_files = 0
            total_size = 0
            
            # Durchsuche alle Workflow-Ordner
            for workflow in ["Angebot", "Pruefung", "Finalisierung"]:
                workflow_path = self.kunden_manager.get_ordner_fuer_workflow(customer_name, workflow)
                if os.path.exists(workflow_path):
                    for root, dirs, files in os.walk(workflow_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            if os.path.isfile(file_path):
                                total_files += 1
                                try:
                                    total_size += os.path.getsize(file_path)
                                except OSError:
                                    pass  # Datei nicht zugreifbar
            
            return {
                'total_uploads': total_files,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'customer': customer_name
            }
            
        except Exception as e:
            self._log_error(f"Fehler beim Laden der Upload-Statistiken für {customer_name}", e)
            return {'total_uploads': 0, 'total_size_mb': 0}
    
    def process_files_to_customer(self, customer_name: str, workflow: str) -> Dict[str, Any]:
        """
        Verarbeitet Dateien direkt zu einem bestimmten Kunden und Workflow.
        
        Args:
            customer_name: Name des Zielkunden
            workflow: Ziel-Workflow
            
        Returns:
            Dictionary mit Verarbeitungsresultaten
        """
        try:
            if not self.uploaded_files:
                return {'success': False, 'error': 'Keine Dateien zum Verarbeiten'}
            
            # Setze Kunde und starte Verarbeitung
            self.current_customer = customer_name
            
            # Verarbeite Dateien
            result = self._process_files_to_workflow(customer_name, workflow)
            
            if result.get('success'):
                # Aktualisiere interne Listen
                self.processed_files.extend(result.get('processed_files', []))
                self.uploaded_files.clear()  # Leere Upload-Liste nach erfolgreichem Upload
                
                self._log_info(f"Upload zu {customer_name} abgeschlossen", {
                    'workflow': workflow,
                    'files_processed': result.get('success_count', 0)
                })
            
            return result
            
        except Exception as e:
            self._log_error("Fehler beim Verarbeiten der Dateien", e)
            return {'success': False, 'error': str(e)}
    
    def _process_files_to_workflow(self, customer_name: str, workflow: str) -> Dict[str, Any]:
        """
        Interne Methode zur Dateiverarbeitung.
        
        Args:
            customer_name: Kundenname
            workflow: Workflow-Name
            
        Returns:
            Verarbeitungsresultat
        """
        try:
            processed_files = []
            errors = []
            
            # Erstelle Zielordner
            target_path = self.kunden_manager.get_ordner_fuer_workflow(customer_name, workflow)
            
            # Erstelle datumsbasierten Unterordner
            date_folder = datetime.datetime.now().strftime("%Y-%m-%d")
            dated_target_path = os.path.join(target_path, date_folder)
            
            os.makedirs(dated_target_path, exist_ok=True)
            
            # Verarbeite jede Datei
            for file_path in self.uploaded_files:
                try:
                    if not os.path.exists(file_path):
                        errors.append(f"Datei nicht gefunden: {os.path.basename(file_path)}")
                        continue
                    
                    filename = os.path.basename(file_path)
                    target_file_path = os.path.join(dated_target_path, filename)
                    
                    # Kopiere Datei
                    shutil.copy2(file_path, target_file_path)
                    
                    # Erstelle relative Pfad-Info
                    relative_path = os.path.relpath(target_file_path, self.kunden_manager.base_path)
                    
                    processed_files.append({
                        'file': filename,
                        'source_path': file_path,
                        'target_path': target_file_path,
                        'relative_path': relative_path,
                        'size_mb': round(os.path.getsize(file_path) / (1024 * 1024), 2)
                    })
                    
                except Exception as e:
                    errors.append(f"Fehler bei {os.path.basename(file_path)}: {str(e)}")
            
            return {
                'success': len(processed_files) > 0,
                'customer': customer_name,
                'workflow': workflow,
                'processed_files': processed_files,
                'success_count': len(processed_files),
                'total_files': len(self.uploaded_files),
                'errors': errors,
                'target_path': dated_target_path
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'customer': customer_name,
                'workflow': workflow
            }
