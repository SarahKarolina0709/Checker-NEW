#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BERICHT HTML INTEGRATION ANALYSE
(Ehemals: html_integration_report.py)
Analysiert vorhandene HTML Templates & Integrations-Status.
"""
from pathlib import Path
import os

def analyse_html_integration():
    print("HTML INTEGRATION ANALYSE BERICHT")
    print("="*60)
    html_files = list(Path('.').glob('**/*.html'))
    print(f"Gefundene HTML Dateien: {len(html_files)}")
    templates = [
        'optimized_translator_report.html',
        'quality_analysis_report.html',
        'translation_comparison.html',
        'batch_analysis_report.html'
    ]
    for t in templates:
        exists = any(t in str(p) for p in html_files)
        print(f"  {'OK ' if exists else 'FEHLT'} {t}")
    gui_file = 'modern_translation_quality_gui.py'
    if os.path.exists(gui_file):
        with open(gui_file,'r',encoding='utf-8') as f:
            content = f.read()
        print("GUI Integrations-Prüfung:")
        checks = [
            ('def export_results', 'export_results Methode'),
            ('webbrowser', 'webbrowser Nutzung'),
            ('.html', 'HTML Zugriff im Code')
        ]
        for snip, label in checks:
            print(f"  {'OK ' if snip in content else 'FEHLT'} {label}")
    print("Empfehlungen: Browser-Integration, Template-Population, Multi-Format Export.")

if __name__ == '__main__':
    analyse_html_integration()
