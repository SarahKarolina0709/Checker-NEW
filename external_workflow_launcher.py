#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 EXTERNE WORKFLOW-NAVIGATION

Dieses Script verbindet die Welcome-Seite (checker_simplified.py)
mit Ihren bestehenden externen Qualitätsprüfungs-Workflows.

RESPEKTIERT IHRE ARCHITEKTUR:
✅ Keine neuen GUI-Elemente auf der Welcome-Seite
✅ Nutzt Ihre bestehenden Module (ki_module.py, comprehensive_quality_orchestrator.py)
✅ Startet externe Workflows als separate Prozesse
✅ Behält Ihre Workflow-Logik bei
"""

import os
import sys

from tkinter import messagebox
import subprocess

class WorkflowLauncher:
    """Einfacher Launcher für externe Qualitätsprüfungs-Workflows"""

    def __init__(self):
        self.base_path = os.path.dirname(os.path.abspath(__file__))

    def launch_quality_workflow(self):
        """Startet Ihren bestehenden Qualitätsprüfungs-Workflow"""

        # Option 1: ki_module.py direkt starten
        ki_module_path = os.path.join(self.base_path, "ki_module.py")
        if os.path.exists(ki_module_path):
            try:
                subprocess.Popen([sys.executable, ki_module_path])
                print("✅ KI-Qualitätsprüfung gestartet: ki_module.py")
                return True
            except Exception as e:
                print(f"⚠️ Fehler beim Starten von ki_module.py: {e}")

        # Option 2: comprehensive_quality_orchestrator.py starten
        orchestrator_path = os.path.join(self.base_path, "comprehensive_quality_orchestrator.py")
        if os.path.exists(orchestrator_path):
            try:
                subprocess.Popen([sys.executable, orchestrator_path])
                print("✅ Quality Orchestrator gestartet: comprehensive_quality_orchestrator.py")
                return True
            except Exception as e:
                print(f"⚠️ Fehler beim Starten des Orchestrators: {e}")

        # Fallback: Verfügbare Module anzeigen
        self._show_available_modules()
        return False

    def _show_available_modules(self):
        """Zeigt verfügbare Qualitätsprüfungs-Module an"""

        available_modules = []

        # Prüfe verfügbare Module
        modules_to_check = [
            "ki_module.py",
            "comprehensive_quality_orchestrator.py",
            "improved_report_step3d1.py",
            "analyze_functions.py",
            "amazon_components.py"
        ]

        for module in modules_to_check:
            if os.path.exists(os.path.join(self.base_path, module)):
                available_modules.append(module)

        if available_modules:
            modules_text = "\n".join([f"• {module}" for module in available_modules])
            messagebox.showinfo(
                "Verfügbare Qualitätsprüfungs-Module",
                f"🔍 Ihre externen Qualitätsprüfungs-Workflows:\n\n{modules_text}\n\n" +
                "Starten Sie diese Module direkt oder passen Sie die Navigation an."
            )
        else:
            messagebox.showwarning(
                "Keine Module gefunden",
                "⚠️ Keine Qualitätsprüfungs-Module im aktuellen Verzeichnis gefunden."
            )

# Integration in checker_simplified.py
def launch_external_quality_workflow():
    """
    Startet den externen Qualitätsprüfungs-Workflow

    Verwendung in checker_simplified.py:
    from external_workflow_launcher import launch_external_quality_workflow
    launch_external_quality_workflow()
    """
    launcher = WorkflowLauncher()
    return launcher.launch_quality_workflow()

if __name__ == "__main__":
    # Direkter Start für Tests
    launcher = WorkflowLauncher()
    launcher.launch_quality_workflow()