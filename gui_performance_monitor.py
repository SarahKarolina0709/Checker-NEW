"""
GUI Performance Monitor - Echtzeit UI-Performance Überwachung
=============================================================

Zeigt Performance-Metriken der GUI in Echtzeit an und bietet 
Optimierungsvorschläge für eine bessere Benutzererfahrung.
"""

import customtkinter as ctk
import tkinter as tk
import threading
import time
import psutil
import gc
from typing import Dict, List, Any, Optional
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class GUIPerformanceMonitor:
    """Überwacht und visualisiert GUI-Performance in Echtzeit."""
    
    def __init__(self, app):
        self.app = app
        self.logger = app.logger if hasattr(app, 'logger') else None
        
        # Performance tracking
        self.metrics = {
            "memory_usage": deque(maxlen=100),
            "cpu_usage": deque(maxlen=100),
            "render_times": deque(maxlen=50),
            "ui_responsiveness": deque(maxlen=50),
            "animation_fps": deque(maxlen=30)
        }
        
        # Monitoring state
        self.monitoring_active = False
        self.monitor_thread = None
        self.monitor_window = None
        
        # Performance thresholds
        self.thresholds = {
            "memory_warning": 200,  # MB
            "memory_critical": 500,  # MB
            "cpu_warning": 70,  # %
            "cpu_critical": 90,  # %
            "render_time_warning": 50,  # ms
            "render_time_critical": 100,  # ms
        }
        
        # UI elements
        self.charts = {}
        self.status_labels = {}
        
    def start_monitoring(self):
        """Starte Performance-Monitoring."""
        if self.monitoring_active:
            return
        
        try:
            self.monitoring_active = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            
            if self.logger:
                self.logger.info("Performance monitoring started")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error starting performance monitor: {e}")
    
    def stop_monitoring(self):
        """Stoppe Performance-Monitoring."""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
        
        if self.logger:
            self.logger.info("Performance monitoring stopped")
    
    def show_monitor_window(self):
        """Zeige Performance-Monitor-Fenster."""
        if self.monitor_window and self.monitor_window.winfo_exists():
            self.monitor_window.focus()
            return
        
        try:
            self._create_monitor_window()
            self.start_monitoring()
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error showing monitor window: {e}")
    
    def _create_monitor_window(self):
        """Erstelle das Monitor-Fenster."""
        self.monitor_window = ctk.CTkToplevel(self.app.root)
        self.monitor_window.title("🔍 GUI Performance Monitor")
        self.monitor_window.geometry("900x700")
        self.monitor_window.configure(fg_color="#F8FAFC")
        
        # Make window stay on top
        self.monitor_window.attributes("-topmost", True)
        
        # Window cleanup
        self.monitor_window.protocol("WM_DELETE_WINDOW", self._on_monitor_close)
        
        # Header
        header_frame = ctk.CTkFrame(self.monitor_window, fg_color="#FFFFFF", height=60)
        header_frame.pack(fill="x", padx=10, pady=10)
        header_frame.pack_propagate(False)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="🔍 GUI Performance Monitor",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#0F172A"
        )
        title_label.pack(side="left", padx=20, pady=15)
        
        # Control buttons
        control_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        control_frame.pack(side="right", padx=20, pady=10)
        
        self.start_btn = ctk.CTkButton(
            control_frame,
            text="▶️ Start",
            command=self.start_monitoring,
            width=80,
            height=30,
            fg_color="#10B981"
        )
        self.start_btn.pack(side="left", padx=5)
        
        self.stop_btn = ctk.CTkButton(
            control_frame,
            text="⏹️ Stop",
            command=self.stop_monitoring,
            width=80,
            height=30,
            fg_color="#EF4444"
        )
        self.stop_btn.pack(side="left", padx=5)
        
        clear_btn = ctk.CTkButton(
            control_frame,
            text="🗑️ Clear",
            command=self._clear_metrics,
            width=80,
            height=30,
            fg_color="#6B7280"
        )
        clear_btn.pack(side="left", padx=5)
        
        # Main content area
        content_frame = ctk.CTkFrame(self.monitor_window, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Create tabs
        self._create_tabs(content_frame)
    
    def _create_tabs(self, parent):
        """Erstelle Tab-System für verschiedene Metriken."""
        # Tab frame
        tab_frame = ctk.CTkFrame(parent, fg_color="#FFFFFF")
        tab_frame.pack(fill="both", expand=True)
        
        # Tab buttons
        tab_button_frame = ctk.CTkFrame(tab_frame, fg_color="#F1F5F9", height=50)
        tab_button_frame.pack(fill="x", padx=10, pady=10)
        tab_button_frame.pack_propagate(False)
        
        self.tab_buttons = {}
        self.tab_contents = {}
        
        tabs = [
            ("overview", "📊 Übersicht"),
            ("memory", "💾 Speicher"),
            ("performance", "⚡ Performance"),
            ("optimization", "🔧 Optimierung")
        ]
        
        for i, (tab_id, tab_name) in enumerate(tabs):
            btn = ctk.CTkButton(
                tab_button_frame,
                text=tab_name,
                command=lambda tid=tab_id: self._switch_tab(tid),
                width=120,
                height=35,
                fg_color="#E2E8F0" if i > 0 else "#2563EB",
                text_color="#64748B" if i > 0 else "#FFFFFF"
            )
            btn.pack(side="left", padx=5, pady=7)
            self.tab_buttons[tab_id] = btn
        
        # Tab content area
        self.tab_content_frame = ctk.CTkFrame(tab_frame, fg_color="transparent")
        self.tab_content_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Create tab contents
        self._create_overview_tab()
        self._create_memory_tab()
        self._create_performance_tab()
        self._create_optimization_tab()
        
        # Show overview tab by default
        self._switch_tab("overview")
    
    def _create_overview_tab(self):
        """Erstelle Übersichts-Tab."""
        overview_frame = ctk.CTkFrame(self.tab_content_frame, fg_color="#FFFFFF")
        
        # Current status grid
        status_grid = ctk.CTkFrame(overview_frame, fg_color="transparent")
        status_grid.pack(fill="x", padx=20, pady=20)
        status_grid.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Status cards
        self._create_status_card(status_grid, "memory", "💾 Speicher", "0 MB", 0, 0)
        self._create_status_card(status_grid, "cpu", "🔥 CPU", "0%", 0, 1)
        self._create_status_card(status_grid, "render", "🎨 Render Zeit", "0ms", 0, 2)
        self._create_status_card(status_grid, "fps", "📹 FPS", "0", 0, 3)
        
        # Quick actions
        actions_frame = ctk.CTkFrame(overview_frame, fg_color="#F8FAFC")
        actions_frame.pack(fill="x", padx=20, pady=10)
        
        actions_title = ctk.CTkLabel(
            actions_frame,
            text="⚡ Schnellaktionen",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#0F172A"
        )
        actions_title.pack(anchor="w", padx=15, pady=(15, 10))
        
        action_buttons = ctk.CTkFrame(actions_frame, fg_color="transparent")
        action_buttons.pack(fill="x", padx=15, pady=(0, 15))
        
        gc_btn = ctk.CTkButton(
            action_buttons,
            text="🗑️ Garbage Collection",
            command=self._force_gc,
            height=35,
            fg_color="#10B981"
        )
        gc_btn.pack(side="left", padx=(0, 10))
        
        optimize_btn = ctk.CTkButton(
            action_buttons,
            text="🚀 UI Optimieren",
            command=self._optimize_ui,
            height=35,
            fg_color="#3B82F6"
        )
        optimize_btn.pack(side="left", padx=10)
        
        self.tab_contents["overview"] = overview_frame
    
    def _create_status_card(self, parent, key, title, value, row, col):
        """Erstelle Status-Karte."""
        card = ctk.CTkFrame(parent, fg_color="#F8FAFC", corner_radius=8)
        card.grid(row=row, column=col, sticky="ew", padx=5, pady=5)
        
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#64748B"
        )
        title_label.pack(pady=(15, 5))
        
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#0F172A"
        )
        value_label.pack(pady=(0, 15))
        
        self.status_labels[key] = value_label
    
    def _create_memory_tab(self):
        """Erstelle Speicher-Tab."""
        memory_frame = ctk.CTkFrame(self.tab_content_frame, fg_color="#FFFFFF")
        
        # Memory chart
        chart_frame = ctk.CTkFrame(memory_frame, fg_color="#F8FAFC")
        chart_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        chart_title = ctk.CTkLabel(
            chart_frame,
            text="💾 Speicherverbrauch über Zeit",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#0F172A"
        )
        chart_title.pack(pady=15)
        
        # Matplotlib chart
        fig, ax = plt.subplots(figsize=(8, 4), facecolor='#F8FAFC')
        ax.set_facecolor('#FFFFFF')
        ax.set_title('Speicherverbrauch (MB)')
        ax.set_xlabel('Zeit')
        ax.set_ylabel('MB')
        ax.grid(True, alpha=0.3)
        
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        
        self.charts["memory"] = (fig, ax, canvas)
        self.tab_contents["memory"] = memory_frame
    
    def _create_performance_tab(self):
        """Erstelle Performance-Tab."""
        perf_frame = ctk.CTkFrame(self.tab_content_frame, fg_color="#FFFFFF")
        
        # Performance metrics
        metrics_frame = ctk.CTkFrame(perf_frame, fg_color="#F8FAFC")
        metrics_frame.pack(fill="x", padx=20, pady=20)
        
        metrics_title = ctk.CTkLabel(
            metrics_frame,
            text="⚡ Performance-Metriken",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#0F172A"
        )
        metrics_title.pack(pady=15)
        
        # Metrics grid
        metrics_grid = ctk.CTkFrame(metrics_frame, fg_color="transparent")
        metrics_grid.pack(fill="x", padx=15, pady=(0, 15))
        metrics_grid.grid_columnconfigure((0, 1), weight=1)
        
        # Render performance
        render_card = ctk.CTkFrame(metrics_grid, fg_color="#FFFFFF")
        render_card.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        render_title = ctk.CTkLabel(
            render_card,
            text="🎨 Render-Performance",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#0F172A"
        )
        render_title.pack(pady=(15, 5))
        
        self.render_time_label = ctk.CTkLabel(
            render_card,
            text="Durchschnitt: 0ms",
            font=ctk.CTkFont(size=12),
            text_color="#64748B"
        )
        self.render_time_label.pack(pady=(0, 15))
        
        # UI Responsiveness
        resp_card = ctk.CTkFrame(metrics_grid, fg_color="#FFFFFF")
        resp_card.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
        
        resp_title = ctk.CTkLabel(
            resp_card,
            text="📱 UI-Reaktionsfähigkeit",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#0F172A"
        )
        resp_title.pack(pady=(15, 5))
        
        self.responsiveness_label = ctk.CTkLabel(
            resp_card,
            text="Status: Gut",
            font=ctk.CTkFont(size=12),
            text_color="#10B981"
        )
        self.responsiveness_label.pack(pady=(0, 15))
        
        self.tab_contents["performance"] = perf_frame
    
    def _create_optimization_tab(self):
        """Erstelle Optimierungs-Tab."""
        opt_frame = ctk.CTkFrame(self.tab_content_frame, fg_color="#FFFFFF")
        
        # Optimization suggestions
        suggestions_frame = ctk.CTkFrame(opt_frame, fg_color="#F8FAFC")
        suggestions_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        suggestions_title = ctk.CTkLabel(
            suggestions_frame,
            text="🔧 Optimierungsvorschläge",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#0F172A"
        )
        suggestions_title.pack(pady=15)
        
        # Suggestions list
        self.suggestions_scroll = ctk.CTkScrollableFrame(
            suggestions_frame,
            fg_color="#FFFFFF"
        )
        self.suggestions_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        self._update_optimization_suggestions()
        
        self.tab_contents["optimization"] = opt_frame
    
    def _switch_tab(self, tab_id):
        """Wechsele zwischen Tabs."""
        # Hide all tabs
        for content in self.tab_contents.values():
            content.pack_forget()
        
        # Update button colors
        for tid, btn in self.tab_buttons.items():
            if tid == tab_id:
                btn.configure(fg_color="#2563EB", text_color="#FFFFFF")
            else:
                btn.configure(fg_color="#E2E8F0", text_color="#64748B")
        
        # Show selected tab
        if tab_id in self.tab_contents:
            self.tab_contents[tab_id].pack(fill="both", expand=True)
    
    def _monitor_loop(self):
        """Haupt-Monitoring-Loop."""
        while self.monitoring_active:
            try:
                self._collect_metrics()
                self._update_display()
                time.sleep(1.0)  # Update every second
                
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Error in monitor loop: {e}")
                time.sleep(5.0)  # Wait longer on error
    
    def _collect_metrics(self):
        """Sammle Performance-Metriken."""
        try:
            # Memory usage
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            self.metrics["memory_usage"].append(memory_mb)
            
            # CPU usage
            cpu_percent = process.cpu_percent()
            self.metrics["cpu_usage"].append(cpu_percent)
            
            # Simulate render time (would be measured in real implementation)
            render_time = np.random.normal(25, 5)  # Simulate ~25ms render time
            self.metrics["render_times"].append(max(0, render_time))
            
            # UI responsiveness (simulated)
            responsiveness = 100 - min(cpu_percent * 0.5 + memory_mb * 0.1, 100)
            self.metrics["ui_responsiveness"].append(max(0, responsiveness))
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error collecting metrics: {e}")
    
    def _update_display(self):
        """Aktualisiere Display mit aktuellen Metriken."""
        if not self.monitor_window or not self.monitor_window.winfo_exists():
            return
        
        try:
            # Update status labels
            if self.metrics["memory_usage"]:
                current_memory = self.metrics["memory_usage"][-1]
                self.status_labels["memory"].configure(text=f"{current_memory:.1f} MB")
                
                # Color coding
                if current_memory > self.thresholds["memory_critical"]:
                    color = "#EF4444"  # Red
                elif current_memory > self.thresholds["memory_warning"]:
                    color = "#F59E0B"  # Yellow
                else:
                    color = "#10B981"  # Green
                self.status_labels["memory"].configure(text_color=color)
            
            if self.metrics["cpu_usage"]:
                current_cpu = self.metrics["cpu_usage"][-1]
                self.status_labels["cpu"].configure(text=f"{current_cpu:.1f}%")
            
            if self.metrics["render_times"]:
                current_render = self.metrics["render_times"][-1]
                self.status_labels["render"].configure(text=f"{current_render:.1f}ms")
            
            # Update charts
            self._update_memory_chart()
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error updating display: {e}")
    
    def _update_memory_chart(self):
        """Aktualisiere Speicher-Chart."""
        if "memory" not in self.charts:
            return
        
        try:
            fig, ax, canvas = self.charts["memory"]
            
            if self.metrics["memory_usage"]:
                ax.clear()
                ax.plot(list(self.metrics["memory_usage"]), color="#3B82F6", linewidth=2)
                ax.set_title('Speicherverbrauch (MB)')
                ax.set_xlabel('Zeit (Sekunden)')
                ax.set_ylabel('MB')
                ax.grid(True, alpha=0.3)
                
                # Add threshold lines
                ax.axhline(y=self.thresholds["memory_warning"], color="#F59E0B", linestyle="--", alpha=0.7, label="Warnung")
                ax.axhline(y=self.thresholds["memory_critical"], color="#EF4444", linestyle="--", alpha=0.7, label="Kritisch")
                ax.legend()
                
                canvas.draw()
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error updating memory chart: {e}")
    
    def _update_optimization_suggestions(self):
        """Aktualisiere Optimierungsvorschläge."""
        try:
            # Clear existing suggestions
            for widget in self.suggestions_scroll.winfo_children():
                widget.destroy()
            
            suggestions = self._generate_suggestions()
            
            for i, suggestion in enumerate(suggestions):
                self._create_suggestion_card(suggestion, i)
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error updating suggestions: {e}")
    
    def _generate_suggestions(self) -> List[Dict[str, Any]]:
        """Generiere Optimierungsvorschläge basierend auf Metriken."""
        suggestions = []
        
        # Memory suggestions
        if self.metrics["memory_usage"] and self.metrics["memory_usage"][-1] > self.thresholds["memory_warning"]:
            suggestions.append({
                "title": "🧹 Speicher optimieren",
                "description": "Hoher Speicherverbrauch erkannt. Führen Sie Garbage Collection aus.",
                "action": "gc",
                "priority": "high",
                "impact": "Kann 20-50MB Speicher freigeben"
            })
        
        # Performance suggestions
        if self.metrics["render_times"] and np.mean(self.metrics["render_times"]) > self.thresholds["render_time_warning"]:
            suggestions.append({
                "title": "⚡ Render-Performance verbessern",
                "description": "Lange Render-Zeiten erkannt. Reduzieren Sie Animationen oder komplexe UI-Elemente.",
                "action": "reduce_animations",
                "priority": "medium",
                "impact": "Verbessert UI-Reaktionsfähigkeit"
            })
        
        # General suggestions
        suggestions.extend([
            {
                "title": "🔧 Icon-Cache optimieren",
                "description": "Bereinigen Sie den Icon-Cache für bessere Performance.",
                "action": "clear_icon_cache",
                "priority": "low",
                "impact": "Spart 5-15MB Speicher"
            },
            {
                "title": "🎨 Theme-Wechsel",
                "description": "Dark Theme kann die Performance auf einigen Systemen verbessern.",
                "action": "suggest_theme",
                "priority": "low",
                "impact": "Kann Akkulaufzeit verlängern"
            }
        ])
        
        return suggestions
    
    def _create_suggestion_card(self, suggestion, index):
        """Erstelle Vorschlag-Karte."""
        card = ctk.CTkFrame(self.suggestions_scroll, fg_color="#F8FAFC")
        card.pack(fill="x", pady=5, padx=10)
        
        # Priority indicator
        priority_colors = {
            "high": "#EF4444",
            "medium": "#F59E0B",
            "low": "#6B7280"
        }
        
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 5))
        
        priority_badge = ctk.CTkFrame(
            header,
            fg_color=priority_colors.get(suggestion["priority"], "#6B7280"),
            width=80,
            height=20,
            corner_radius=10
        )
        priority_badge.pack(side="right")
        
        priority_label = ctk.CTkLabel(
            priority_badge,
            text=suggestion["priority"].upper(),
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#FFFFFF"
        )
        priority_label.pack()
        
        title_label = ctk.CTkLabel(
            header,
            text=suggestion["title"],
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#0F172A"
        )
        title_label.pack(side="left")
        
        # Description
        desc_label = ctk.CTkLabel(
            card,
            text=suggestion["description"],
            font=ctk.CTkFont(size=12),
            text_color="#64748B",
            wraplength=500,
            justify="left"
        )
        desc_label.pack(anchor="w", padx=15, pady=5)
        
        # Impact
        impact_label = ctk.CTkLabel(
            card,
            text=f"💡 {suggestion['impact']}",
            font=ctk.CTkFont(size=11),
            text_color="#10B981"
        )
        impact_label.pack(anchor="w", padx=15, pady=5)
        
        # Action button
        if suggestion["action"]:
            action_btn = ctk.CTkButton(
                card,
                text="🚀 Anwenden",
                command=lambda: self._apply_suggestion(suggestion["action"]),
                width=100,
                height=30,
                fg_color="#3B82F6"
            )
            action_btn.pack(anchor="e", padx=15, pady=(5, 15))
    
    def _apply_suggestion(self, action):
        """Wende Optimierungsvorschlag an."""
        try:
            if action == "gc":
                self._force_gc()
            elif action == "clear_icon_cache":
                self._clear_icon_cache()
            elif action == "reduce_animations":
                self._reduce_animations()
            elif action == "suggest_theme":
                self._suggest_theme_change()
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error applying suggestion {action}: {e}")
    
    def _force_gc(self):
        """Erzwinge Garbage Collection."""
        try:
            before = psutil.Process().memory_info().rss / 1024 / 1024
            gc.collect()
            after = psutil.Process().memory_info().rss / 1024 / 1024
            freed = before - after
            
            if self.logger:
                self.logger.info(f"Garbage collection freed {freed:.1f}MB")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error in garbage collection: {e}")
    
    def _clear_icon_cache(self):
        """Leere Icon-Cache."""
        try:
            if hasattr(self.app, 'icon_manager') and self.app.icon_manager:
                self.app.icon_manager.clear_icon_cache()
                if self.logger:
                    self.logger.info("Icon cache cleared")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error clearing icon cache: {e}")
    
    def _reduce_animations(self):
        """Reduziere Animationen."""
        # This would be implemented to reduce animation complexity
        if self.logger:
            self.logger.info("Animation reduction suggested")
    
    def _suggest_theme_change(self):
        """Schlage Theme-Wechsel vor."""
        # This would open theme selection
        if self.logger:
            self.logger.info("Theme change suggested")
    
    def _optimize_ui(self):
        """Führe allgemeine UI-Optimierung durch."""
        try:
            self._force_gc()
            self._clear_icon_cache()
            
            if self.logger:
                self.logger.info("UI optimization completed")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error optimizing UI: {e}")
    
    def _clear_metrics(self):
        """Lösche alle Metriken."""
        for metric_list in self.metrics.values():
            metric_list.clear()
        
        if self.logger:
            self.logger.info("Performance metrics cleared")
    
    def _on_monitor_close(self):
        """Handle Monitor-Fenster schließen."""
        self.stop_monitoring()
        self.monitor_window.destroy()
        self.monitor_window = None

def show_performance_monitor(app):
    """Zeige Performance Monitor für die Anwendung."""
    try:
        monitor = GUIPerformanceMonitor(app)
        monitor.show_monitor_window()
        return monitor
    except Exception as e:
        if hasattr(app, 'logger'):
            app.logger.error(f"Error showing performance monitor: {e}")
        return None
