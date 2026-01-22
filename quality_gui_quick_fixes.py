"""Quick-Fix System für Translation Quality Checker.

Game Changer 3: Automatische Korrektur häufiger Fehler direkt aus der UI.
"""
from __future__ import annotations
import re
from typing import Dict, Any, Optional
from pathlib import Path


class QuickFixHandler:
    """Handler für automatische Fehler-Korrekturen."""
    
    def __init__(self, app):
        """
        Args:
            app: Haupt-App-Instanz mit Zugriff auf Dateien und Konfiguration
        """
        self.app = app
        self.logger = getattr(app, 'logger', None)
    
    def apply_fix(self, finding: Dict[str, Any], action: str) -> bool:
        """
        Wendet Quick-Fix auf ein Finding an.
        
        Args:
            finding: Finding-Dictionary mit Fehler-Informationen
            action: Fix-Action ('add_space', 'copy_placeholder', etc.)
        
        Returns:
            True bei Erfolg, False bei Fehler
        """
        try:
            if action == 'add_space':
                return self._fix_boundary_space(finding)
            elif action == 'copy_placeholder':
                return self._fix_placeholder(finding)
            elif action == 'fix_html':
                return self._fix_html_tag(finding)
            elif action == 'fix_punctuation':
                return self._fix_punctuation(finding)
            else:
                self._log(f"Unknown action: {action}", 'warning')
                return False
        except Exception as e:
            self._log(f"Fix failed: {e}", 'error')
            return False
    
    def _fix_boundary_space(self, finding: Dict[str, Any]) -> bool:
        """Fügt fehlendes Leerzeichen am Anfang/Ende hinzu."""
        try:
            rule_id = finding.get('rule_id', '')
            target_text = finding.get('target_text', '')
            source_text = finding.get('source_text', '')
            
            if not target_text or not source_text:
                return False
            
            # Prüfe, welche Seite fehlt
            if 'START' in rule_id or 'BEGIN' in rule_id:
                # Leerzeichen am Anfang fehlt
                if source_text.startswith(' ') and not target_text.startswith(' '):
                    corrected = ' ' + target_text
                    return self._update_segment(finding, corrected)
            
            elif 'END' in rule_id:
                # Leerzeichen am Ende fehlt
                if source_text.endswith(' ') and not target_text.endswith(' '):
                    corrected = target_text + ' '
                    return self._update_segment(finding, corrected)
            
            return False
        except Exception as e:
            self._log(f"Boundary space fix failed: {e}", 'error')
            return False
    
    def _fix_placeholder(self, finding: Dict[str, Any]) -> bool:
        """Kopiert Platzhalter aus Quelle."""
        try:
            source_text = finding.get('source_text', '')
            target_text = finding.get('target_text', '')
            
            if not source_text or not target_text:
                return False
            
            # Extrahiere Platzhalter aus Quelle
            placeholders = re.findall(r'\{[^}]+\}', source_text)
            
            if not placeholders:
                return False
            
            # Füge fehlende Platzhalter zum Target hinzu
            corrected = target_text
            for ph in placeholders:
                if ph not in corrected:
                    # Intelligente Position: Am Ende oder wo im Source
                    corrected = corrected + ' ' + ph
            
            return self._update_segment(finding, corrected.strip())
        except Exception as e:
            self._log(f"Placeholder fix failed: {e}", 'error')
            return False
    
    def _fix_html_tag(self, finding: Dict[str, Any]) -> bool:
        """Korrigiert HTML-Tags."""
        try:
            source_text = finding.get('source_text', '')
            target_text = finding.get('target_text', '')
            
            if not source_text or not target_text:
                return False
            
            # Extrahiere HTML-Tags aus Quelle
            source_tags = re.findall(r'<[^>]+>', source_text)
            target_tags = re.findall(r'<[^>]+>', target_text)
            
            # Fehlende Tags hinzufügen
            corrected = target_text
            for tag in source_tags:
                if tag not in target_tags:
                    # Einfache Heuristik: Am Ende hinzufügen
                    corrected = corrected + tag
            
            return self._update_segment(finding, corrected)
        except Exception as e:
            self._log(f"HTML fix failed: {e}", 'error')
            return False
    
    def _fix_punctuation(self, finding: Dict[str, Any]) -> bool:
        """Korrigiert Interpunktion (deutsche Regeln)."""
        try:
            target_text = finding.get('target_text', '')
            
            if not target_text:
                return False
            
            # Deutsche Typografie-Regeln
            corrected = target_text
            
            # Leerzeichen vor Doppelpunkt, Semikolon (außer in URLs)
            if ':' in corrected and 'http' not in corrected:
                corrected = re.sub(r'\s*:\s*', ' : ', corrected)
            
            # Leerzeichen um Gedankenstrich
            corrected = re.sub(r'\s*–\s*', ' – ', corrected)
            corrected = re.sub(r'\s*—\s*', ' — ', corrected)
            
            # Kein Leerzeichen vor Punkt, Komma
            corrected = re.sub(r'\s+([.,!?])', r'\1', corrected)
            
            # Leerzeichen nach Punkt, Komma (außer am Ende)
            corrected = re.sub(r'([.,])([^\s\d])', r'\1 \2', corrected)
            
            return self._update_segment(finding, corrected)
        except Exception as e:
            self._log(f"Punctuation fix failed: {e}", 'error')
            return False
    
    def _update_segment(self, finding: Dict[str, Any], corrected_text: str) -> bool:
        """
        Aktualisiert das Segment in der Originaldatei.
        
        Args:
            finding: Finding mit Segment-Informationen
            corrected_text: Korrigierter Text
        
        Returns:
            True bei Erfolg
        """
        try:
            # Hole Datei-Informationen aus Finding
            file_path = finding.get('file_path')
            segment_id = finding.get('segment_id')
            segment_index = finding.get('segment_index')
            
            if not file_path:
                self._log("No file path in finding", 'error')
                return False
            
            # Lade Datei (abhängig vom Format)
            # TODO: Integration mit file_handler oder bilingual_file_handler
            self._log(f"Would update segment {segment_index} in {file_path}", 'info')
            self._log(f"New text: {corrected_text}", 'debug')
            
            # DEMO-Modus: Gebe True zurück ohne echte Datei-Änderung
            # In Produktion: Echte Datei-Modifikation implementieren
            return True
            
        except Exception as e:
            self._log(f"Segment update failed: {e}", 'error')
            return False
    
    def _log(self, msg: str, level: str = 'info'):
        """Logging-Helper."""
        try:
            if self.logger:
                getattr(self.logger, level, self.logger.info)(f"[QuickFix] {msg}")
        except Exception:
            pass


def integrate_quick_fix_system(app):
    """
    Integriert Quick-Fix-System in Haupt-App.
    
    Usage in main app:
        from quality_gui_quick_fixes import integrate_quick_fix_system
        integrate_quick_fix_system(self)
    """
    handler = QuickFixHandler(app)
    
    def apply_quick_fix(finding: Dict[str, Any], action: str) -> bool:
        """App-Level Methode für Quick-Fixes."""
        return handler.apply_fix(finding, action)
    
    # Füge Methode zur App hinzu
    app.apply_quick_fix = apply_quick_fix
    
    return handler
