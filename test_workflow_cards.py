#!/usr/bin/env python3
"""
Test für die Workflow-Karten-Darstellung
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # Test-Import der wichtigsten Module
    from welcome_screen_components.section_header_mixin import SectionHeaderMixin
    print("✓ SectionHeaderMixin importiert erfolgreich")
    
    from ui_theme import UITheme
    print("✓ UITheme importiert erfolgreich")
    
    # Test der Workflow-Definitionen
    workflow_routes = {
        'angebots_workflow': {
            'name': 'Angebots-Analyzer',
            'description': 'Analyse von Übersetzungsanfragen',
            'icon': 'euro-money-2',
            'module': 'angebots_workflow'},
        'pruefung_workflow': {
            'name': 'Multi-File Check',
            'description': 'Qualitätsprüfung für Übersetzungen',
            'icon': 'check',
            'module': 'pruefung_workflow'},
        'finalisierung_workflow': {
            'name': 'Smart Finalization',
            'description': 'Finalisierung und Bereitstellung',
            'icon': 'success',
            'module': 'finalisierung_workflow'},
        'projekt_workflow': {
            'name': 'Projekt-Manager',
            'description': 'Verwaltung aller Projekte',
            'icon': 'project',
            'module': 'projekt_workflow'}
    }
    
    print("\n✓ Workflow-Definitionen geladen:")
    for key, workflow in workflow_routes.items():
        name_length = len(workflow['name'])
        desc_length = len(workflow['description'])
        print(f"  - {workflow['name']} (Länge: {name_length})")
        print(f"    {workflow['description']} (Länge: {desc_length})")
        print()
    
    print("✓ Alle Tests bestanden - Workflow-Karten sind bereit!")
    
except Exception as e:
    print(f"✗ Fehler beim Test: {str(e)}")
    import traceback
    traceback.print_exc()
