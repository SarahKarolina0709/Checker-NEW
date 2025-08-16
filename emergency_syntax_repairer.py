#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚨 EMERGENCY SYNTAX REPAIR
==========================

Repariert kritische Syntax-Fehler nach manuellen Edits
und stellt minimale Funktionalität wieder her.
"""

import os
import re
from pathlib import Path

class EmergencySyntaxRepairer:
    """🚨 Emergency Syntax-Reparatur"""

    def __init__(self):
        self.repaired_files = []

    def repair_critical_syntax_errors(self):
        """🚨 Repariere kritische Syntax-Fehler"""
        print("🚨 EMERGENCY SYNTAX REPAIR GESTARTET!")

        # Liste der Dateien mit bekannten Problemen
        problem_files = [
            'modern_translation_quality_gui.py',
            'quality_gui_advanced_features.py',
            'quality_gui_main_app.py',
            'quality_gui_notifications.py',
            'quality_gui_progress_upload.py',
            'quality_gui_ui_components.py'
        ]

        for file_path in problem_files:
            if os.path.exists(file_path):
                print(f"🔧 Repariere: {file_path}")
                self._repair_file(file_path)

        print(f"\n✅ Emergency Syntax Repair abgeschlossen!")
        print(f"📁 Reparierte Dateien: {len(self.repaired_files)}")

        for file in self.repaired_files:
            print(f"   ✅ {file}")

    def _repair_file(self, file_path):
        """🔧 Repariere einzelne Datei"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # 1. Repariere fehlende Imports
            content = self._add_missing_imports(content, file_path)

            # 2. Repariere unvollständige try-blocks
            content = self._repair_try_blocks(content)

            # 3. Repariere Einrückungsfehler
            content = self._repair_indentation(content)

            # 4. Füge fehlende Fallback-Definitionen hinzu
            content = self._add_fallback_definitions(content, file_path)

            # Nur schreiben wenn Änderungen vorhanden
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                self.repaired_files.append(file_path)
                print(f"   ✅ {file_path} repariert")
            else:
                print(f"   ℹ️ {file_path} keine Änderungen erforderlich")

        except Exception as e:
            print(f"   ❌ Fehler bei {file_path}: {e}")

    def _add_missing_imports(self, content, file_path):
        """📦 Füge fehlende Imports hinzu"""

        # Standard-Imports die oft fehlen
        standard_imports = [
            "import logging",
            "import os",
            "import sys",
            "from pathlib import Path"
        ]

        # UI-Imports für GUI-Dateien
        if 'gui' in file_path or 'quality_gui' in file_path:
            ui_imports = [
                "try:",
                "    import customtkinter as ctk",
                "    import tkinter as tk",
                "    from tkinter import messagebox",
                "except ImportError:",
                "    print('⚠️ GUI-Module nicht verfügbar')",
                "    ctk = None",
                "",
                "# Logger Setup",
                "logger = logging.getLogger(__name__)",
                ""
            ]

            # Prüfe ob UI-Imports bereits vorhanden
            if "import customtkinter" not in content:
                # Füge nach den Docstrings ein
                lines = content.splitlines()
                insert_pos = 0

                # Finde Position nach Docstring
                in_docstring = False
                for i, line in enumerate(lines):
                    if line.strip().startswith('"""'):
                        if not in_docstring:
                            in_docstring = True
                        else:
                            insert_pos = i + 1
                            break
                    elif not in_docstring and line.strip() and not line.strip().startswith('#'):
                        insert_pos = i
                        break

                # Füge UI-Imports ein
                for j, import_line in enumerate(reversed(ui_imports)):
                    lines.insert(insert_pos, import_line)

                content = '\n'.join(lines)

        return content

    def _repair_try_blocks(self, content):
        """🔧 Repariere unvollständige try-blocks"""

        # Finde try-blocks ohne except/finally
        lines = content.splitlines()
        repaired_lines = []

        i = 0
        while i < len(lines):
            line = lines[i]

            if line.strip().startswith('try:'):
                # Finde das Ende des try-blocks
                try_indent = len(line) - len(line.lstrip())
                try_end = None

                # Suche nach except oder finally
                j = i + 1
                while j < len(lines):
                    next_line = lines[j]
                    if next_line.strip():
                        next_indent = len(next_line) - len(next_line.lstrip())

                        if (next_indent <= try_indent and
                            (next_line.strip().startswith('except') or
                             next_line.strip().startswith('finally') or
                             next_line.strip().startswith('class') or
                             next_line.strip().startswith('def'))):
                            try_end = j
                            break
                    j += 1

                repaired_lines.append(line)

                # Kopiere try-block Inhalt
                k = i + 1
                while k < len(lines) and (try_end is None or k < try_end):
                    repaired_lines.append(lines[k])
                    k += 1

                # Füge except hinzu wenn keiner gefunden
                if try_end is None or not lines[try_end].strip().startswith('except'):
                    except_line = ' ' * try_indent + 'except Exception as e:'
                    pass_line = ' ' * (try_indent + 4) + 'print(f"⚠️ Fehler: {e}")'
                    repaired_lines.append(except_line)
                    repaired_lines.append(pass_line)

                i = k
            else:
                repaired_lines.append(line)
                i += 1

        return '\n'.join(repaired_lines)

    def _repair_indentation(self, content):
        """🔧 Repariere Einrückungsfehler"""

        lines = content.splitlines()
        repaired_lines = []
        expected_indent = 0

        for line in lines:
            if not line.strip():  # Leere Zeilen
                repaired_lines.append(line)
                continue

            # Bestimme erwartete Einrückung basierend auf vorheriger Zeile
            if repaired_lines:
                prev_line = repaired_lines[-1].strip()
                if prev_line.endswith(':'):
                    expected_indent += 4
                elif line.strip().startswith(('except', 'finally', 'elif', 'else')):
                    expected_indent = max(0, expected_indent - 4)
                elif line.strip().startswith(('class', 'def')) and expected_indent > 0:
                    expected_indent = 0

            # Korrigiere Einrückung wenn nötig
            current_indent = len(line) - len(line.lstrip())
            if line.strip().startswith(('class', 'def', 'import', 'from')):
                # Top-level Deklarationen
                corrected_line = line.lstrip()
            else:
                # Verwende erwartete Einrückung
                corrected_line = ' ' * expected_indent + line.lstrip()

            repaired_lines.append(corrected_line)

        return '\n'.join(repaired_lines)

    def _add_fallback_definitions(self, content, file_path):
        """🔧 Füge Fallback-Definitionen hinzu"""

        fallback_definitions = []

        # UI-Theme Fallbacks für GUI-Dateien
        if 'gui' in file_path and 'UITheme' in content:
            fallback_definitions.extend([
                "",
                "# Fallback UI Theme Definitionen",
                "class UITheme:",
                "    @staticmethod",
                "    def get_color(color_name, fallback='#FFFFFF'):",
                "        color_map = {",
                "            'primary': '#2563EB',",
                "            'secondary': '#64748B',",
                "            'success': '#059669',",
                "            'warning': '#D97706',",
                "            'danger': '#DC2626',",
                "            'info': '#0284C7',",
                "            'text_primary': '#1F2937',",
                "            'background': '#FFFFFF',",
                "            'surface': '#F8FAFC'",
                "        }",
                "        return color_map.get(color_name, fallback)",
                "",
                "    @staticmethod",
                "    def get_font(font_name, fallback=('Arial', 12)):",
                "        return fallback",
                "",
                "    @staticmethod",
                "    def get_spacing(spacing_name, fallback=8):",
                "        return fallback",
                ""
            ])

        # Component Fallbacks
        if any(comp in content for comp in ['ModernProgressBar', 'EnhancedButton', 'ProfessionalCard']):
            fallback_definitions.extend([
                "",
                "# Fallback Component Definitionen",
                "class ModernProgressBar(ctk.CTkProgressBar):",
                "    def __init__(self, parent, **kwargs):",
                "        super().__init__(parent, **kwargs)",
                "",
                "class EnhancedButton(ctk.CTkButton):",
                "    def __init__(self, parent, **kwargs):",
                "        super().__init__(parent, **kwargs)",
                "    ",
                "    @classmethod",
                "    def create_secondary_button(cls, parent, text='Button', **kwargs):",
                "        return cls(parent, text=text, **kwargs)",
                "",
                "class ProfessionalCard(ctk.CTkFrame):",
                "    def __init__(self, parent, title='', icon=None, **kwargs):",
                "        super().__init__(parent, **kwargs)",
                "",
                "class ProfessionalButton(ctk.CTkButton):",
                "    def __init__(self, parent, **kwargs):",
                "        super().__init__(parent, **kwargs)",
                "",
                "class ProgressIndicator(ctk.CTkFrame):",
                "    def __init__(self, parent, **kwargs):",
                "        super().__init__(parent, **kwargs)",
                ""
            ])

        if fallback_definitions:
            # Füge Fallbacks am Ende der Datei hinzu
            content += '\n'.join(fallback_definitions)

        return content

if __name__ == "__main__":
    print("🚨 EMERGENCY SYNTAX REPAIR SYSTEM")
    print("=" * 40)

    repairer = EmergencySyntaxRepairer()
    repairer.repair_critical_syntax_errors()
