from typing import List, Dict, Optional, Tuple, Any
import datetime
import os
import re
import unicodedata
import logging
import contextlib
import json

from rapidfuzz import process, fuzz
import shutil
try:
    # Optional dependency – provides robust cross-process file locks
    from filelock import FileLock  # type: ignore
except Exception:  # pragma: no cover - fallback if not installed
    FileLock = None  # type: ignore

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

    def __init__(self, base_dir: str = "Checker_Projekte"):
        self.base_dir = base_dir
        # Logische Workflow-Namen (intern/UI)
        self.workflows = ["Ausgangstexte", "Angebot", "Pruefung", "Finalisierung"]
        # Physische Ordnernamen (nummeriert) – Zielstruktur gemäß Vorgabe
        # Mapping nur hier zentral pflegen; Migration: falls alter (unnummerierter) Ordner existiert, wird er weiter genutzt
        self.workflow_folder_map = {
            "Ausgangstexte": "01_Ausgangstext",
            "Angebot": "02_Angebot",
            "Pruefung": "03_Prüfung",  # Umlaut wie in gewünschter Struktur
            "Finalisierung": "04_Finalisierung",
        }
        os.makedirs(self.base_dir, exist_ok=True)
        # Konsistenter Logger (keine globale Konfiguration, NullHandler verhindert Warnungen)
        if not hasattr(self, 'logger') or self.logger is None:
            self.logger = logging.getLogger(f"{__name__}.KundenManager")
            if not self.logger.handlers:
                self.logger.addHandler(logging.NullHandler())
        # Einmalige Warnung, falls filelock fehlt
        self._warned_no_filelock: bool = False

    # --- Locking Helpers -------------------------------------------------
    def _get_customer_lock_path(self, kundenname: str) -> str:
        safe_name = self._sanitize_name(kundenname)
        kundenpfad = self.kunden_ordner(safe_name)
        # Sperrdatei pro Kunde – schützt projektweite Operationen (Erstellen/Umbenennen/Migration)
        return os.path.join(kundenpfad, ".customer.lock")

    def _customer_lock(self, kundenname: str, timeout: int = 30):
        """Kontextmanager für einen kundenspezifischen File-Lock.

        Nutzt filelock.FileLock wenn vorhanden, sonst no-op Fallback.
        """
        # Stelle sicher, dass es den Kundenordner gibt, damit der Lock-Pfad valide ist
        try:
            os.makedirs(self.kunden_ordner(self._sanitize_name(kundenname)), exist_ok=True)
        except Exception:
            pass

        if FileLock is not None:
            lock_path = self._get_customer_lock_path(kundenname)
            return FileLock(lock_path, timeout=timeout)
        else:
            # Hinweis im Logger nur einmal, dass nur Prozess-interne Sicherheit besteht
            if not getattr(self, "_warned_no_filelock", False):
                try:
                    self.logger.warning("filelock nicht installiert – Cross-Process-Transaktionsschutz deaktiviert")
                except Exception:
                    pass
                self._warned_no_filelock = True
            return contextlib.nullcontext()

    # Windows reservierte Namen (basenames) blocken
    _WINDOWS_RESERVED = {"con", "prn", "aux", "nul", *{f"com{i}" for i in range(1, 10)}, *{f"lpt{i}" for i in range(1, 10)}}

    def _sanitize_name(self, name: Any) -> str:
        """Bereinigt Namen von ungültigen Zeichen für Dateinamen.

        Schritte:
        1) Unicode-Normalisierung (NFC) für konsistente Darstellung von Umlauten/Combining Marks
        2) Ersetzen problematischer Dateisystem-Zeichen durch "_"
        3) Mehrfache und führende/abschließende Unterstriche bereinigen
        """
        if not name:
            return "Unbenannt"

        # Unicode NFC Normalisierung (z. B. "Mu\u0308ller" → "Müller")
        name = unicodedata.normalize('NFC', str(name))

        # Ersetze ungültige Zeichen durch Unterstriche
        sanitized = re.sub(r'[<>:\"/\\|?*]', '_', name)
        # Normalisiere Whitespaces (inkl. Tabs/Zeilenumbrüche) zu Unterstrichen
        sanitized = re.sub(r'\s+', '_', sanitized)
        # Entferne mehrfache Unterstriche
        sanitized = re.sub(r'_+', '_', sanitized)
        # Entferne führende/nachfolgende Unterstriche
        sanitized = sanitized.strip('_')

        # Windows reservierte Basenamen abfangen (case-insensitive)
        try:
            base_lower = sanitized.lower()
            if base_lower in self._WINDOWS_RESERVED:
                sanitized = f"_{sanitized}"
        except Exception:
            pass

        # Fail-safe: Falls alles weggefallen ist, Standard verwenden
        return sanitized or "Unbenannt"

    def _generate_project_id(self, projektname: Optional[str] = None, datum: Optional[str] = None) -> str:
        """Generiert eine eindeutige Projekt-ID basierend auf Datum und Projektname"""
        if datum is None:
            datum = datetime.date.today().isoformat()

        project_id = datum
        if projektname:
            safe_projektname = self._sanitize_name(projektname)
            project_id += f"_{safe_projektname.replace(' ', '_')}"

        return project_id

    def _parse_project_date(self, project_id: str) -> Optional[datetime.date]:
        """Parst das Datum am Anfang der Projekt-ID robust.

        Unterstützte Formate am Präfix:
        - YYYY-MM-DD
        - YYYY_MM_DD (wird in YYYY-MM-DD konvertiert)
        - YYYYMMDD

        Gibt None zurück, wenn kein Datum erkannt werden kann.
        """
        try:
            # 1) YYYY-MM-DD
            m = re.match(r"^(\d{4}-\d{2}-\d{2})", project_id)
            if m:
                return datetime.date.fromisoformat(m.group(1))

            # 2) YYYY_MM_DD → ersetze '_' durch '-'
            m = re.match(r"^(\d{4})_(\d{2})_(\d{2})", project_id)
            if m:
                iso = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
                return datetime.date.fromisoformat(iso)

            # 3) YYYYMMDD
            m = re.match(r"^(\d{4})(\d{2})(\d{2})", project_id)
            if m:
                iso = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
                return datetime.date.fromisoformat(iso)

            return None
        except Exception:
            return None

    def _extract_project_suffix(self, project_id: str) -> int:
        """Extrahiert numerisches Suffix am Ende ('-01', '-02', ...) als int; fehlt → 0."""
        m = re.search(r"-(\d+)$", project_id)
        if not m:
            return 0
        try:
            return int(m.group(1))
        except ValueError:
            return 0

    def _make_unique_project_id(self, kundenname: str, project_id: str) -> str:
        """
        Stellt sicher, dass die Projekt-ID innerhalb des Kunden-Ordners eindeutig ist.

        Existiert bereits ein Projekt mit derselben ID, wird ein Suffix "-01", "-02", ... angehängt.

        Args:
            kundenname: Kundenname
            project_id: vorgeschlagene Projekt-ID (z. B. "2025-08-11_Projekt_A")

        Returns:
            Eindeutige Projekt-ID (z. B. "2025-08-11_Projekt_A-01")
        """
        try:
            base_id = project_id
            unique_id = base_id
            counter = 1
            # Prüfe, ob der Projektpfad bereits existiert und erhöhe Suffix bis eindeutig
            while os.path.exists(self.get_projekt_pfad(kundenname, unique_id)):
                unique_id = f"{base_id}-{counter:02d}"
                counter += 1
            return unique_id
        except Exception:
            # Fail-safe: Im Zweifel ursprüngliche ID verwenden
            return project_id

    def kunden_ordner(self, kundenname: str) -> str:
        """Gibt den Pfad zum Kundenordner zurück"""
        safe_name = self._sanitize_name(kundenname)
        return os.path.join(self.base_dir, safe_name)

    def _normalize_name_for_match(self, value: str) -> str:
        """Einheitliche Normalform für Fuzzy-Matching und Vergleiche.

        Schritte:
        - Unicode NFC, lowercase
        - Ersetze Whitespaces zu "_"
        - Ersetze Bindestrich zu "_"
        - Entferne alle Nicht-Word-Zeichen außer "_" → ersetze zu "_"
        - Mehrfache "_" reduzieren, führende/abschließende "_" trimmen
        """
        try:
            s = unicodedata.normalize('NFC', str(value)).lower()
            s = re.sub(r'\s+', '_', s)
            s = s.replace('-', '_')
            s = re.sub(r'[^\w]', '_', s)
            s = re.sub(r'_+', '_', s)
            s = s.strip('_')
            return s
        except Exception:
            return str(value).lower().strip()

    def _normalize_for_compare_ascii(self, value: str) -> str:
        """Vergleichs-Normalform: NFKD → ASCII, für Suche/Fuzzy-Match.

        WICHTIG: Nur für Vergleiche verwenden, niemals für Dateinamen speichern.
        """
        try:
            # NFC erst, dann NFKD zerlegen und Diakritika entfernen (ASCII)
            s = unicodedata.normalize('NFC', str(value))
            s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')
            s = s.lower()
            s = re.sub(r'\s+', '_', s)
            s = s.replace('-', '_')
            s = re.sub(r'[^\w]', '_', s)
            s = re.sub(r'_+', '_', s)
            return s.strip('_')
        except Exception:
            return str(value).lower().strip()

    def erstelle_kundenstruktur(self, kundenname: str) -> str:
        """Erstellt die Basis-Kundenstruktur (nur der Hauptordner)"""
        safe_name = self._sanitize_name(kundenname)
        kundenpfad = self.kunden_ordner(safe_name)
        os.makedirs(kundenpfad, exist_ok=True)
        return kundenpfad

    def erstelle_projekt_ordner(self, kundenname: str, projektname: Optional[str] = None, datum: Optional[str] = None) -> Tuple[str, str]:
        """
        Erstellt einen neuen Projekt-Ordner für einen Kunden mit vollständiger Workflow-Struktur

        Args:
            kundenname: Name des Kunden
            projektname: Name des Projekts (optional)
            datum: Datum für das Projekt (optional, Standard: heute)

        Returns:
            Tuple: (projekt_pfad, projekt_id) - Pfad zum erstellten Projekt-Ordner und Projekt-ID
        """
        # Stelle sicher, dass der Kunde existiert (vor Lock, damit Pfad vorhanden ist)
        self.erstelle_kundenstruktur(kundenname)

        # Kritischer Abschnitt: eindeutige ID bestimmen und Ordner erstellen
        with self._customer_lock(kundenname, timeout=60):
            return self._create_project_locked(kundenname, projektname, datum)

    def _create_project_locked(self, kundenname: str, projektname: Optional[str] = None, datum: Optional[str] = None) -> Tuple[str, str]:
        """Interne Hilfsmethode: Projekt unter bereits gehaltenem Kunden-Lock erstellen."""
        # Generiere Projekt-ID und stelle Eindeutigkeit sicher (vermeidet Race-Condition bei Parallelzugriff)
        project_id = self._generate_project_id(projektname, datum)
        project_id = self._make_unique_project_id(kundenname, project_id)

        # Erstelle Projekt-Ordner und Unterordner atomar unter dem Lock
        safe_customer = self._sanitize_name(kundenname)
        projekt_pfad = os.path.join(self.kunden_ordner(safe_customer), project_id)
        # Root-Projektordner explizit anlegen (für spätere project_meta.json etc.)
        os.makedirs(projekt_pfad, exist_ok=True)

        for workflow in self.workflows:
                phys = self.workflow_folder_map.get(workflow, workflow)
                workflow_pfad = os.path.join(projekt_pfad, phys)
                os.makedirs(workflow_pfad, exist_ok=True)

        return projekt_pfad, project_id

    def get_projekt_pfad(self, kundenname: str, projekt_id: str) -> str:
        """Gibt den Pfad zu einem spezifischen Projekt zurück"""
        safe_customer = self._sanitize_name(kundenname)
        return os.path.join(self.kunden_ordner(safe_customer), projekt_id)

    def get_projekt_workflow_ordner(self, kundenname: str, projekt_id: str, workflow: str) -> str:
        """Gibt den Pfad zu einem Workflow-Ordner innerhalb eines Projekts zurück"""
        projekt_pfad = self.get_projekt_pfad(kundenname, projekt_id)
        phys = self.workflow_folder_map.get(workflow, workflow)
        # Falls Alt-Ordner (unnummeriert) existiert, bevorzuge diesen (Migration tolerant)
        alt_path = os.path.join(projekt_pfad, workflow)
        phys_path = os.path.join(projekt_pfad, phys)
        if os.path.isdir(alt_path) and not os.path.isdir(phys_path):
            return alt_path
        return phys_path

    def liste_kundenprojekte(self, kundenname: str) -> List[str]:
        """Listet alle Projekte eines Kunden auf"""
        safe_customer = self._sanitize_name(kundenname)
        kunden_pfad = self.kunden_ordner(safe_customer)

        if not os.path.exists(kunden_pfad):
            return []

        projekte: List[str] = []
        with os.scandir(kunden_pfad) as it:
            projekte = [e.name for e in it if e.is_dir()]

        # Sortiere nach parsed Datum (neueste zuerst), dann nach Suffix (höchstes zuerst), dann Name
        def sort_key(pid: str):
            d = self._parse_project_date(pid) or datetime.date.min
            suf = self._extract_project_suffix(pid)
            return (d.toordinal(), suf, pid.lower())

        projekte_sorted = sorted(projekte, key=sort_key, reverse=True)
        return projekte_sorted

    def get_neuestes_projekt(self, kundenname: str) -> Optional[str]:
        """Gibt das neueste Projekt eines Kunden zurück"""
        projekte = self.liste_kundenprojekte(kundenname)
        return projekte[0] if projekte else None

    def alle_kunden(self) -> List[str]:
        """Gibt alle Kunden zurück"""
        return [d for d in os.listdir(self.base_dir) if os.path.isdir(os.path.join(self.base_dir, d))]

    def fuzzy_kundenname_suche(self, kundenname: str, threshold: int = 70) -> Optional[str]:
        """Sucht den ähnlichsten Kundenordnernamen (fuzzy) und gibt ihn zurück"""
        kunden_liste = self.alle_kunden()
        if not kunden_liste:
            return None

        # Einheitliche Normalform verwenden
        # 1) Direkter exakter Check via sanitize + NFC (schneller Gleichheitstest)
        safe_input = self._sanitize_name(kundenname)
        if safe_input in kunden_liste:
            return safe_input

        # 2) Vergleichsnormalform (NFKD→ASCII) für robustes Fuzzy-Matching
        search_normalized = self._normalize_for_compare_ascii(kundenname)
        kunden_normalized = [self._normalize_for_compare_ascii(k) for k in kunden_liste]

        # Fuzzy-Matching auf normalisierten Strings; idx zurück auf Original mappen
        match, score, idx = process.extractOne(search_normalized, kunden_normalized, scorer=fuzz.WRatio)

        if score >= threshold:
            return kunden_liste[idx]  # Gib den ursprünglichen Kundennamen zurück
        return None

    def find_customer_fuzzy(self, search_name: str, threshold: int = 70) -> Optional[str]:
        """Alias für fuzzy_kundenname_suche für Rückwärtskompatibilität"""
        return self.fuzzy_kundenname_suche(search_name, threshold)

    def search_customers(self, query: str, limit: int = 8, min_score: int = 35) -> List[Dict[str, int]]:
        """
        Liefert eine Liste der besten fuzzy-Treffer für die Kundensuche.

        Args:
            query: Suchtext
            limit: maximale Anzahl an Treffern
            min_score: Mindestscore (0..100), darunter werden Treffer gefiltert

        Returns:
            Liste von Dicts: [{ 'name': str, 'score': int }]
        """
        try:
            kunden_liste = self.alle_kunden()
            if not query or not kunden_liste:
                return []

            # RapidFuzz mit Vergleichs-Normalform (NFKD→ASCII) verwenden
            from rapidfuzz import process, fuzz
            normalized_query = self._normalize_for_compare_ascii(query)
            normalized_choices = [self._normalize_for_compare_ascii(k) for k in kunden_liste]
            results = process.extract(normalized_query, normalized_choices, scorer=fuzz.WRatio, limit=limit)

            matches = []
            for _norm, score, idx in results:
                if score >= min_score:
                    matches.append({'name': kunden_liste[idx], 'score': int(score)})

            # Fallback: zeige zumindest die Top-Ergebnisse, wenn alle unter min_score sind
            if not matches and results:
                for _norm, score, idx in results[:limit]:
                    matches.append({'name': kunden_liste[idx], 'score': int(score)})

            return matches
        except Exception:
            # Fail-safe: Keine Ergebnisse bei Fehlern
            return []

    def customer_exists(self, kundenname: str) -> Tuple[bool, Optional[str], float]:
        """
        Prüft, ob ein Kunde bereits existiert (mit verbessertem Fuzzy Matching)

        Returns:
            tuple: (exists: bool, matched_customer: str or None, similarity_score: float)
        """
        try:
            existing_customers = self.alle_kunden()

            if not existing_customers:
                return False, None, 0.0

            # 0) Exakte Gleichheit mit NFC+Sanitize (Dateisystem-Realität)
            safe_input = self._sanitize_name(kundenname)
            # Case-insensitive Vermeidung von Kollisionen über Filesystem-Grenzen hinweg
            existing_map = {c.lower(): c for c in existing_customers}
            if safe_input in existing_customers:
                return True, safe_input, 100.0
            if safe_input.lower() in existing_map:
                return True, existing_map[safe_input.lower()], 100.0

            # Einheitliche Normalisierung
            search_norm = self._normalize_name_for_match(kundenname)
            existing_norm = [self._normalize_name_for_match(c) for c in existing_customers]

            # 1. Prüfe auf exakte Übereinstimmung in Normalform
            for i, norm in enumerate(existing_norm):
                if norm == search_norm:
                    return True, existing_customers[i], 100.0

            # 2. Prüfe auf exakte Übereinstimmung in Vergleichs-Normalform (NFKD→ASCII)
            search_cmp = self._normalize_for_compare_ascii(kundenname)
            existing_cmp = [self._normalize_for_compare_ascii(c) for c in existing_customers]
            for i, norm in enumerate(existing_cmp):
                if norm == search_cmp:
                    return True, existing_customers[i], 100.0

            # 3. Fuzzy-Matching für ähnliche Namen
            fuzzy_match = self.find_customer_fuzzy(kundenname, threshold=70)
            if fuzzy_match:
                # Berechne Similarity Score
                # Nutze Vergleichs-Normalform für Score, da robust gegenüber Diakritika
                search_for_score = self._normalize_for_compare_ascii(kundenname)
                match_for_score = self._normalize_for_compare_ascii(fuzzy_match)

                # Verwende rapidfuzz für genauen Score
                from rapidfuzz import fuzz
                score = fuzz.WRatio(search_for_score, match_for_score)

                return True, fuzzy_match, float(score)

            return False, None, 0.0

        except Exception as e:
            self.logger.error(f"Error in customer_exists: {e}")
            return False, None, 0.0

    def neuer_kunde(self, kundenname: str) -> bool:
        """Erstellt einen neuen Kunden"""
        try:
            # Prüfe ob Kunde bereits existiert (immer NFC+sanitize vor Vergleichen)
            safe = self._sanitize_name(kundenname)
            existing = {c.lower(): c for c in self.alle_kunden()}
            if safe in existing.values() or safe.lower() in existing:
                return False  # Kunde existiert bereits

            # Erstelle die Kundenstruktur
            kundenpfad = self.erstelle_kundenstruktur(safe)

            # Prüfe ob die Erstellung erfolgreich war
            return os.path.exists(kundenpfad)

        except Exception:
            return False

    # Rückwärtskompatibilität: Methoden für alte Struktur
    def neuer_anfrage_ordner(self, kundenname: str, workflow: str, projektname: Optional[str] = None) -> Optional[str]:
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

    def get_ordner_fuer_workflow(self, kundenname: str, workflow: str) -> str:
        """
        Rückwärtskompatibilität: Gibt den Workflow-Ordner für das neueste Projekt zurück
        """
        neuestes_projekt = self.get_neuestes_projekt(kundenname)
        if not neuestes_projekt:
            # Erstelle ein neues Projekt
            projekt_pfad, projekt_id = self.erstelle_projekt_ordner(kundenname)
            neuestes_projekt = projekt_id

        return self.get_projekt_workflow_ordner(kundenname, neuestes_projekt, workflow)

    def migrate_from_old_structure(self, kundenname: str) -> bool:
        """
        Migriert einen Kunden von der alten zur neuen Struktur
        """
        safe_customer = self._sanitize_name(kundenname)
        kunden_pfad = self.kunden_ordner(safe_customer)

        if not os.path.exists(kunden_pfad):
            return False

        with self._customer_lock(kundenname, timeout=120):
            # Prüfe ob bereits neue Struktur
            items = os.listdir(kunden_pfad)
            old_workflows = ["Angebot", "Pruefung", "Finalisierung", "Ausgangstexte"]

            # Wenn alte Workflow-Ordner direkt im Kundenordner existieren
            if any(item in old_workflows for item in items):
                # Erstelle ein Standard-Projekt für Migration (unter Lock, ohne erneutes Locking)
                migration_project_path, migration_project_id = self._create_project_locked(
                    kundenname,
                    "Migration_Projekt",
                    datetime.date.today().isoformat()
                )

                # Verschiebe alte Ordner in das neue Projekt – sicher:
                # - Zielordner nur löschen, wenn leer
                # - Falls belegt, nach "<Workflow>__alt" (mit Suffix) verschieben
                import shutil
                for workflow in old_workflows:
                    old_path = os.path.join(kunden_pfad, workflow)
                    if os.path.exists(old_path):
                        new_path = os.path.join(migration_project_path, workflow)
                        if os.path.exists(new_path):
                            try:
                                # Leeren Ordner entfernen, sonst nach __alt verschieben
                                if not os.listdir(new_path):
                                    os.rmdir(new_path)
                                else:
                                    alt_base = os.path.join(migration_project_path, f"{workflow}__alt")
                                    alt_path = alt_base
                                    counter = 1
                                    while os.path.exists(alt_path):
                                        alt_path = f"{alt_base}-{counter:02d}"
                                        counter += 1
                                    shutil.move(new_path, alt_path)
                            except Exception:
                                # Fail-safe: Ziel unangetastet lassen, Inhalte später mergen/nachziehen
                                pass
                        # Verschiebe alten Workflow-Ordner an Zielposition
                        shutil.move(old_path, new_path)

                return True

            return False

    # --- Nützliche Utilities -------------------------------------------------
    def rename_customer(self, old_name: str, new_name: str) -> bool:
        """Benennt einen Kundenordner sicher um (mit Locks, Sanitize, Kollisionscheck)."""
        try:
            safe_old = self._sanitize_name(old_name)
            safe_new = self._sanitize_name(new_name)

            existing = {c.lower(): c for c in self.alle_kunden()}
            if safe_old.lower() not in existing:
                return False
            # Kollision vermeiden (Case-insensitive, außer identisch)
            if safe_new.lower() in existing and existing[safe_new.lower()] != existing[safe_old.lower()]:
                return False

            # Quelle/Ziel-Pfade bestimmen
            src = self.kunden_ordner(safe_old)
            dst = self.kunden_ordner(safe_new)
            if os.path.abspath(src) == os.path.abspath(dst):
                return True  # nichts zu tun

            # Basisverzeichnis-Level Locks verwenden (nicht im Kundenordner selbst), damit Rename auf Windows möglich ist
            lock_names = sorted({safe_old, safe_new})
            lock_paths = [os.path.join(self.base_dir, f".rename-{name}.lock") for name in lock_names]

            if FileLock is not None:
                with contextlib.ExitStack() as stack:
                    for lp in lock_paths:
                        stack.enter_context(FileLock(lp, timeout=60))
                    # Nach Erwerb der Locks erneut prüfen
                    if not os.path.exists(src):
                        return False
                    if os.path.exists(dst) and os.path.abspath(dst) != os.path.abspath(src):
                        return False
                    os.makedirs(self.base_dir, exist_ok=True)
                    try:
                        os.replace(src, dst)
                    except Exception:
                        shutil.move(src, dst)
                    return True
            else:
                # Kein FileLock verfügbar – best effort ohne Cross-Process-Schutz
                if not os.path.exists(src):
                    return False
                if os.path.exists(dst) and os.path.abspath(dst) != os.path.abspath(src):
                    return False
                try:
                    os.replace(src, dst)
                except Exception:
                    shutil.move(src, dst)
                return True
        except Exception:
            return False

    def archive_project(self, kundenname: str, project_id: str) -> bool:
        """Archiviert ein Projekt in den Unterordner "__Archiv" des Kunden."""
        try:
            with self._customer_lock(kundenname, timeout=60):
                customer_path = self.kunden_ordner(self._sanitize_name(kundenname))
                project_path = self.get_projekt_pfad(kundenname, project_id)
                if not os.path.isdir(project_path):
                    return False
                archiv_root = os.path.join(customer_path, "__Archiv")
                os.makedirs(archiv_root, exist_ok=True)
                dest = os.path.join(archiv_root, project_id)
                # Kollisionen vermeiden
                counter = 1
                base_dest = dest
                while os.path.exists(dest):
                    dest = f"{base_dest}-{counter:02d}"
                    counter += 1
                shutil.move(project_path, dest)
                return True
        except Exception:
            return False

    def write_project_meta(self, kundenname: str, project_id: str, data: Dict[str, Any]) -> bool:
        """Schreibt project_meta.json in den Projektordner."""
        try:
            path = self.get_projekt_pfad(kundenname, project_id)
            os.makedirs(path, exist_ok=True)
            meta_path = os.path.join(path, "project_meta.json")
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    def read_project_meta(self, kundenname: str, project_id: str) -> Optional[Dict[str, Any]]:
        """Liest project_meta.json, falls vorhanden."""
        try:
            meta_path = os.path.join(self.get_projekt_pfad(kundenname, project_id), "project_meta.json")
            if not os.path.isfile(meta_path):
                return None
            with open(meta_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

# KUNDEN HINZUFÜGEN / ENTFERNEN
    def add_customer(self, customer_name: str) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """
        Fügt einen neuen Kunden hinzu und erstellt dessen Ordnerstruktur.
        
        Returns:
            (success: bool, message: str, similar_customers: List[Dict[str, Any]])
        """
        try:
            if not customer_name or not customer_name.strip():
                return False, "Bitte geben Sie einen Kundennamen ein", []
            
            # Bereinige den Kundennamen
            name = customer_name.strip()
            sanitized_name = self._sanitize_name(name)
            
            # Prüfe ob Kunde bereits existiert
            exists, matched_name, score = self.customer_exists(name)
            if exists:
                return False, f"Kunde '{name}' existiert bereits", []
            
            # Ähnliche Kunden suchen
            similar_customers = []
            kunden = self.alle_kunden()
            for kunde in kunden:
                score = fuzz.ratio(sanitized_name.lower(), kunde.lower())
                if score >= 80 and sanitized_name.lower() != kunde.lower():
                    similar_customers.append({
                        'name': kunde,
                        'score': score,
                        'reason': self._get_similarity_reason(sanitized_name, kunde, score)
                    })
            
            # Bei ähnlichen Kunden Warnung zurückgeben
            if similar_customers:
                return False, "Ähnlicher Kunde gefunden", similar_customers[:3]
            
            # Kundenordner anlegen
            try:
                kunden_pfad = self.erstelle_kundenstruktur(sanitized_name)
                self.logger.info(f"Kundenordner angelegt: {kunden_pfad}")
                return True, f"Kunde '{name}' erfolgreich hinzugefügt", []
            except Exception as e:
                self.logger.error(f"Fehler beim Anlegen des Kundenordners: {e}")
                return False, f"Fehler beim Anlegen des Kundenordners: {str(e)}", []
                
        except Exception as e:
            self.logger.error(f"Fehler beim Hinzufügen des Kunden: {e}")
            return False, f"Fehler beim Hinzufügen des Kunden: {str(e)}", []

    def _get_similarity_reason(self, new_name: str, existing_name: str, score: int) -> str:
        """Gibt den Grund für die Ähnlichkeit zurück"""
        if new_name.lower() == existing_name.lower():
            return "Exakte Übereinstimmung (unterschiedliche Groß-/Kleinschreibung)"
        elif existing_name.lower().startswith(new_name.lower()[:3]) or new_name.lower().startswith(existing_name.lower()[:3]):
            return "Ähnlicher Anfang"
        elif new_name.lower() in existing_name.lower() or existing_name.lower() in new_name.lower():
            return "Enthält Teilstring"
        elif score >= 85:
            return "Sehr ähnlich"
        else:
            return "Ähnlich"

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