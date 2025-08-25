
from typing import Dict, List, Optional, Any, Tuple
VALID_WORKFLOWS: Tuple[str, ...] = ("Ausgangstexte", "Angebot", "Pruefung", "Finalisierung")

def _validate_workflow(w: str) -> str:
    return w if w in VALID_WORKFLOWS else "Ausgangstexte"
"""
Upload-Manager für die Checker-App
==================================

Dieser Manager integriert das erweiterte Upload-System in die Hauptanwendung.
Er bietet automatische Kundenablage, Fuzzy-Matching und Datumssortierung.
"""

from typing import Dict, List, Optional, Any
import datetime
import os
import sys
import subprocess
import re

from tkinter import filedialog, messagebox, simpledialog
import shutil

# Robuster Import des KundenManagers – unterstütze verschiedene Modulpfade
try:
    # gleicher Ordner (Package-Import)
    from .kunden_manager import KundenManager  # type: ignore
except Exception:
    try:
        # absoluter Paketpfad
        from src.managers.kunden_manager import KundenManager  # type: ignore
    except Exception:
        try:
            # legacy: top-level Import falls im PYTHONPATH
            from kunden_manager import KundenManager  # type: ignore
        except Exception:
            KundenManager = None  # type: ignore


class UploadManager:
    """
    Manager für erweiterte Upload-Funktionalität in der Checker-App.

    Features:
    - Automatische Kundenablage mit Datumsorganisation
    - Fuzzy-Matching für Kundenerkennung
    - Intelligente Kundenvorschläge aus Dateinamen
    - Integration mit bestehenden Workflows
    """

    def __init__(self, app_instance, kunden_manager):
        """
        Initialisiert den Upload-Manager.

        Args:
            app_instance: Referenz zur Hauptanwendung
            kunden_manager: Instanz des KundenManagers (optional)
        """
        # Akzeptiere die übergebene Instanz, auch wenn der Klassenimport nicht auflösbar ist
        if kunden_manager is None:
            raise RuntimeError("KundenManager-Instanz fehlt – UploadManager benötigt eine gültige Instanz.")
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

    def _get_unique_target(self, folder: str, filename: str) -> str:
        """Ermittelt einen kollisionsfreien Zielpfad in 'folder' für 'filename'.

        Falls der Dateiname bereits existiert, wird ein Suffix "-01", "-02", ...
        vor der Dateiendung eingefügt, bis ein freier Name gefunden ist.
        """
        try:
            os.makedirs(folder, exist_ok=True)
        except Exception:
            # Falls Ordner bereits existiert oder nicht erstellt werden kann, ignorieren wir hier – Copy wird ggf. fehlschlagen
            pass

        base, ext = os.path.splitext(filename)
        candidate = os.path.join(folder, filename)
        if not os.path.exists(candidate):
            return candidate

        i = 1
        while True:
            new_name = f"{base}-{i:02d}{ext}"
            candidate = os.path.join(folder, new_name)
            if not os.path.exists(candidate):
                return candidate
            i += 1

    def _log_info(self, message: str, extra_data: Dict = None):
        """Hilfsmethode für Info-Logging mit strukturierten Feldern über extra."""
        if self.logger:
            if extra_data:
                self.logger.info(message, extra={"ctx": extra_data})
            else:
                self.logger.info(message)
        else:
            print(f"[UPLOAD] {message} | {extra_data or ''}")

    def _is_headless(self) -> bool:
        """True, wenn keine interaktive UI vorhanden ist (z. B. während Tests)."""
        try:
            if getattr(self.app, 'root', None) is None:
                return True
        except Exception:
            return True
        # PyTest-Indikator als zusätzlicher Hinweis
        return bool(os.environ.get("PYTEST_CURRENT_TEST"))

    def _log_error(self, message: str, error: Exception = None, extra_data: Dict = None):
        """Hilfsmethode für Error-Logging mit extra und optionalem Stacktrace."""
        if self.logger:
            extra = {"ctx": extra_data} if extra_data else None
            if error:
                self.logger.error(message, exc_info=error, extra=extra)
            else:
                self.logger.error(message, extra=extra)
        else:
            if error:
                print(f"[UPLOAD ERROR] {message}: {error}")
            else:
                print(f"[UPLOAD ERROR] {message}")
            if extra_data:
                print(f"[UPLOAD ERROR] ctx: {extra_data}")

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
            if not self._is_headless():
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
            Liste von Dictionaries mit Dateiname, Vorschlag und Match-Typ
        """
        suggestions = []
        for file_path in self.uploaded_files:
            filename = os.path.basename(file_path)
            suggestion = self._extract_customer_from_filename(filename)
            if suggestion:
                suggestions.append({
                    'file': filename,
                    'suggestion': suggestion['suggestion'],
                    'match_type': suggestion['match_type']
                })
        self._log_info(f"Kundenvorschläge generiert: {len(suggestions)} aus {len(self.uploaded_files)} Dateien")
        return suggestions

    def _extract_customer_from_filename(self, filename: str) -> Optional[Dict[str, str]]:
        """Extrahiert potenzielle Kundennamen aus Dateinamen und gibt strukturierten Vorschlag zurück."""
        if KundenManager is None or self.kunden_manager is None:
            raise RuntimeError("KundenManager nicht verfügbar – UploadManager benötigt eine gültige Instanz.")
        name_without_ext = os.path.splitext(filename)[0]
        patterns = [
            r'([A-Za-z][A-Za-z0-9_\-\s]+)_[Aa]ngebot',
            r'[Aa]ngebot_([A-Za-z][A-Za-z0-9_\-\s]+)',
            r'([A-Za-z][A-Za-z0-9_\-\s]+)_[Pp]ruefung',
            r'[Pp]ruefung_([A-Za-z][A-Za-z0-9_\-\s]+)',
            r'^([A-Za-z][A-Za-z0-9_\-\s]+)_20\d{2}',
            r'^([A-Za-z][A-Za-z0-9_\-\s]{2,})_\d+',
            r'^([A-Za-z][A-Za-z0-9_\-\s]{3,})_[A-Z]{2,3}$',
        ]
        for pattern in patterns:
            m = re.search(pattern, name_without_ext, re.IGNORECASE)
            if m:
                raw = m.group(1).strip()
                clean = re.sub(r'[_\-]+', '_', raw).strip('_-')
                fuzzy = self.kunden_manager.find_customer_fuzzy(clean, self.fuzzy_threshold)
                if fuzzy:
                    return {'suggestion': fuzzy, 'match_type': 'fuzzy'}
                return {'suggestion': clean, 'match_type': 'new'}
        return None

    def process_files_with_customer(self, customer_name: str, workflow: str = "Ausgangstexte") -> Dict[str, Any]:
        """
        Verarbeitet alle Upload-Dateien für einen bestimmten Kunden und Workflow. Nutzt zentrale _process_files_to_workflow-Logik.
        Falls kein Workflow übergeben wird, wird suggest_workflow_from_filename genutzt.
        """
        if KundenManager is None or self.kunden_manager is None:
            raise RuntimeError("KundenManager nicht verfügbar – UploadManager benötigt eine gültige Instanz.")
        if not self.uploaded_files:
            return {'success': False, 'error': 'Keine Dateien zum Verarbeiten vorhanden'}

        # Stelle sicher, dass der Kunde existiert oder verwende Fuzzy-Matching
        final_customer = self._resolve_customer_name(customer_name)
        if not final_customer:
            return {'success': False, 'error': f'Kunde "{customer_name}" konnte nicht aufgelöst werden'}

        # Workflow-Vorschlag nutzen, falls nicht explizit übergeben
        if not workflow or workflow not in VALID_WORKFLOWS:
            # Versuche, aus erstem Dateinamen einen Workflow zu bestimmen
            if self.uploaded_files:
                first_file = os.path.basename(self.uploaded_files[0])
                suggested = self.suggest_workflow_from_filename(first_file)
                workflow = suggested if suggested in VALID_WORKFLOWS else _validate_workflow(workflow)
            else:
                workflow = _validate_workflow(workflow)
        else:
            workflow = _validate_workflow(workflow)

        return self._process_files_to_workflow(final_customer, workflow)

    def _resolve_customer_name(self, customer_input: str) -> Optional[str]:
        """Löst einen Kundennamen auf – mit Fuzzy-Matching oder Neuanlage."""
        if KundenManager is None or self.kunden_manager is None:
            raise RuntimeError("KundenManager nicht verfügbar – UploadManager benötigt eine gültige Instanz.")
        if not customer_input or not customer_input.strip():
            return None

        customer_input = customer_input.strip()

        # Prüfe exakte Übereinstimmung oder Fuzzy-Match
        # KundenManager.customer_exists liefert (exists, matched_customer, similarity_score)
        result = self.kunden_manager.customer_exists(customer_input)
        try:
            exists, matched_customer, _score = result
        except Exception:
            # Rückwärtskompatibilität, falls nur 2 Werte zurückgegeben werden
            exists, matched_customer = result if isinstance(result, (list, tuple)) and len(result) >= 2 else (False, None)

        if exists:
            if matched_customer != customer_input:
                # Fuzzy-Match gefunden - in Headless-Mode automatisch übernehmen
                if self._is_headless():
                    return matched_customer
                # Benutzer synchron fragen (Rollback von non-blocking, da aufrufende Pipeline unmittelbares Ergebnis benötigt)
                result = messagebox.askyesno(
                    "Ähnlicher Kunde gefunden",
                    f"Ähnlicher Kunde gefunden: '{matched_customer}'\n\nSoll dieser verwendet werden?",
                    parent=getattr(self.app, 'root', None)
                )
                if result:
                    return matched_customer
                else:
                    return self._create_new_customer(customer_input)
            else:
                # Exakter Match
                return matched_customer
        else:
            # Kein Match - neuen Kunden erstellen
            return self._create_new_customer(customer_input)

    def _create_new_customer(self, customer_name: str) -> Optional[str]:
        """Erstellt einen neuen Kunden nach Benutzerbestätigung."""
        if KundenManager is None or self.kunden_manager is None:
            raise RuntimeError("KundenManager nicht verfügbar – UploadManager benötigt eine gültige Instanz.")
        # In Headless-Umgebungen automatisch anlegen
        if self._is_headless():
            create_new = True
        else:
            # Synchronous Dialog (Rollback von non-blocking wegen benötigtem unmittelbarem Rückgabewert)
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
        """Speichert eine Datei im Kundenordner mit neuer Projekt-Struktur."""
        if KundenManager is None or self.kunden_manager is None:
            raise RuntimeError("KundenManager nicht verfügbar – UploadManager benötigt eine gültige Instanz.")
        try:
            # Stelle sicher, dass der Kunde existiert
            if not os.path.exists(self.kunden_manager.kunden_ordner(customer_name)):
                self.kunden_manager.erstelle_kundenstruktur(customer_name)

            # Heutiges Datum als Projekt-ID
            heute = datetime.date.today().isoformat()
            
            # Suche existierendes Projekt für heute oder erstelle neues
            existing_projects = self.kunden_manager.liste_kundenprojekte(customer_name)
            today_project = None
            for project_id in existing_projects:
                if project_id.startswith(heute):
                    today_project = project_id
                    break
            
            if not today_project:
                # Erstelle neues Projekt für heute
                projekt_path, today_project = self.kunden_manager.erstelle_projekt_ordner(customer_name, datum=heute)
            
            # Workflow-Ordner in Projekt (nummeriert nach Mapping)
            workflow_ordner = self.kunden_manager.get_projekt_workflow_ordner(customer_name, today_project, workflow)

            # Ordner sicherstellen
            os.makedirs(workflow_ordner, exist_ok=True)

            # Dateiname und kollisionsfreier Zielpfad
            original_filename = os.path.basename(file_path)
            ziel_pfad = self._get_unique_target(workflow_ordner, original_filename)

            # Datei kopieren
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
                'project_id': today_project,
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
            if not self._is_headless():
                messagebox.showwarning(
                    "Keine Dateien",
                    "Bitte wählen Sie zuerst Dateien aus.",
                    parent=getattr(self.app, 'root', None)
                )
            return None

        # Schritt 1: Kundenvorschläge anzeigen
        suggestions = self.get_customer_suggestions()
        if suggestions and not self._is_headless():
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
        Gibt im Headless-Modus sofort None zurück (kein Dialog).
        """
        if self._is_headless():
            return None
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
        Ermittelt den Workflow für den Upload - interaktiv, nutzt zentrale Workflow-Liste und Validierung.

        Returns:
            Workflow-Name oder None bei Abbruch
        """
        workflow_list = list(VALID_WORKFLOWS)
        workflow_text = "\n".join([f"{i+1}. {w}" for i, w in enumerate(workflow_list)])

        # Dialog nur anzeigen, wenn nicht headless
        if self._is_headless():
            return workflow_list[0]  # Standard: "Ausgangstexte"

        selection = simpledialog.askstring(
            "Workflow auswählen",
            f"Workflow-Nummer eingeben:\n\n{workflow_text}\n\n(Standard: 1 - {workflow_list[0]})",
            parent=getattr(self.app, 'root', None)
        )

        if not selection or not selection.strip():
            return workflow_list[0]  # Standard

        try:
            index = int(selection.strip()) - 1
            if 0 <= index < len(workflow_list):
                return workflow_list[index]
            else:
                return workflow_list[0]
        except ValueError:
            return workflow_list[0]

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
            if not self._is_headless():
                messagebox.showwarning(
                    "Kein Kunde",
                    "Kein Kunde ausgewählt.",
                    parent=getattr(self.app, 'root', None)
                )
            return False

        customer_path = self.kunden_manager.kunden_ordner(customer_name)

        if not os.path.exists(customer_path):
            if not self._is_headless():
                messagebox.showerror(
                    "Fehler",
                    f"Kundenordner nicht gefunden: {customer_path}",
                    parent=getattr(self.app, 'root', None)
                )
            return False

        try:
            # OS-portabel öffnen
            if sys.platform.startswith("win"):
                os.startfile(customer_path)  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.Popen(["open", customer_path])
            else:
                subprocess.Popen(["xdg-open", customer_path])

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
            if not self._is_headless():
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
        Hinweis: "Ausgangstexte"-Ordner wird bewusst ignoriert, da dort keine echten Uploads gezählt werden sollen.
        """
        if KundenManager is None or self.kunden_manager is None:
            raise RuntimeError("KundenManager nicht verfügbar – UploadManager benötigt eine gültige Instanz.")
        try:
            customer_path = self.kunden_manager.kunden_ordner(customer_name)

            if not os.path.exists(customer_path):
                return {'total_uploads': 0, 'total_size_mb': 0}

            total_files = 0
            total_size = 0

            # Durchsuche alle Workflow-Ordner (zentral aus VALID_WORKFLOWS, außer "Ausgangstexte")
            # "Ausgangstexte" wird bewusst ignoriert, da dort keine echten Uploads gezählt werden sollen.
            for workflow in VALID_WORKFLOWS:
                if workflow == "Ausgangstexte":
                    continue
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
        """Verarbeitet Dateien direkt zu einem bestimmten Kunden und Workflow."""
        if KundenManager is None or self.kunden_manager is None:
            raise RuntimeError("KundenManager nicht verfügbar – UploadManager benötigt eine gültige Instanz.")
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
        """Interne Methode zur Dateiverarbeitung."""
        if KundenManager is None or self.kunden_manager is None:
            raise RuntimeError("KundenManager nicht verfügbar – UploadManager benötigt eine gültige Instanz.")
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
                    target_file_path = self._get_unique_target(dated_target_path, filename)

                    # Kopiere Datei
                    shutil.copy2(file_path, target_file_path)

                    # Erstelle relative Pfad-Info (Basis ist KundenManager.base_dir)
                    relative_path = os.path.relpath(target_file_path, self.kunden_manager.base_dir)

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