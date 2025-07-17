#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test der Qualitätsprüfung-Integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Test der Imports
try:
    from core.workflows.pruefung_workflow import PruefungWorkflow
    print("✅ PruefungWorkflow erfolgreich importiert")
except ImportError as e:
    print(f"❌ Fehler beim Import von PruefungWorkflow: {e}")

try:
    from pruefung_workflow_controller import PruefungWorkflowController
    print("✅ PruefungWorkflowController erfolgreich importiert")
except ImportError as e:
    print(f"❌ Fehler beim Import von PruefungWorkflowController: {e}")

try:
    from ui_components.pruefung_workflow_view import PruefungWorkflowView
    print("✅ PruefungWorkflowView erfolgreich importiert")
except ImportError as e:
    print(f"❌ Fehler beim Import von PruefungWorkflowView: {e}")

print("\n📋 Test der Qualitätsprüfung-Integration abgeschlossen")
print("Die Integration sollte jetzt funktionieren!")
