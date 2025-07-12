#!/usr/bin/env python3
"""
Minimaler Test für pruefung_workflow.py
"""
print("Teste Import der Klassen aus pruefung_workflow...")
from pruefung_workflow import PruefungWorkflow, ProcessingStage, ErrorSeverity, ErrorPattern, EnhancedProgressTracker, SmartErrorHandler, AIAnalysisEngine

print("Alle Klassen erfolgreich importiert!")

print("Prüfe PruefungWorkflow.__init__...")
import inspect
print(inspect.signature(PruefungWorkflow.__init__))

print("Test abgeschlossen!")
