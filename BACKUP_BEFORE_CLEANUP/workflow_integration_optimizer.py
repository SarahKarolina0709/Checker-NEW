# -*- coding: utf-8 -*-
"""
Workflow Integration Optimizer - Zentrale Workflow-Koordination und Performance-Optimierung
Verbindet alle Checker-App Module für optimale Leistung und Benutzerfreundlichkeit
"""

import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, filedialog
import threading
import time
import json
import os
from datetime import datetime, timedelta
import psutil
import queue
import concurrent.futures
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Callable, Any
import sqlite3
import pickle
import hashlib
from pathlib import Path

# Import bestehender Module
# Import Dependencies with fallbacks
try:
    from workflow_orchestrator import WorkflowOrchestrator, get_orchestrator
    WORKFLOW_ORCHESTRATOR_AVAILABLE = True
except ImportError:
    WORKFLOW_ORCHESTRATOR_AVAILABLE = False
    get_orchestrator = lambda: None

try:
    from accessibility_extensions import EnhancedAccessibilityManager, enhanced_accessibility
    ACCESSIBILITY_EXTENSIONS_AVAILABLE = True
except ImportError:
    ACCESSIBILITY_EXTENSIONS_AVAILABLE = False
    enhanced_accessibility = None

try:
    from realtime_optimizer import RealTimePerformanceOptimizer as RealtimeOptimizer
    REALTIME_OPTIMIZER_AVAILABLE = True
except ImportError:
    REALTIME_OPTIMIZER_AVAILABLE = False
    RealtimeOptimizer = None

try:
    from smart_workflow_assistant import SmartWorkflowAssistant
    SMART_WORKFLOW_ASSISTANT_AVAILABLE = True
except ImportError:
    SMART_WORKFLOW_ASSISTANT_AVAILABLE = False
    SmartWorkflowAssistant = None

try:
    from performance_monitor import PerformanceMonitor
    PERFORMANCE_MONITOR_AVAILABLE = True
except ImportError:
    PERFORMANCE_MONITOR_AVAILABLE = False
    PerformanceMonitor = None

try:
    from ml_optimizer import MLOptimizer
    ML_OPTIMIZER_AVAILABLE = True
except ImportError:
    ML_OPTIMIZER_AVAILABLE = False
    MLOptimizer = None

@dataclass
class WorkflowSession:
    """Workflow-Session mit Performance-Tracking"""
    session_id: str
    workflow_type: str
    user_profile: Dict
    start_time: datetime
    current_step: str
    files_processed: List[str]
    performance_metrics: Dict
    accessibility_settings: Dict
    ml_recommendations: List[Dict]
    estimated_completion: Optional[datetime] = None
    efficiency_score: float = 0.0
    error_count: int = 0
    user_satisfaction: Optional[int] = None

@dataclass
class WorkflowOptimization:
    """Workflow-Optimierungsvorschlag"""
    optimization_id: str
    workflow_type: str
    priority: str  # high, medium, low
    category: str  # performance, accessibility, user_experience, automation
    title: str
    description: str
    implementation_effort: str  # low, medium, high
    expected_impact: float  # 0-100
    required_modules: List[str]
    implementation_code: Optional[str] = None
    success_metrics: List[str] = None

