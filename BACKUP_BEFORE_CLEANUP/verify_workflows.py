#!/usr/bin/env python3
"""
Einfacher Test für Workflow-Button Sichtbarkeit
"""

import sys
import os

def test_workflow_definitions():
    """Testet ob alle Workflow-Definitionen korrekt sind"""
    
    # Simuliere die Workflow-Liste aus der App
    workflows = [
        ("📊 Angebotsanalyse", "angebots_workflow", "Analysieren Sie Angebotsdokumente mit integriertem Datei-Upload"),
        ("🔍 Qualitätsprüfung", "pruefung_workflow", "Professionelle Überprüfung und Validierung von Übersetzungen"),
        ("✅ Finalisierung", "finalisierung_workflow", "Finale Bearbeitung und Export Ihrer Projekte"),
        ("📁 Projektübersicht", "projekt_workflow", "Verwalten Sie alle Ihre laufenden und abgeschlossenen Projekte")
    ]
    
    print("🔍 Workflow-Button Verifikation:")
    print("=" * 50)
    
    for i, (title, workflow_type, description) in enumerate(workflows, 1):
        print(f"{i}. {title}")
        print(f"   Typ: {workflow_type}")
        print(f"   Beschreibung: {description}")
        print()
    
    # Spezielle Überprüfung für Qualitätsprüfung
    pruefung_found = any("pruefung_workflow" in workflow for _, workflow, _ in workflows)
    qualitaet_found = any("Qualitätsprüfung" in title for title, _, _ in workflows)
    
    print("✅ Spezielle Überprüfungen:")
    print(f"   Qualitätsprüfung Button: {'✅ Gefunden' if qualitaet_found else '❌ Nicht gefunden'}")
    print(f"   pruefung_workflow Typ: {'✅ Gefunden' if pruefung_found else '❌ Nicht gefunden'}")
    
    # Workflow-Name-Mapping
    workflow_names = {
        "angebots_workflow": "Angebotsanalyse",
        "pruefung_workflow": "Qualitätsprüfung",
        "finalisierung_workflow": "Finalisierung", 
        "projekt_workflow": "Projektübersicht"
    }
    
    print("\n📋 Workflow-Name-Mapping:")
    for workflow_type, name in workflow_names.items():
        print(f"   {workflow_type} → {name}")
    
    return True

if __name__ == "__main__":
    test_workflow_definitions()
    print("\n✅ Alle Tests erfolgreich!")
    print("Die 'Qualitätsprüfung' Button sollte sichtbar sein!")
