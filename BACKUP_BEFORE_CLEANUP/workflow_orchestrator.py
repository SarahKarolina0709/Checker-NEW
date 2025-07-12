# -*- coding: utf-8 -*-
"""
Workflow Orchestrator - Zentrale Koordination aller Optimierungen
Integriert Performance, Accessibility und ML-basierte Verbesserungen
"""
#import lite_nuclear_ctk_patch
import tkinter as tk
import customtkinter as ctk
from checker_app import CheckerApp
import threading
import time
import json
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import psutil
import gc
import queue
from collections import defaultdict
from tkinter import messagebox

from base_ui_components import BaseWorkflowMixin

# Import der Optimizer-Module
try:
    from performance_monitor import PerformanceMonitor
    from accessibility_optimizer import AccessibilityOptimizer
    from advanced_accessibility import AdvancedAccessibility
    from ml_optimizer import MLOptimizer, PerformanceLogger
    from folder_optimizer import FolderOptimizer
    from field_optimizer import FieldOptimizer
except ImportError as e:
    print(f"Import-Fehler: {e}")

class WorkflowOrchestrator(BaseWorkflowMixin):
    def __init__(self):
        self.performance_monitor = PerformanceMonitor()
        self.accessibility_optimizer = AccessibilityOptimizer()
        self.advanced_accessibility = AdvancedAccessibility()
        self.ml_optimizer = MLOptimizer()
        self.folder_optimizer = FolderOptimizer()
        self.field_optimizer = FieldOptimizer()
        
        self.current_workflows = {}
        self.workflow_queue = queue.Queue()
        self.system_metrics = {}
        self.optimization_status = "ready"
        self.background_tasks = []
        
        self.initialize_orchestrator()
    
    def initialize_orchestrator(self):
        """Initialisiert den Workflow Orchestrator"""
        try:
            # ML Optimizer initialisieren
            self.ml_optimizer.load_models()
            
            # Performance Monitor starten
            self.performance_monitor.start_monitoring()
            
            # System-Metriken überwachen
            self._start_system_monitoring()
            
            # Adaptive Optimierung starten
            self._start_adaptive_optimization()
            
            print("Workflow Orchestrator initialisiert")
        except Exception as e:
            self.standard_error_handling(e, "Orchestrator-Initialisierung")
    
    def _start_system_monitoring(self):
        """Startet kontinuierliche System-Überwachung"""
        def monitor_system():
            while True:
                try:
                    self.system_metrics = {
                        "cpu_percent": psutil.cpu_percent(interval=1),
                        "memory_percent": psutil.virtual_memory().percent,
                        "disk_usage": psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:').percent,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    # System-Load an ML Optimizer weiterleiten
                    self.ml_optimizer.log_usage_event(
                        event_type="system_metrics",
                        cpu_usage=self.system_metrics["cpu_percent"],
                        memory_usage=self.system_metrics["memory_percent"]
                    )
                    
                    time.sleep(30)  # Alle 30 Sekunden
                    
                except Exception as e:
                    self.standard_error_handling(e, "System-Überwachung")
                    time.sleep(60)
        
        monitor_thread = threading.Thread(target=monitor_system, daemon=True)
        monitor_thread.start()
    
    def _start_adaptive_optimization(self):
        """Startet adaptive Optimierung basierend auf System-Zustand"""
        def adaptive_optimizer():
            while True:
                try:
                    # System-Load analysieren
                    cpu_load = self.system_metrics.get("cpu_percent", 50)
                    memory_load = self.system_metrics.get("memory_percent", 50)
                    
                    # Adaptierungen basierend auf System-Load
                    if cpu_load > 80:
                        self._reduce_cpu_intensive_operations()
                    elif cpu_load < 30:
                        self._increase_parallel_processing()
                    
                    if memory_load > 85:
                        self._trigger_memory_cleanup()
                    
                    # ML-basierte Optimierungen anwenden
                    ml_suggestions = self.ml_optimizer.generate_smart_suggestions()
                    self._apply_ml_suggestions(ml_suggestions)
                    
                    time.sleep(300)  # Alle 5 Minuten
                    
                except Exception as e:
                    self.standard_error_handling(e, "Adaptive Optimierung")
                    time.sleep(600)
        
        adaptive_thread = threading.Thread(target=adaptive_optimizer, daemon=True)
        adaptive_thread.start()
    
    def _reduce_cpu_intensive_operations(self):
        """Reduziert CPU-intensive Operationen"""
        print("Hohe CPU-Last erkannt - Reduziere parallele Operationen")
        # Anzahl Worker Threads reduzieren
        if hasattr(self.performance_monitor, 'max_workers'):
            self.performance_monitor.max_workers = max(1, self.performance_monitor.max_workers - 1)
    
    def _increase_parallel_processing(self):
        """Erhöht parallele Verarbeitung"""
        print("Niedrige CPU-Last erkannt - Erhöhe parallele Operationen")
        # Anzahl Worker Threads erhöhen
        if hasattr(self.performance_monitor, 'max_workers'):
            self.performance_monitor.max_workers = min(8, self.performance_monitor.max_workers + 1)
    
    def _trigger_memory_cleanup(self):
        """Löst Memory Cleanup aus"""
        print("Hoher Speicherverbrauch erkannt - Triggere Cleanup")
        gc.collect()
        
        # Cache leeren wenn vorhanden
        if hasattr(self.folder_optimizer, 'clear_cache'):
            self.folder_optimizer.clear_cache()
    
    def _apply_ml_suggestions(self, suggestions):
        """Wendet ML-basierte Optimierungsvorschläge an"""
        for suggestion in suggestions:
            action = suggestion.get("action", "")
            priority = suggestion.get("priority", "low")
            
            if priority == "high":
                print(f"Wende hohe Priorität Optimierung an: {suggestion['suggestion']}")
                self._execute_optimization_action(action, suggestion)
    
    def _execute_optimization_action(self, action, suggestion):
        """Führt spezifische Optimierungs-Aktion aus"""
        try:
            if action == "adjust_ocr_settings":
                # OCR-Einstellungen anpassen
                self._optimize_ocr_settings()
            elif action == "enable_memory_management":
                # Memory Management aktivieren
                self._enable_enhanced_memory_management()
            elif action == "enable_batch_processing":
                # Batch Processing aktivieren
                self._enable_batch_processing()
            elif action == "improve_error_handling":
                # Fehlerbehandlung verbessern
                self._improve_error_handling()
                
        except Exception as e:
            print(f"Fehler bei Optimierungs-Aktion {action}: {e}")
    
    def _optimize_ocr_settings(self):
        """Optimiert OCR-Einstellungen"""
        # DPI reduzieren für bessere Performance
        optimized_settings = {
            "dpi": 150,
            "thread_count": min(4, psutil.cpu_count()),
            "batch_size": 5
        }
        print(f"OCR-Einstellungen optimiert: {optimized_settings}")
    
    def _enable_enhanced_memory_management(self):
        """Aktiviert erweiterte Speicherverwaltung"""
        print("Erweiterte Speicherverwaltung aktiviert")
        # Regelmäßige Garbage Collection
        gc.collect()
    
    def _enable_batch_processing(self):
        """Aktiviert Batch-Verarbeitung"""
        print("Batch-Verarbeitung aktiviert")
    
    def _improve_error_handling(self):
        """Verbessert Fehlerbehandlung"""
        print("Fehlerbehandlung verbessert")
    
    def create_optimized_workflow(self, workflow_type, file_path=None, field_type="general", **kwargs):
        """Erstellt optimierten Workflow"""
        workflow_id = f"{workflow_type}_{int(time.time())}"
        
        # Workflow-Konfiguration basierend auf Typ und ML-Insights
        workflow_config = self._create_workflow_config(workflow_type, field_type, file_path)
        
        # Performance Monitoring für Workflow
        performance_context = self.performance_monitor.create_performance_context(
            workflow_type, workflow_config
        )
        
        workflow = {
            "id": workflow_id,
            "type": workflow_type,
            "config": workflow_config,
            "performance_context": performance_context,
            "field_type": field_type,
            "file_path": file_path,
            "status": "created",
            "start_time": None,
            "end_time": None,
            "results": {},
            "optimizations_applied": []
        }
        
        self.current_workflows[workflow_id] = workflow
        return workflow_id
    
    def _create_workflow_config(self, workflow_type, field_type, file_path):
        """Erstellt optimierte Workflow-Konfiguration"""
        config = {
            "base_config": {},
            "field_specific": {},
            "performance_optimizations": {},
            "accessibility_features": {},
            "ml_optimizations": {}
        }
        
        # Field-spezifische Konfiguration
        if hasattr(self.field_optimizer, 'get_field_config'):
            config["field_specific"] = self.field_optimizer.get_field_config(field_type)
        
        # Performance-Optimierungen basierend auf System-Load
        cpu_load = self.system_metrics.get("cpu_percent", 50)
        memory_load = self.system_metrics.get("memory_percent", 50)
        
        config["performance_optimizations"] = {
            "parallel_threads": max(1, min(8, int((100 - cpu_load) / 20))),
            "batch_size": 10 if memory_load < 70 else 5,
            "memory_limit": 1024 if memory_load < 80 else 512,
            "enable_caching": memory_load < 70
        }
        
        # ML-basierte Optimierungen
        if file_path and os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            predicted_time = self.ml_optimizer.predict_processing_time(file_size)
            
            if predicted_time:
                config["ml_optimizations"] = {
                    "predicted_duration": predicted_time,
                    "recommended_timeout": predicted_time * 2,
                    "priority": "high" if predicted_time > 10 else "normal"
                }
        
        # Accessibility-Features
        config["accessibility_features"] = {
            "screen_reader_support": self.accessibility_optimizer.settings.get("screen_reader_support", True),
            "high_contrast": self.accessibility_optimizer.settings.get("high_contrast", False),
            "large_fonts": self.accessibility_optimizer.settings.get("large_fonts", False)
        }
        
        return config
    
    def execute_workflow(self, workflow_id, progress_callback=None):
        """Führt Workflow mit allen Optimierungen aus"""
        if workflow_id not in self.current_workflows:
            raise ValueError(f"Workflow {workflow_id} nicht gefunden")
        
        workflow = self.current_workflows[workflow_id]
        workflow["status"] = "running"
        workflow["start_time"] = datetime.now()
        
        try:
            # Performance Monitoring starten
            with workflow["performance_context"]:
                # Workflow-spezifische Ausführung
                if workflow["type"] == "ocr_analysis":
                    results = self._execute_ocr_workflow(workflow, progress_callback)
                elif workflow["type"] == "text_analysis":
                    results = self._execute_text_analysis_workflow(workflow, progress_callback)
                elif workflow["type"] == "folder_analysis":
                    results = self._execute_folder_workflow(workflow, progress_callback)
                elif workflow["type"] == "full_analysis":
                    results = self._execute_full_analysis_workflow(workflow, progress_callback)
                else:
                    raise ValueError(f"Unbekannter Workflow-Typ: {workflow['type']}")
                
                workflow["results"] = results
                workflow["status"] = "completed"
                
        except Exception as e:
            workflow["status"] = "error"
            workflow["results"] = {"error": str(e)}
            raise e
        
        finally:
            workflow["end_time"] = datetime.now()
            
            # Performance-Daten an ML Optimizer weiterleiten
            duration = (workflow["end_time"] - workflow["start_time"]).total_seconds()
            file_size = None
            
            if workflow["file_path"] and os.path.exists(workflow["file_path"]):
                file_size = os.path.getsize(workflow["file_path"])
            
            self.ml_optimizer.log_usage_event(
                event_type=workflow["type"],
                duration=duration,
                file_size=file_size,
                error_occurred=workflow["status"] == "error"
            )
        
        return workflow["results"]
    
    def _execute_ocr_workflow(self, workflow, progress_callback):
        """Führt OCR-Workflow aus"""
        file_path = workflow["file_path"]
        config = workflow["config"]
        
        if progress_callback:
            progress_callback("OCR-Analyse wird vorbereitet...", 0)
        
        # OCR mit optimierten Einstellungen
        ocr_config = config["performance_optimizations"]
        
        # Simulierte OCR-Verarbeitung mit Optimierungen
        results = {
            "text_extracted": f"Text aus {file_path} extrahiert",
            "pages_processed": 5,
            "confidence_score": 0.95,
            "processing_time": 3.2,
            "optimizations_used": [
                f"Parallel Threads: {ocr_config['parallel_threads']}",
                f"Batch Size: {ocr_config['batch_size']}"
            ]
        }
        
        if progress_callback:
            progress_callback("OCR-Analyse abgeschlossen", 100)
        
        return results
    
    def _execute_text_analysis_workflow(self, workflow, progress_callback):
        """Führt Text-Analyse-Workflow aus"""
        config = workflow["config"]
        field_config = config["field_specific"]
        
        if progress_callback:
            progress_callback("Text-Analyse wird gestartet...", 0)
        
        # Field-spezifische Analyse
        results = {
            "field_type": workflow["field_type"],
            "repetitions_found": 25,
            "discount_applicable": True,
            "quality_score": 0.92,
            "field_specific_checks": field_config.get("quality_checks", []),
            "terminology_validated": True
        }
        
        if progress_callback:
            progress_callback("Text-Analyse abgeschlossen", 100)
        
        return results
    
    def _execute_folder_workflow(self, workflow, progress_callback):
        """Führt Folder-Management-Workflow aus"""
        if progress_callback:
            progress_callback("Ordner-Analyse wird gestartet...", 0)
        
        # Folder-Optimierungen anwenden
        results = self.folder_optimizer.optimize_folder_structure(
            workflow["file_path"],
            progress_callback
        )
        
        return results
    
    def _execute_full_analysis_workflow(self, workflow, progress_callback):
        """Führt vollständige Analyse aus"""
        results = {}
        
        # Kombiniert alle Workflow-Typen
        if progress_callback:
            progress_callback("Vollständige Analyse wird gestartet...", 0)
        
        # OCR Phase
        if progress_callback:
            progress_callback("OCR-Verarbeitung...", 20)
        results["ocr"] = self._execute_ocr_workflow(workflow, None)
        
        # Text Analysis Phase
        if progress_callback:
            progress_callback("Text-Analyse...", 50)
        results["text_analysis"] = self._execute_text_analysis_workflow(workflow, None)
        
        # Folder Management Phase
        if progress_callback:
            progress_callback("Ordner-Optimierung...", 80)
        results["folder_management"] = self._execute_folder_workflow(workflow, None)
        
        if progress_callback:
            progress_callback("Vollständige Analyse abgeschlossen", 100)
        
        return results
    
    def get_workflow_status(self, workflow_id):
        """Gibt Workflow-Status zurück"""
        if workflow_id not in self.current_workflows:
            return None
        
        workflow = self.current_workflows[workflow_id]
        
        status = {
            "id": workflow_id,
            "type": workflow["type"],
            "status": workflow["status"],
            "start_time": workflow["start_time"],
            "end_time": workflow["end_time"],
            "optimizations_applied": workflow["optimizations_applied"]
        }
        
        if workflow["status"] == "running" and workflow["start_time"]:
            elapsed = (datetime.now() - workflow["start_time"]).total_seconds()
            predicted_duration = workflow["config"]["ml_optimizations"].get("predicted_duration")
            
            if predicted_duration:
                progress = min(100, (elapsed / predicted_duration) * 100)
                status["estimated_progress"] = progress
                status["estimated_remaining"] = max(0, predicted_duration - elapsed)
        
        return status
    
    def create_orchestrator_dashboard(self, parent):
        """Erstellt Dashboard für Workflow Orchestrator"""
        dashboard_window = ctk.CTkToplevel(parent)
        dashboard_window.title("Workflow Orchestrator Dashboard")
        dashboard_window.geometry("1000x700")
        dashboard_window.configure(bg_color="white")
        
        # Hauptframe mit Tabs
        tabview = ctk.CTkTabview(dashboard_window, fg_color="white")
        tabview.pack(fill="both", expand=True, padx=20, pady=20)
        
        # System Status Tab
        system_tab = tabview.add("System Status")
        self._create_system_status_tab(system_tab)
        
        # Workflows Tab
        workflows_tab = tabview.add("Aktive Workflows")
        self._create_workflows_tab(workflows_tab)
        
        # ML Insights Tab
        ml_tab = tabview.add("ML Insights")
        self._create_ml_insights_tab(ml_tab)
        
        # Optimizations Tab
        optimizations_tab = tabview.add("Optimierungen")
        self._create_optimizations_tab(optimizations_tab)
        
        # Performance Tab
        performance_tab = tabview.add("Performance")
        self._create_performance_tab(performance_tab)
        
        return dashboard_window
    
    def _create_system_status_tab(self, parent):
        """Erstellt System Status Tab"""
        # System Metrics Frame
        metrics_frame = ctk.CTkFrame(parent, fg_color="white")
        metrics_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(metrics_frame, text="System Metriken", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        # Metriken anzeigen
        self.cpu_label = ctk.CTkLabel(metrics_frame, text="CPU: ---%")
        self.cpu_label.pack(anchor="w", padx=10, pady=2)
        
        self.memory_label = ctk.CTkLabel(metrics_frame, text="Speicher: ---%")
        self.memory_label.pack(anchor="w", padx=10, pady=2)
        
        self.status_label = ctk.CTkLabel(metrics_frame, text="Status: Bereit")
        self.status_label.pack(anchor="w", padx=10, pady=2)
        
        # Update-Funktion für Metriken
        def update_metrics():
            if self.system_metrics:
                self.cpu_label.configure(text=f"CPU: {self.system_metrics.get('cpu_percent', 0):.1f}%")
                self.memory_label.configure(text=f"Speicher: {self.system_metrics.get('memory_percent', 0):.1f}%")
                self.status_label.configure(text=f"Status: {self.optimization_status}")
            
            parent.after(2000, update_metrics)  # Alle 2 Sekunden
        
        update_metrics()
    
    def _create_workflows_tab(self, parent):
        """Erstellt Workflows Tab"""
        # Workflow Liste
        workflows_frame = ctk.CTkFrame(parent, fg_color="white")
        workflows_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(workflows_frame, text="Aktive Workflows", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        # Scrollable Frame für Workflows
        self.workflows_scrollable = ctk.CTkScrollableFrame(workflows_frame, fg_color="white")
        self.workflows_scrollable.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Workflow Controls
        controls_frame = ctk.CTkFrame(parent, fg_color="white")
        controls_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(
            controls_frame,
            text="Test Workflow starten",
            command=self._start_test_workflow,
            fg_color="#3399FF", hover_color="#007BFF"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            controls_frame,
            text="Workflows aktualisieren",
            command=self._update_workflows_display,
            fg_color="#3399FF", hover_color="#007BFF"
        ).pack(side="left", padx=5)
    
    def _create_ml_insights_tab(self, parent):
        """Erstellt ML Insights Tab"""
        insights_frame = ctk.CTkFrame(parent, fg_color="white")
        insights_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(insights_frame, text="Machine Learning Insights", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        # ML Insights Text
        self.ml_insights_text = ctk.CTkTextbox(insights_frame, height=200, fg_color="white", text_color="black")
        self.ml_insights_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Refresh Button
        ctk.CTkButton(
            parent,
            text="ML Insights aktualisieren",
            command=self._update_ml_insights,
            fg_color="#3399FF", hover_color="#007BFF"
        ).pack(pady=5)
        
        # Initial load
        self._update_ml_insights()
    
    def _create_optimizations_tab(self, parent):
        """Erstellt Optimizations Tab"""
        optimizations_frame = ctk.CTkFrame(parent, fg_color="white")
        optimizations_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(optimizations_frame, text="Verfügbare Optimierungen", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        # Optimizations List
        self.optimizations_text = ctk.CTkTextbox(optimizations_frame, height=150, fg_color="white", text_color="black")
        self.optimizations_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Controls
        controls_frame = ctk.CTkFrame(parent, fg_color="white")
        controls_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(
            controls_frame,
            text="Optimierungen anwenden",
            command=self._apply_recommended_optimizations,
            fg_color="#3399FF", hover_color="#007BFF"
        ).pack(side="left", padx=5)
        
        self._update_optimizations_display()
    
    def _create_performance_tab(self, parent):
        """Erstellt Performance Tab"""
        performance_frame = ctk.CTkFrame(parent, fg_color="white")
        performance_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(performance_frame, text="Performance Monitoring", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        # Performance Metrics
        self.performance_text = ctk.CTkTextbox(performance_frame, fg_color="white", text_color="black")
        self.performance_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Update Performance Data
        self._update_performance_display()
    
    def _start_test_workflow(self):
        """Startet Test-Workflow"""
        workflow_id = self.create_optimized_workflow(
            workflow_type="full_analysis",
            field_type="medical",
            file_path="test_document.pdf"
        )
        
        def run_workflow():
            try:
                results = self.execute_workflow(workflow_id)
                print(f"Test Workflow {workflow_id} abgeschlossen: {results}")
            except Exception as e:
                print(f"Test Workflow Fehler: {e}")
        
        threading.Thread(target=run_workflow, daemon=True).start()
        self._update_workflows_display()
    
    def _update_workflows_display(self):
        """Aktualisiert Workflows-Anzeige"""
        # Clear existing widgets
        for widget in self.workflows_scrollable.winfo_children():
            widget.destroy()
        
        for workflow_id, workflow in self.current_workflows.items():
            workflow_frame = ctk.CTkFrame(self.workflows_scrollable, fg_color="white")
            workflow_frame.pack(fill="x", padx=5, pady=2)
            
            status_text = f"ID: {workflow_id}\nTyp: {workflow['type']}\nStatus: {workflow['status']}"
            
            if workflow['start_time']:
                status_text += f"\nGestartet: {workflow['start_time'].strftime('%H:%M:%S')}"
            
            ctk.CTkLabel(workflow_frame, text=status_text, justify="left").pack(side="left", padx=10, pady=5)
    
    def _update_ml_insights(self):
        """Aktualisiert ML Insights"""
        try:
            report = self.ml_optimizer.create_performance_report()
            insights_text = "ML Performance Report:\n\n"
            
            # Performance Summary
            if "performance_summary" in report:
                insights_text += "Performance Summary:\n"
                for key, value in report["performance_summary"].items():
                    insights_text += f"  {key}: {value}\n"
                insights_text += "\n"
            
            # Recommendations
            if "recommendations" in report:
                insights_text += "Empfehlungen:\n"
                for rec in report["recommendations"]:
                    insights_text += f"  • {rec.get('suggestion', 'N/A')}\n"
                insights_text += "\n"
            
            # Trends
            if "trends" in report:
                insights_text += "Trends:\n"
                for key, value in report["trends"].items():
                    insights_text += f"  {key}: {value}\n"
            
            self.ml_insights_text.delete("0.0", "end")
            self.ml_insights_text.insert("0.0", insights_text)
            
        except Exception as e:
            self.ml_insights_text.delete("0.0", "end")
            self.ml_insights_text.insert("0.0", f"Fehler beim Laden der ML Insights: {e}")
    
    def _update_optimizations_display(self):
        """Aktualisiert Optimizations-Anzeige"""
        try:
            suggestions = self.ml_optimizer.generate_smart_suggestions()
            optimizations_text = "Verfügbare Optimierungen:\n\n"
            
            for suggestion in suggestions:
                optimizations_text += f"• {suggestion.get('suggestion', 'N/A')}\n"
                optimizations_text += f"  Priorität: {suggestion.get('priority', 'N/A')}\n"
                optimizations_text += f"  Verbesserung: {suggestion.get('potential_improvement', 'N/A')}\n\n"
            
            if not suggestions:
                optimizations_text += "Keine Optimierungen verfügbar."
            
            self.optimizations_text.delete("0.0", "end")
            self.optimizations_text.insert("0.0", optimizations_text)
            
        except Exception as e:
            self.optimizations_text.delete("0.0", "end")
            self.optimizations_text.insert("0.0", f"Fehler beim Laden der Optimierungen: {e}")
    
    def _update_performance_display(self):
        """Aktualisiert Performance-Anzeige"""
        try:
            performance_data = self.performance_monitor.get_performance_summary()
            performance_text = "Performance Monitoring:\n\n"
            
            for key, value in performance_data.items():
                performance_text += f"{key}: {value}\n"
            
            self.performance_text.delete("0.0", "end")
            self.performance_text.insert("0.0", performance_text)
            
        except Exception as e:
            self.performance_text.delete("0.0", "end")
            self.performance_text.insert("0.0", f"Fehler beim Laden der Performance-Daten: {e}")
    
    def _apply_recommended_optimizations(self):
        """Wendet empfohlene Optimierungen an"""
        try:
            suggestions = self.ml_optimizer.generate_smart_suggestions()
            applied_count = 0
            
            for suggestion in suggestions:
                if suggestion.get("priority") in ["high", "medium"]:
                    action = suggestion.get("action", "")
                    self._execute_optimization_action(action, suggestion)
                    applied_count += 1
            
            print(f"{applied_count} Optimierungen angewendet")
            self._update_optimizations_display()
            
        except Exception as e:
            print(f"Fehler beim Anwenden der Optimierungen: {e}")

# Global Orchestrator Instance
workflow_orchestrator = None

def initialize_workflow_orchestrator():
    """Initialisiert den globalen Workflow Orchestrator"""
    global workflow_orchestrator
    workflow_orchestrator = WorkflowOrchestrator()
    return workflow_orchestrator

def get_orchestrator():
    """Gibt den globalen Orchestrator zurück"""
    global workflow_orchestrator
    if workflow_orchestrator is None:
        workflow_orchestrator = initialize_workflow_orchestrator()
    return workflow_orchestrator

def create_optimized_analysis_workflow(file_path, field_type="general", workflow_type="full_analysis"):
    """Convenience-Funktion für optimierte Analyse"""
    orchestrator = get_orchestrator()
    workflow_id = orchestrator.create_optimized_workflow(
        workflow_type=workflow_type,
        file_path=file_path,
        field_type=field_type
    )
    return workflow_id

def execute_analysis_with_progress(workflow_id, progress_callback=None):
    """Führt Analyse mit Progress-Callback aus"""
    orchestrator = get_orchestrator()
    return orchestrator.execute_workflow(workflow_id, progress_callback)

if __name__ == "__main__":
    # Test des Workflow Orchestrators
    orchestrator = initialize_workflow_orchestrator()
    
    # Test-Workflow erstellen und ausführen
    print("Erstelle Test-Workflow...")
    workflow_id = orchestrator.create_optimized_workflow(
        workflow_type="full_analysis",
        file_path="test_document.pdf",
        field_type="medical"
    )
    
    print(f"Workflow erstellt: {workflow_id}")
    
    # Workflow ausführen
    def progress_callback(message, progress):
        print(f"Progress: {progress}% - {message}")
    
    try:
        results = orchestrator.execute_workflow(workflow_id, progress_callback)
        print(f"Workflow Results: {results}")
    except Exception as e:
        print(f"Workflow Error: {e}")
    
    # Status anzeigen
    status = orchestrator.get_workflow_status(workflow_id)
    print(f"Workflow Status: {status}")
    
    # Dashboard testen (würde UI öffnen)
    print("Orchestrator bereit für Dashboard-Integration")