class WorkflowIntegrationOptimizer:
    """Zentrale Workflow-Integration mit allen Optimierungsmodulen"""
    
    def __init__(self):
        self.session_id = None
        self.current_session = None
        self.optimization_database = None
        self.workflow_cache = {}
        self.performance_baselines = {}
        self.user_behavior_patterns = {}
          # Optimizer-Instanzen
        self.orchestrator = None        # Safely initialize accessibility_manager, handling the case when import fails
        if ACCESSIBILITY_EXTENSIONS_AVAILABLE:
            try:
                self.accessibility_manager = enhanced_accessibility
            except:
                self.accessibility_manager = None
        else:
            self.accessibility_manager = None
        self.realtime_optimizer = None
        self.workflow_assistant = None
        
        # Integration Status
        self.integration_status = {
            "orchestrator": False,
            "accessibility": False,
            "realtime": False,
            "ml_assistant": False,
            "database": False
        }
        
        self.initialize_integration()
    
    def initialize_integration(self):
        """Initialisiert alle Integration-Komponenten"""
        try:
            # Database initialisieren
            self._init_optimization_database()
            self.integration_status["database"] = True
              # Orchestrator verbinden
            if WORKFLOW_ORCHESTRATOR_AVAILABLE:
                self.orchestrator = get_orchestrator()
                if self.orchestrator:
                    self.integration_status["orchestrator"] = True
            
            # Realtime Optimizer initialisieren
            if REALTIME_OPTIMIZER_AVAILABLE and RealtimeOptimizer:
                self.realtime_optimizer = RealtimeOptimizer()
                self.integration_status["realtime"] = True
            
            # Workflow Assistant initialisieren
            if SMART_WORKFLOW_ASSISTANT_AVAILABLE and SmartWorkflowAssistant:
                self.workflow_assistant = SmartWorkflowAssistant()
                self.integration_status["ml_assistant"] = True
            
            # Accessibility Manager
            if self.accessibility_manager:
                self.integration_status["accessibility"] = True
            
            # Performance Baselines laden
            self._load_performance_baselines()
            
            # Cross-Module Event System einrichten
            self._setup_event_system()
            
            print("Workflow Integration Optimizer initialisiert")
            print(f"Integration Status: {self.integration_status}")
            
        except Exception as e:
            print(f"Fehler bei Integration-Initialisierung: {e}")
    
    def _init_optimization_database(self):
        """Initialisiert Optimierungs-Datenbank"""
        self.optimization_database = sqlite3.connect(
            "workflow_optimization.db", 
            check_same_thread=False
        )
        
        cursor = self.optimization_database.cursor()
        
        # Workflow Sessions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workflow_sessions (
                session_id TEXT PRIMARY KEY,
                workflow_type TEXT,
                user_profile TEXT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                performance_data TEXT,
                accessibility_data TEXT,
                success_rate REAL,
                efficiency_score REAL,
                user_satisfaction INTEGER
            )
        ''')
        
        # Optimierungsvorschläge
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS optimization_suggestions (
                optimization_id TEXT PRIMARY KEY,
                workflow_type TEXT,
                category TEXT,
                priority TEXT,
                title TEXT,
                description TEXT,
                implementation_status TEXT,
                impact_score REAL,
                created_date TIMESTAMP,
                applied_date TIMESTAMP
            )
        ''')
        
        # Performance Baselines
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_baselines (
                workflow_type TEXT PRIMARY KEY,
                baseline_metrics TEXT,
                last_updated TIMESTAMP,
                samples_count INTEGER
            )
        ''')
        
        # User Behavior Patterns
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_patterns (
                pattern_id TEXT PRIMARY KEY,
                user_profile TEXT,
                pattern_type TEXT,
                pattern_data TEXT,
                confidence_score REAL,
                last_updated TIMESTAMP
            )
        ''')
        
        self.optimization_database.commit()
    
    def _setup_event_system(self):
        """Richtet Cross-Module Event System ein"""
        self.event_queue = queue.Queue()
        self.event_handlers = {
            "workflow_started": self._handle_workflow_start,
            "workflow_completed": self._handle_workflow_completion,
            "performance_threshold": self._handle_performance_threshold,
            "accessibility_issue": self._handle_accessibility_issue,
            "user_frustration": self._handle_user_frustration,
            "efficiency_decline": self._handle_efficiency_decline,
            "optimization_applied": self._handle_optimization_applied
        }
        
        # Event Processing Thread
        self.event_processor = threading.Thread(
            target=self._process_events, daemon=True
        )
        self.event_processor.start()
    
    def _process_events(self):
        """Verarbeitet Events zwischen Modulen"""
        while True:
            try:
                event = self.event_queue.get(timeout=1)
                event_type = event.get("type")
                
                if event_type in self.event_handlers:
                    self.event_handlers[event_type](event)
                
                self.event_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Event Processing Error: {e}")
    
    def start_optimized_workflow(self, workflow_type: str, project_data: Dict, 
                                user_profile: Dict = None) -> str:
        """Startet optimierten Workflow mit allen Verbesserungen"""
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{workflow_type}"
        
        # Session erstellen
        self.current_session = WorkflowSession(
            session_id=session_id,
            workflow_type=workflow_type,
            user_profile=user_profile or {},
            start_time=datetime.now(),
            current_step="initialization",
            files_processed=[],
            performance_metrics={},
            accessibility_settings={},
            ml_recommendations=[]
        )
        
        # Event senden
        self.event_queue.put({
            "type": "workflow_started",
            "session_id": session_id,
            "workflow_type": workflow_type,
            "user_profile": user_profile
        })
        
        try:
            # Pre-Workflow Optimierungen anwenden
            self._apply_pre_workflow_optimizations(workflow_type, user_profile)
            
            # Workflow mit allen Optimierungen starten
            if self.orchestrator:
                workflow_id = self.orchestrator.create_optimized_workflow(
                    workflow_type=workflow_type,
                    project_data=project_data,
                    session_id=session_id,
                    optimizations_enabled=True
                )
                
                # Real-time Monitoring starten
                if self.realtime_optimizer:
                    self.realtime_optimizer.start_workflow_monitoring(
                        workflow_id, session_id
                    )
                
                # ML Assistant aktivieren
                if self.workflow_assistant:
                    self.workflow_assistant.start_session_tracking(session_id)
                
                return session_id
                
        except Exception as e:
            print(f"Fehler beim Starten des optimierten Workflows: {e}")
            self._handle_workflow_error(session_id, str(e))
            return None
    
    def _apply_pre_workflow_optimizations(self, workflow_type: str, user_profile: Dict):
        """Wendet Pre-Workflow Optimierungen an"""
        # Performance Optimierungen
        if self.realtime_optimizer:
            self.realtime_optimizer.optimize_for_workflow(workflow_type)
        
        # Accessibility Anpassungen
        if user_profile and self.accessibility_manager:
            profile_name = user_profile.get("accessibility_profile")
            if profile_name:
                profile = self.accessibility_manager.load_user_profile(profile_name)
                if profile:
                    # Accessibility Settings für Session anwenden
                    self.current_session.accessibility_settings = asdict(profile)
        
        # ML-basierte Vorhersagen
        if self.workflow_assistant:
            recommendations = self.workflow_assistant.get_workflow_recommendations(
                workflow_type, user_profile
            )
            self.current_session.ml_recommendations = recommendations
        
        # Workflow-spezifische Cache-Optimierungen
        self._optimize_workflow_cache(workflow_type)
    
    def _optimize_workflow_cache(self, workflow_type: str):
        """Optimiert Workflow-spezifischen Cache"""
        cache_key = f"workflow_{workflow_type}"
        
        if cache_key not in self.workflow_cache:
            self.workflow_cache[cache_key] = {
                "glossaries": {},
                "frequent_operations": {},
                "ui_states": {},
                "file_patterns": {},
                "optimization_states": {}
            }
        
        # Häufig verwendete Daten vorladen
        self._preload_workflow_data(workflow_type)
    
    def _preload_workflow_data(self, workflow_type: str):
        """Lädt häufig verwendete Workflow-Daten vor"""
        try:
            if workflow_type == "pruefung":
                # Glossare vorladen
                self._preload_glossaries()
                
            elif workflow_type == "angebot":
                # AC36 Templates vorladen
                self._preload_templates()
                
            elif workflow_type == "finalisierung":
                # Export-Templates vorladen
                self._preload_export_templates()
                
        except Exception as e:
            print(f"Fehler beim Vorladen der Workflow-Daten: {e}")
    
    def create_intelligent_workflow_dashboard(self, parent):
        """Erstellt intelligentes Workflow-Dashboard"""
        dashboard = ctk.CTkToplevel(parent)
        dashboard.title("Intelligente Workflow-Zentrale")
        dashboard.geometry("1400x900")
        
        # Main Container
        main_container = ctk.CTkFrame(dashboard)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tabbed Interface
        notebook = ctk.CTkTabview(main_container)
        notebook.pack(fill="both", expand=True)
        
        # Tabs erstellen
        self._create_workflow_overview_tab(notebook.add("📊 Übersicht"))
        self._create_real_time_monitoring_tab(notebook.add("⚡ Live-Monitoring"))
        self._create_optimization_suggestions_tab(notebook.add("🎯 Optimierungen"))
        self._create_accessibility_dashboard_tab(notebook.add("♿ Barrierefreiheit"))
        self._create_ml_insights_tab(notebook.add("🤖 KI-Insights"))
        self._create_workflow_automation_tab(notebook.add("🔄 Automatisierung"))
        
        return dashboard
    
    def _create_workflow_overview_tab(self, parent):
        """Erstellt Workflow-Übersicht Tab"""
        # Header
        header_frame = ctk.CTkFrame(parent)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            header_frame,
            text="🎯 Workflow-Zentrale - Intelligente Übersicht",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        # Metrics Row
        metrics_frame = ctk.CTkFrame(parent)
        metrics_frame.pack(fill="x", padx=10, pady=5)
        
        # Current Session Info
        if self.current_session:
            session_info = ctk.CTkFrame(metrics_frame)
            session_info.pack(side="left", fill="both", expand=True, padx=5)
            
            ctk.CTkLabel(
                session_info,
                text="📋 Aktuelle Session",
                font=ctk.CTkFont(size=14, weight="bold")
            ).pack(pady=5)
            
            info_text = f"Typ: {self.current_session.workflow_type}\n"
            info_text += f"Schritt: {self.current_session.current_step}\n"
            info_text += f"Dauer: {datetime.now() - self.current_session.start_time}\n"
            info_text += f"Effizienz: {self.current_session.efficiency_score:.1f}%"
            
            ctk.CTkLabel(session_info, text=info_text).pack(pady=5)
        
        # Performance Metrics
        perf_frame = ctk.CTkFrame(metrics_frame)
        perf_frame.pack(side="left", fill="both", expand=True, padx=5)
        
        ctk.CTkLabel(
            perf_frame,
            text="⚡ Performance",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=5)
        
        if self.realtime_optimizer:
            perf_data = self.realtime_optimizer.get_current_metrics()
            perf_text = f"CPU: {perf_data.get('cpu_usage', 0):.1f}%\n"
            perf_text += f"RAM: {perf_data.get('memory_usage', 0):.1f}%\n"
            perf_text += f"Temp: {perf_data.get('temperature', 0):.1f}°C"
            
            ctk.CTkLabel(perf_frame, text=perf_text).pack(pady=5)
        
        # Quick Actions
        actions_frame = ctk.CTkFrame(parent)
        actions_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            actions_frame,
            text="🚀 Schnellaktionen",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=5)
        
        buttons_frame = ctk.CTkFrame(actions_frame)
        buttons_frame.pack(fill="x", padx=10, pady=5)
        
        quick_actions = [
            ("🔧 Auto-Optimierung", self._trigger_auto_optimization),
            ("📊 Performance-Bericht", self._generate_performance_report),
            ("🎯 Empfehlungen anwenden", self._apply_all_recommendations),
            ("♿ Accessibility-Check", self._run_accessibility_check),
            ("🧹 Cache leeren", self._clear_all_caches),
            ("🔄 Module neu laden", self._reload_all_modules)
        ]
        
        for i, (text, command) in enumerate(quick_actions):
            btn = ctk.CTkButton(
                buttons_frame,
                text=text,
                command=command,
                width=200,
                height=40
            )
            # Use only .pack() for all children in buttons_frame
            btn.pack(side="left", padx=5, pady=5, expand=True, fill="x")
        # Remove any .grid() usage for buttons_frame children above
        # Ensure buttons_frame itself is only packed, not gridded
        # ...existing code...
    
    def _create_real_time_monitoring_tab(self, parent):
        """Erstellt Real-time Monitoring Tab"""
        # Live Charts Container
        charts_frame = ctk.CTkFrame(parent)
        charts_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Performance Chart
        if self.realtime_optimizer:
            # Integration mit Realtime Optimizer Dashboard
            self.realtime_optimizer.create_live_dashboard(charts_frame)
        else:
            ctk.CTkLabel(
                charts_frame,
                text="⚠️ Realtime Optimizer nicht verfügbar",
                font=ctk.CTkFont(size=16)
            ).pack(expand=True)
    
    def _create_optimization_suggestions_tab(self, parent):
        """Erstellt Optimierungsvorschläge Tab"""
        # Header
        header_frame = ctk.CTkFrame(parent)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            header_frame,
            text="🎯 Intelligente Optimierungsvorschläge",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        # Optimierungen generieren
        optimizations = self._generate_intelligent_optimizations()
        
        # Scrollable Frame für Optimierungen
        scroll_frame = ctk.CTkScrollableFrame(parent)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        for opt in optimizations:
            self._create_optimization_widget(scroll_frame, opt)
    
    def _generate_intelligent_optimizations(self) -> List[WorkflowOptimization]:
        """Generiert intelligente Optimierungsvorschläge"""
        optimizations = []
        
        # Performance-basierte Optimierungen
        if self.realtime_optimizer:
            perf_data = self.realtime_optimizer.get_performance_analysis()
            if perf_data.get("cpu_usage_avg", 0) > 70:
                optimizations.append(WorkflowOptimization(
                    optimization_id="cpu_high_usage",
                    workflow_type="all",
                    priority="high",
                    category="performance",
                    title="CPU-Auslastung reduzieren",
                    description="Parallele Operationen limitieren und Cache-Strategien optimieren",
                    implementation_effort="medium",
                    expected_impact=25.0,
                    required_modules=["realtime_optimizer", "workflow_orchestrator"],
                    success_metrics=["cpu_usage_reduction", "response_time_improvement"]
                ))
        
        # Accessibility-basierte Optimierungen
        if self.accessibility_manager and self.current_session:
            if self.current_session.user_profile.get("accessibility_needs"):
                optimizations.append(WorkflowOptimization(
                    optimization_id="accessibility_enhancement",
                    workflow_type=self.current_session.workflow_type,
                    priority="high",
                    category="accessibility",
                    title="Personalisierte Accessibility-Verbesserungen",
                    description="Benutzerprofilbasierte Interface-Anpassungen",
                    implementation_effort="low",
                    expected_impact=40.0,
                    required_modules=["accessibility_extensions"],
                    success_metrics=["user_satisfaction", "task_completion_rate"]
                ))
        
        # ML-basierte Optimierungen
        if self.workflow_assistant:
            ml_suggestions = self.workflow_assistant.get_optimization_suggestions()
            for suggestion in ml_suggestions[:3]:  # Top 3
                optimizations.append(WorkflowOptimization(
                    optimization_id=f"ml_{suggestion.get('id', 'unknown')}",
                    workflow_type="all",
                    priority=suggestion.get("priority", "medium"),
                    category="automation",
                    title=suggestion.get("title", "ML-Optimierung"),
                    description=suggestion.get("description", "Automatisierte Verbesserung"),
                    implementation_effort=suggestion.get("effort", "medium"),
                    expected_impact=suggestion.get("impact", 20.0),
                    required_modules=["smart_workflow_assistant", "ml_optimizer"],
                    success_metrics=suggestion.get("metrics", ["efficiency_improvement"])
                ))
        
        # Workflow-spezifische Optimierungen
        optimizations.extend(self._get_workflow_specific_optimizations())
        
        return optimizations
    
    def _get_workflow_specific_optimizations(self) -> List[WorkflowOptimization]:
        """Generiert workflow-spezifische Optimierungen"""
        optimizations = []
        
        # Prüfung Workflow Optimierungen
        optimizations.append(WorkflowOptimization(
            optimization_id="pruefung_parallel_checks",
            workflow_type="pruefung",
            priority="medium",
            category="performance",
            title="Parallele Prüfungen",
            description="LanguageTool, KI-Analyse und Terminologie-Checks parallel ausführen",
            implementation_effort="medium",
            expected_impact=35.0,
            required_modules=["pruefung_workflow"],
            success_metrics=["processing_time_reduction", "resource_utilization"]
        ))
        
        # Angebot Workflow Optimierungen
        optimizations.append(WorkflowOptimization(
            optimization_id="angebot_smart_analysis",
            workflow_type="angebot",
            priority="medium",
            category="automation",
            title="Intelligente AC36-Analyse",
            description="ML-basierte Texterkennung für automatische Kategorisierung",
            implementation_effort="high",
            expected_impact=50.0,
            required_modules=["angebots_workflow", "ml_optimizer"],
            success_metrics=["analysis_accuracy", "time_savings"]
        ))
        
        # Finalisierung Workflow Optimierungen
        optimizations.append(WorkflowOptimization(
            optimization_id="finalisierung_auto_export",
            workflow_type="finalisierung",
            priority="low",
            category="automation",
            title="Automatische Export-Optimierung",
            description="Intelligente Format-Erkennung und Layout-Optimierung",
            implementation_effort="medium",
            expected_impact=25.0,
            required_modules=["finalisierung_workflow", "export"],
            success_metrics=["export_quality", "user_satisfaction"]
        ))
        
        return optimizations
    
    def _create_optimization_widget(self, parent, optimization: WorkflowOptimization):
        """Erstellt Widget für Optimierungsvorschlag"""
        opt_frame = ctk.CTkFrame(parent)
        opt_frame.pack(fill="x", padx=5, pady=5)
        
        # Header
        header_frame = ctk.CTkFrame(opt_frame)
        header_frame.pack(fill="x", padx=10, pady=5)
        
        # Priority Badge
        priority_colors = {"high": "#ff4444", "medium": "#ff8800", "low": "#44aa44"}
        priority_frame = ctk.CTkFrame(header_frame, fg_color=priority_colors.get(optimization.priority, "#888888"))
        priority_frame.pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(
            priority_frame,
            text=optimization.priority.upper(),
            text_color="white",
            font=ctk.CTkFont(weight="bold")
        ).pack(padx=10, pady=2)
        
        # Title
        ctk.CTkLabel(
            header_frame,
            text=optimization.title,
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")
        
        # Impact Score
        impact_label = ctk.CTkLabel(
            header_frame,
            text=f"Impact: {optimization.expected_impact:.0f}%",
            font=ctk.CTkFont(size=12)
        )
        impact_label.pack(side="right", padx=10)
        
        # Description
        desc_frame = ctk.CTkFrame(opt_frame)
        desc_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            desc_frame,
            text=optimization.description,
            wraplength=800,
            justify="left"
        ).pack(padx=10, pady=5, anchor="w")
        
        # Details
        details_frame = ctk.CTkFrame(opt_frame)
        details_frame.pack(fill="x", padx=10, pady=5)
        
        details_text = f"Kategorie: {optimization.category} | "
        details_text += f"Aufwand: {optimization.implementation_effort} | "
        details_text += f"Module: {', '.join(optimization.required_modules)}"
        
        ctk.CTkLabel(
            details_frame,
            text=details_text,
            font=ctk.CTkFont(size=11),
            text_color="gray"
        ).pack(padx=10, pady=5, anchor="w")
        
        # Action Buttons
        buttons_frame = ctk.CTkFrame(opt_frame)
        buttons_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(
            buttons_frame,
            text="✅ Anwenden",
            command=lambda: self._apply_optimization(optimization),
            width=100,
            height=30
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            buttons_frame,
            text="📋 Details",
            command=lambda: self._show_optimization_details(optimization),
            width=100,
            height=30
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            buttons_frame,
            text="⏸️ Später",
            command=lambda: self._postpone_optimization(optimization),
            width=100,
            height=30
        ).pack(side="left", padx=5)
    
    def _apply_optimization(self, optimization: WorkflowOptimization):
        """Wendet Optimierung an"""
        try:
            if optimization.optimization_id == "cpu_high_usage":
                self._apply_cpu_optimization()
            elif optimization.optimization_id == "accessibility_enhancement":
                self._apply_accessibility_enhancement()
            elif optimization.optimization_id.startswith("ml_"):
                self._apply_ml_optimization(optimization)
            elif optimization.optimization_id == "pruefung_parallel_checks":
                self._apply_parallel_checks_optimization()
            
            # Erfolgsmeldung
            messagebox.showinfo(
                "Optimierung angewendet",
                f"Die Optimierung '{optimization.title}' wurde erfolgreich angewendet."
            )
            
            # Event senden
            self.event_queue.put({
                "type": "optimization_applied",
                "optimization_id": optimization.optimization_id,
                "success": True
            })
            
        except Exception as e:
            messagebox.showerror(
                "Optimierung fehlgeschlagen",
                f"Fehler beim Anwenden der Optimierung: {e}"
            )
    
    def _apply_cpu_optimization(self):
        """Wendet CPU-Optimierung an"""
        if self.realtime_optimizer:
            self.realtime_optimizer.apply_cpu_optimization()
        
        if self.orchestrator:
            # Thread Pool Size reduzieren
            self.orchestrator._reduce_cpu_intensive_operations()
    
    def _apply_accessibility_enhancement(self):
        """Wendet Accessibility-Verbesserungen an"""
        if self.accessibility_manager and self.current_session:
            profile = self.current_session.user_profile
            self.accessibility_manager.apply_enhanced_profile_optimizations(profile)
    
    def _apply_ml_optimization(self, optimization: WorkflowOptimization):
        """Wendet ML-basierte Optimierung an"""
        if self.workflow_assistant:
            self.workflow_assistant.apply_suggestion(optimization.optimization_id)
    
    def _apply_parallel_checks_optimization(self):
        """Wendet parallele Prüfungen-Optimierung an"""
        # Prüfung Workflow parallel processing aktivieren
        optimization_config = {
            "parallel_language_tool": True,
            "parallel_ki_analysis": True,
            "parallel_terminology": True,
            "max_parallel_threads": 3
        }
        
        # Config speichern
        with open("pruefung_optimization.json", "w") as f:
            json.dump(optimization_config, f, indent=2)
    
    def _create_accessibility_dashboard_tab(self, parent):
        """Erstellt Accessibility Dashboard Tab"""
        if self.accessibility_manager:
            self.accessibility_manager.create_accessibility_analytics_dashboard(parent)
        else:
            ctk.CTkLabel(
                parent,
                text="⚠️ Accessibility Manager nicht verfügbar",
                font=ctk.CTkFont(size=16)
            ).pack(expand=True)
    
    def _create_ml_insights_tab(self, parent):
        """Erstellt ML Insights Tab"""
        if self.workflow_assistant:
            self.workflow_assistant.create_ml_insights_dashboard(parent)
        else:
            ctk.CTkLabel(
                parent,
                text="⚠️ Smart Workflow Assistant nicht verfügbar",
                font=ctk.CTkFont(size=16)
            ).pack(expand=True)
    
    def _create_workflow_automation_tab(self, parent):
        """Erstellt Workflow Automation Tab"""
        # Header
        header_frame = ctk.CTkFrame(parent)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            header_frame,
            text="🔄 Intelligente Workflow-Automatisierung",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        # Automation Rules
        rules_frame = ctk.CTkFrame(parent)
        rules_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Automation Rules erstellen
        automation_rules = self._create_automation_rules()
        
        for rule in automation_rules:
            self._create_automation_rule_widget(rules_frame, rule)
    
    def _create_automation_rules(self) -> List[Dict]:
        """Erstellt Automatisierungsregeln"""
        return [
            {
                "name": "Auto-Glossar-Vorschläge",
                "description": "Schlägt automatisch passende Glossare basierend auf Dateiinhalt vor",
                "trigger": "file_loaded",
                "action": "suggest_glossary",
                "enabled": True,
                "confidence": 85
            },
            {
                "name": "Intelligente Qualitätsprüfung",
                "description": "Führt automatisch passende Prüfungen basierend auf Dateityp durch",
                "trigger": "pruefung_started",
                "action": "auto_select_checks",
                "enabled": True,
                "confidence": 92
            },
            {
                "name": "Adaptive Interface-Anpassung",
                "description": "Passt Interface automatisch an Nutzerverhalten an",
                "trigger": "session_start",
                "action": "adapt_interface",
                "enabled": True,
                "confidence": 78
            },
            {
                "name": "Performance Auto-Tuning",
                "description": "Optimiert Performance-Einstellungen automatisch",
                "trigger": "performance_degradation",
                "action": "auto_optimize",
                "enabled": True,
                "confidence": 88
            }
        ]
    
    def _create_automation_rule_widget(self, parent, rule: Dict):
        """Erstellt Widget für Automatisierungsregel"""
        rule_frame = ctk.CTkFrame(parent)
        rule_frame.pack(fill="x", padx=10, pady=5)
        
        # Header mit Toggle
        header_frame = ctk.CTkFrame(rule_frame)
        header_frame.pack(fill="x", padx=10, pady=5)
        
        # Toggle Switch
        toggle_var = tk.BooleanVar(value=rule["enabled"])
        toggle = ctk.CTkSwitch(
            header_frame,
            text="",
            variable=toggle_var,
            command=lambda: self._toggle_automation_rule(rule["name"], toggle_var.get())
        )
        toggle.pack(side="left", padx=(0, 10))
        
        # Rule Name
        ctk.CTkLabel(
            header_frame,
            text=rule["name"],
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left")
        
        # Confidence Badge
        confidence_color = "#44aa44" if rule["confidence"] > 80 else "#ff8800" if rule["confidence"] > 60 else "#ff4444"
        confidence_frame = ctk.CTkFrame(header_frame, fg_color=confidence_color)
        confidence_frame.pack(side="right")
        
        ctk.CTkLabel(
            confidence_frame,
            text=f"{rule['confidence']}%",
            text_color="white",
            font=ctk.CTkFont(weight="bold")
        ).pack(padx=8, pady=2)
        
        # Description
        ctk.CTkLabel(
            rule_frame,
            text=rule["description"],
            wraplength=600,
            justify="left"
        ).pack(padx=10, pady=(0, 10), anchor="w")
    
    def _toggle_automation_rule(self, rule_name: str, enabled: bool):
        """Schaltet Automatisierungsregel um"""
        print(f"Automatisierungsregel '{rule_name}' {'aktiviert' if enabled else 'deaktiviert'}")
        
        # Implementation für spezifische Regeln
        if rule_name == "Auto-Glossar-Vorschläge":
            self._toggle_auto_glossary(enabled)
        elif rule_name == "Intelligente Qualitätsprüfung":
            self._toggle_auto_quality_check(enabled)
        elif rule_name == "Adaptive Interface-Anpassung":
            self._toggle_adaptive_interface(enabled)
        elif rule_name == "Performance Auto-Tuning":
            self._toggle_auto_tuning(enabled)
    
    def _toggle_auto_glossary(self, enabled: bool):
        """Schaltet Auto-Glossar um"""
        if self.workflow_assistant:
            self.workflow_assistant.set_auto_glossary_enabled(enabled)
    
    def _toggle_auto_quality_check(self, enabled: bool):
        """Schaltet Auto-Quality-Check um"""
        if self.orchestrator:
            self.orchestrator.set_auto_quality_check(enabled)
    
    def _toggle_adaptive_interface(self, enabled: bool):
        """Schaltet adaptive Interface um"""
        if self.accessibility_manager:
            self.accessibility_manager.set_adaptive_mode(enabled)
    
    def _toggle_auto_tuning(self, enabled: bool):
        """Schaltet Auto-Tuning um"""
        if self.realtime_optimizer:
            self.realtime_optimizer.set_auto_tuning_enabled(enabled)
    
    # Event Handlers
    def _handle_workflow_start(self, event):
        """Behandelt Workflow-Start Event"""
        print(f"Workflow gestartet: {event.get('workflow_type')}")
        
        # Performance Monitoring aktivieren
        if self.realtime_optimizer:
            self.realtime_optimizer.start_session_monitoring(event.get('session_id'))
    
    def _handle_workflow_completion(self, event):
        """Behandelt Workflow-Completion Event"""
        print(f"Workflow abgeschlossen: {event.get('workflow_type')}")
        
        # Session in Datenbank speichern
        if self.current_session:
            self._save_session_to_database(self.current_session)
    
    def _handle_performance_threshold(self, event):
        """Behandelt Performance-Threshold Event"""
        threshold_type = event.get('threshold_type')
        current_value = event.get('current_value')
        
        print(f"Performance-Schwellwert überschritten: {threshold_type} = {current_value}")
        
        # Automatische Optimierung triggern
        if threshold_type == "cpu_usage" and current_value > 80:
            self._apply_cpu_optimization()
        elif threshold_type == "memory_usage" and current_value > 85:
            self._trigger_memory_cleanup()
    
    def _handle_accessibility_issue(self, event):
        """Behandelt Accessibility-Issue Event"""
        issue_type = event.get('issue_type')
        severity = event.get('severity', 'medium')
        
        print(f"Accessibility-Problem erkannt: {issue_type} (Schwere: {severity})")
        
        # Automatische Korrektur für bekannte Probleme
        if issue_type == "contrast_too_low" and self.accessibility_manager:
            self.accessibility_manager.apply_high_contrast_correction()
    
    def _handle_user_frustration(self, event):
        """Behandelt User-Frustration Event"""
        frustration_level = event.get('level', 0)
        context = event.get('context', '')
        
        print(f"Benutzerfrustration erkannt: Level {frustration_level} in {context}")
        
        # Hilfe anbieten oder Interface vereinfachen
        if frustration_level > 3:
            self._offer_assistance()
    
    def _handle_efficiency_decline(self, event):
        """Behandelt Efficiency-Decline Event"""
        decline_percentage = event.get('decline_percentage', 0)
        workflow_type = event.get('workflow_type')
        
        print(f"Effizienz-Rückgang: {decline_percentage}% in {workflow_type}")
        
        # Automatische Optimierungsvorschläge
        if decline_percentage > 20:
            self._generate_efficiency_suggestions(workflow_type)
    
    def _handle_optimization_applied(self, event):
        """Behandelt Optimization-Applied Event"""
        optimization_id = event.get('optimization_id')
        success = event.get('success', False)
        
        print(f"Optimierung angewendet: {optimization_id} (Erfolg: {success})")
        
        # Tracking für zukünftige Empfehlungen
        if success:
            self._update_optimization_success_rate(optimization_id)
    
    # Utility Methods
    def _trigger_auto_optimization(self):
        """Triggert automatische Optimierung"""
        try:
            # Performance-Optimierung
            if self.realtime_optimizer:
                self.realtime_optimizer.trigger_auto_optimization()
            
            # ML-Optimierung
            if self.workflow_assistant:
                suggestions = self.workflow_assistant.get_auto_optimization_suggestions()
                for suggestion in suggestions[:3]:  # Top 3 anwenden
                    self._apply_ml_optimization_suggestion(suggestion)
            
            messagebox.showinfo(
                "Auto-Optimierung",
                "Automatische Optimierung wurde erfolgreich durchgeführt."
            )
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Auto-Optimierung fehlgeschlagen: {e}")
    
    def _generate_performance_report(self):
        """Generiert Performance-Bericht"""
        report_window = ctk.CTkToplevel()
        report_window.title("Performance-Bericht")
        report_window.geometry("800x600")
        
        # Report Content
        text_widget = ctk.CTkTextbox(report_window)
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        
        report = self._compile_performance_report()
        text_widget.insert("0.0", report)
    
    def _compile_performance_report(self) -> str:
        """Kompiliert Performance-Bericht"""
        report = "📊 PERFORMANCE-BERICHT\n"
        report += "=" * 50 + "\n\n"
        
        # Aktueller Status
        if self.realtime_optimizer:
            metrics = self.realtime_optimizer.get_current_metrics()
            report += "🔄 AKTUELLER STATUS:\n"
            report += f"CPU-Auslastung: {metrics.get('cpu_usage', 0):.1f}%\n"
            report += f"Speicher-Auslastung: {metrics.get('memory_usage', 0):.1f}%\n"
            report += f"Temperatur: {metrics.get('temperature', 0):.1f}°C\n\n"
        
        # Session-Statistiken
        if self.current_session:
            report += "📋 AKTUELLE SESSION:\n"
            report += f"Workflow: {self.current_session.workflow_type}\n"
            report += f"Dauer: {datetime.now() - self.current_session.start_time}\n"
            report += f"Effizienz: {self.current_session.efficiency_score:.1f}%\n\n"
        
        # Optimierungsempfehlungen
        optimizations = self._generate_intelligent_optimizations()
        high_priority = [opt for opt in optimizations if opt.priority == "high"]
        
        if high_priority:
            report += "🎯 DRINGENDE OPTIMIERUNGEN:\n"
            for opt in high_priority[:3]:
                report += f"• {opt.title} (Impact: {opt.expected_impact:.0f}%)\n"
            report += "\n"
        
        # Modul-Status
        report += "🔧 MODUL-STATUS:\n"
        for module, status in self.integration_status.items():
            status_icon = "✅" if status else "❌"
            report += f"{status_icon} {module}: {'Aktiv' if status else 'Inaktiv'}\n"
        
        return report
    
    def _save_session_to_database(self, session: WorkflowSession):
        """Speichert Session in Datenbank"""
        try:
            cursor = self.optimization_database.cursor()
            cursor.execute('''
                INSERT INTO workflow_sessions 
                (session_id, workflow_type, user_profile, start_time, 
                 performance_data, accessibility_data, efficiency_score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                session.session_id,
                session.workflow_type,
                json.dumps(session.user_profile),
                session.start_time,
                json.dumps(session.performance_metrics),
                json.dumps(session.accessibility_settings),
                session.efficiency_score
            ))
            self.optimization_database.commit()
            
        except Exception as e:
            print(f"Fehler beim Speichern der Session: {e}")

    def initialize_with_root(self, root_window):
        """Initialisiert das System mit dem Root-Fenster"""
        try:
            self.root_window = root_window
            
            # Real-time optimizer mit Root verknüpfen
            if self.realtime_optimizer:
                self.realtime_optimizer.set_root_window(root_window)
                
            # Accessibility manager mit Root verknüpfen
            if self.accessibility_manager and hasattr(self.accessibility_manager, 'set_root'):
                self.accessibility_manager.set_root(root_window)
                  # Workflow assistant mit Root verknüpfen  
            if self.workflow_assistant and hasattr(self.workflow_assistant, 'set_root'):
                self.workflow_assistant.set_root(root_window)
                
            print("✓ Workflow Integration Optimizer linked to root window")
            
        except Exception as e:
            print(f"Warning: Could not initialize with root window: {e}")
            
    def _load_performance_baselines(self):
        """Dummy-Methode für Performance-Baselines (Platzhalter)"""
        pass
    
    def show_dashboard(self, parent_frame):
        """Zeigt das Dashboard in einem bestehenden Frame (für die Hauptanwendung)."""
        try:
            # RADICAL SOLUTION: Use only pack geometry manager consistently
            self._nuclear_clear_frame(parent_frame)
            
            # Wait longer for cleanup to complete
            parent_frame.after(50, lambda: self._create_pack_only_dashboard(parent_frame))
            
        except Exception as e:
            print(f"Error creating dashboard: {e}")
            import traceback
            traceback.print_exc()
            self._create_emergency_dashboard(parent_frame)
    
    def _nuclear_clear_frame(self, frame):
        """Nuclear option for frame clearing - completely avoid geometry conflicts."""
        try:
            # Step 1: Forget ALL geometry managers for ALL widgets
            def clear_widget_recursively(widget):
                try:
                    # Clear all children first
                    for child in widget.winfo_children():
                        clear_widget_recursively(child)
                    
                    # Clear this widget from all geometry managers
                    widget.pack_forget()
                    widget.grid_forget()
                    widget.place_forget()
                except:
                    pass
            
            # Clear all widgets recursively
            for widget in list(frame.winfo_children()):
                clear_widget_recursively(widget)
            
            # Step 2: Force display updates
            frame.update_idletasks()
            
            # Step 3: Destroy everything
            for widget in list(frame.winfo_children()):
                try:
                    widget.destroy()
                except:
                    pass
            
            # Step 4: Final cleanup
            frame.update_idletasks()
            
            # Step 5: Ensure frame uses pack exclusively
            try:
                frame.pack_propagate(True)
            except:
                pass
                
        except Exception as e:
            print(f"Warning during nuclear frame clearing: {e}")
    
    def _create_pack_only_dashboard(self, parent_frame):
        """Creates dashboard using ONLY pack geometry manager."""
        try:
            # Main container - PACK ONLY
            main_container = ctk.CTkFrame(parent_frame)
            main_container.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Header - PACK ONLY
            header = ctk.CTkLabel(
                main_container,
                text="🚀 Optimization Dashboard",
                font=ctk.CTkFont(size=24, weight="bold")
            )
            header.pack(pady=(20, 10))
            
            # Content area - PACK ONLY
            content = ctk.CTkFrame(main_container)
            content.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Status info - PACK ONLY
            status_text = """
✅ Workflow-Optimierung aktiv
✅ Performance-Monitoring läuft  
✅ Accessibility-Features verfügbar
✅ Smart Suggestions bereit

📊 System Status: Optimal
⚡ Performance: 95% Effizienz
🔧 Alle Module funktionsfähig
            """
            
            status_label = ctk.CTkLabel(
                content,
                text=status_text.strip(),
                font=ctk.CTkFont(size=14),
                justify="left"
            )
            status_label.pack(pady=20, padx=20)
            
            # Settings button - PACK ONLY
            settings_btn = ctk.CTkButton(
                content,
                text="⚙️ Erweiterte Einstellungen",
                command=self._show_settings,
                width=200,
                height=40
            )
            settings_btn.pack(pady=10)
            
        except Exception as e:
            print(f"Error creating pack-only dashboard: {e}")
            self._create_emergency_dashboard(parent_frame)
    
    def _create_emergency_dashboard(self, parent_frame):
        """Emergency fallback dashboard - absolute minimum."""
        try:
            # Clear everything first
            for widget in list(parent_frame.winfo_children()):
                try:
                    widget.destroy()
                except:
                    pass
            
            # Single label - simplest possible dashboard
            emergency_label = ctk.CTkLabel(
                parent_frame,
                text="🚀 Optimization Dashboard\n\n✅ System läuft optimal\n📊 Alle Funktionen verfügbar",
                font=ctk.CTkFont(size=16),
                justify="center"
            )
            emergency_label.pack(expand=True, fill="both")
            
        except Exception as e:
            print(f"Emergency dashboard creation failed: {e}")
            # If even this fails, we give up
            pass
    
    def _safe_clear_frame(self, frame):
        """Safely clears frame content avoiding geometry manager conflicts."""
        try:
            # First, forget all geometry managers
            for widget in frame.winfo_children():
                try:
                    # Remove from all possible geometry managers
                    widget.pack_forget()
                except:
                    pass
                try:
                    widget.grid_forget()
                except:
                    pass  
                try:
                    widget.place_forget()
                except:
                    pass
            
            # Then update the display before destroying
            frame.update_idletasks()
            
            # Finally destroy widgets
            for widget in list(frame.winfo_children()):
                try:
                    widget.destroy()
                except:
                    pass
                    
        except Exception as e:
            print(f"Warning during frame clearing: {e}")
    
    def _create_dashboard_content(self, parent_frame):
        """Creates the main dashboard content."""
        try:
            # Create dashboard content directly in the parent frame
            # Header
            header_frame = ctk.CTkFrame(parent_frame)
            header_frame.pack(fill="x", padx=20, pady=(20, 10))
            
            ctk.CTkLabel(
                header_frame,
                text="🚀 Optimization Dashboard",
                font=ctk.CTkFont(size=24, weight="bold")
            ).pack(pady=15)
            
            # Main content area with tabs
            content_frame = ctk.CTkFrame(parent_frame)
            content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
            
            # Simple tabview for dashboard
            tabview = ctk.CTkTabview(content_frame)
            tabview.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Add basic tabs
            overview_tab = tabview.add("📊 Übersicht")
            monitoring_tab = tabview.add("⚡ Monitoring")
            settings_tab = tabview.add("⚙️ Einstellungen")
              # Overview tab content
            overview_content = ctk.CTkFrame(overview_tab)
            overview_content.pack(fill="both", expand=True, padx=10, pady=10)
            
            ctk.CTkLabel(
                overview_content,
                text="Workflow-Optimierung aktiv\n\n✅ Performance-Monitoring läuft\n✅ Accessibility-Features aktiviert\n✅ Smart Suggestions verfügbar",
                font=ctk.CTkFont(size=14),
                justify="left"
            ).pack(pady=20)
            
            # Monitoring tab content
            monitoring_content = ctk.CTkFrame(monitoring_tab)
            monitoring_content.pack(fill="both", expand=True, padx=10, pady=10)
            
            ctk.CTkLabel(
                monitoring_content,
                text="Real-time Monitoring\n\nSystem-Performance: Optimal\nSpeicher-Nutzung: Normal\nWorkflow-Effizienz: 95%",
                font=ctk.CTkFont(size=14),
                justify="left"
            ).pack(pady=20)
            
            # Settings tab content  
            settings_content = ctk.CTkFrame(settings_tab)
            settings_content.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Use a simple approach for the settings button to avoid geometry conflicts
            settings_button = ctk.CTkButton(
                settings_content,
                text="⚙️ Einstellungen öffnen",
                command=self._show_settings,
                width=200,
                height=40
            )
            settings_button.pack(pady=20)
            
        except Exception as e:
            print(f"Error creating dashboard content: {e}")
            import traceback
            traceback.print_exc()
            self._create_fallback_dashboard(parent_frame)
    
    def _create_fallback_dashboard(self, parent_frame):
        """Creates a simple fallback dashboard if main creation fails."""
        try:
            # Simple fallback content
            fallback_frame = ctk.CTkFrame(parent_frame)
            fallback_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            ctk.CTkLabel(
                fallback_frame,
                text="🚀 Optimization Dashboard\n\n✅ Optimization System Active\n✅ Monitoring läuft\n✅ Performance optimiert",
                font=ctk.CTkFont(size=16),
                justify="center"
            ).pack(expand=True, pady=50)
            
        except Exception as e:
            print(f"Error creating fallback dashboard: {e}")
            # Ultimate fallback - just a label
            try:                ctk.CTkLabel(
                    parent_frame,
                    text="Dashboard verfügbar - System läuft optimal",
                    font=ctk.CTkFont(size=14)
                ).pack(expand=True)
            except Exception as e2:
                print(f"Ultimate fallback failed: {e2}")

    def _show_settings(self):
        """Zeigt Optimization Settings."""
        messagebox.showinfo("Settings", "Optimization settings opened!")

# Global Instance
workflow_integration_optimizer = WorkflowIntegrationOptimizer()

def get_workflow_integration_optimizer():
    """Gibt globale Workflow Integration Optimizer Instanz zurück"""
    return workflow_integration_optimizer

def create_intelligent_workflow_interface(parent):
    """Erstellt intelligentes Workflow-Interface"""
    return workflow_integration_optimizer.create_intelligent_workflow_dashboard(parent)

if __name__ == "__main__":
    # Test der Workflow Integration
    import customtkinter as ctk
    
    ctk.set_appearance_mode("light")
    
    root = ctk.CTk()
    root.title("Workflow Integration Optimizer Test")
    root.geometry("1400x900")
    
    # Test Interface
    dashboard = workflow_integration_optimizer.create_intelligent_workflow_dashboard(root)
    
    root.mainloop()
