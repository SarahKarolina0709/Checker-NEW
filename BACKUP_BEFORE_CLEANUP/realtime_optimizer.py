# -*- coding: utf-8 -*-
"""
Real-time Performance Optimizer - Live-Optimierung basierend auf Systemlast
Erweitert das Performance Monitoring um dynamische Anpassungen
"""

import psutil
import threading
import time
import json
import os
import gc
import sys
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, List, Optional, Callable, Any
import numpy as np
from collections import deque
import sqlite3
import queue
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import ctypes
from ctypes import wintypes
import win32api
import win32process
import win32con

@dataclass
class SystemMetrics:
    """System-Metriken für Performance-Optimierung"""
    cpu_percent: float
    memory_percent: float
    disk_io: Dict[str, float]
    network_io: Dict[str, float]
    gpu_usage: float
    temperature: float
    battery_level: float
    timestamp: datetime

@dataclass
class OptimizationAction:
    """Optimierungsmaßnahme"""
    name: str
    action_type: str  # reduce_quality, disable_feature, increase_threads, etc.
    parameters: Dict[str, Any]
    priority: int
    estimated_improvement: float
    side_effects: List[str]

class RealTimePerformanceOptimizer:
    """Echtzeit-Performance-Optimierer"""
    
    def __init__(self):
        self.monitoring_active = False
        self.optimization_active = True
        self.metrics_history = deque(maxlen=1000)  # Letzte 1000 Messungen
        self.optimization_rules = {}
        self.current_optimizations = set()
        self.performance_targets = {}
        self.adaptive_thresholds = {}
        self.system_profile = None
        self.optimization_queue = queue.Queue()
        self.metrics_db = self._init_metrics_database()
        
        # Performance-Ziele (anpassbar)
        self.performance_targets = {
            'cpu_usage_max': 80.0,
            'memory_usage_max': 85.0,
            'response_time_max': 2.0,  # Sekunden
            'fps_min': 30,
            'temperature_max': 80.0    # Celsius
        }
        
        # Adaptive Schwellwerte
        self.adaptive_thresholds = {
            'performance_critical': 90.0,  # Kritische Performance
            'performance_warning': 70.0,   # Performance-Warnung
            'performance_optimal': 50.0    # Optimale Performance
        }
        
        self._load_optimization_rules()
        self._detect_system_capabilities()
        
    def _init_metrics_database(self):
        """Initialisiert Metriken-Datenbank"""
        conn = sqlite3.connect('performance_metrics.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY,
                timestamp TIMESTAMP,
                cpu_percent REAL,
                memory_percent REAL,
                disk_read REAL,
                disk_write REAL,
                network_sent REAL,
                network_recv REAL,
                gpu_usage REAL,
                temperature REAL,
                battery_level REAL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS optimizations (
                id INTEGER PRIMARY KEY,
                timestamp TIMESTAMP,
                optimization_name TEXT,
                action_type TEXT,
                parameters TEXT,
                effectiveness REAL,
                duration REAL
            )
        ''')
        
        conn.commit()
        return conn
        
    def _load_optimization_rules(self):
        """Lädt Optimierungsregeln"""
        self.optimization_rules = {
            'high_cpu_usage': {
                'trigger': lambda m: m.cpu_percent > 80,
                'actions': [
                    OptimizationAction(
                        name="reduce_ocr_threads",
                        action_type="thread_reduction",
                        parameters={'max_threads': 2},
                        priority=1,
                        estimated_improvement=15.0,
                        side_effects=["slower_processing"]
                    ),
                    OptimizationAction(
                        name="disable_real_time_preview",
                        action_type="feature_disable",
                        parameters={'feature': 'real_time_preview'},
                        priority=2,
                        estimated_improvement=10.0,
                        side_effects=["reduced_user_feedback"]
                    )
                ]
            },
            'high_memory_usage': {
                'trigger': lambda m: m.memory_percent > 85,
                'actions': [
                    OptimizationAction(
                        name="aggressive_garbage_collection",
                        action_type="memory_cleanup",
                        parameters={'force_gc': True},
                        priority=1,
                        estimated_improvement=20.0,
                        side_effects=["temporary_pause"]
                    ),
                    OptimizationAction(
                        name="reduce_cache_size",
                        action_type="cache_reduction",
                        parameters={'max_cache_mb': 100},
                        priority=2,
                        estimated_improvement=15.0,
                        side_effects=["slower_repeated_operations"]
                    )
                ]
            },
            'low_battery': {
                'trigger': lambda m: m.battery_level < 20 and m.battery_level > 0,
                'actions': [
                    OptimizationAction(
                        name="enable_power_saving",
                        action_type="power_optimization",
                        parameters={'reduce_cpu_freq': True, 'dim_display': True},
                        priority=1,
                        estimated_improvement=30.0,
                        side_effects=["slower_performance", "dimmer_display"]
                    )
                ]
            },
            'high_temperature': {
                'trigger': lambda m: m.temperature > 75,
                'actions': [
                    OptimizationAction(
                        name="thermal_throttling",
                        action_type="thermal_management",
                        parameters={'reduce_load': True, 'increase_cooling': True},
                        priority=1,
                        estimated_improvement=25.0,
                        side_effects=["reduced_performance"]
                    )
                ]
            }
        }
        
    def _detect_system_capabilities(self):
        """Erkennt System-Fähigkeiten"""
        self.system_profile = {
            'cpu_cores': psutil.cpu_count(logical=False),
            'cpu_threads': psutil.cpu_count(logical=True),
            'total_memory': psutil.virtual_memory().total,
            'gpu_available': self._detect_gpu(),
            'ssd_available': self._detect_ssd(),
            'battery_present': self._has_battery(),
            'performance_mode': self._get_performance_mode()
        }
        
    def _detect_gpu(self):
        """Erkennt GPU-Verfügbarkeit"""
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            return len(gpus) > 0
        except:
            return False
            
    def _detect_ssd(self):
        """Erkennt SSD-Verfügbarkeit"""
        try:
            import wmi
            c = wmi.WMI()
            for disk in c.Win32_DiskDrive():
                if 'SSD' in disk.Model or 'Solid State' in disk.Model:
                    return True
        except:
            pass
        return False
        
    def _has_battery(self):
        """Prüft Batterie-Verfügbarkeit"""
        try:
            battery = psutil.sensors_battery()
            return battery is not None
        except:
            return False
            
    def _get_performance_mode(self):
        """Ermittelt aktuellen Performance-Modus"""
        try:
            # Windows Power Plan erkennen
            result = os.popen('powercfg /getactivescheme').read()
            if 'High performance' in result:
                return 'high_performance'
            elif 'Balanced' in result:
                return 'balanced'
            elif 'Power saver' in result:
                return 'power_saver'
        except:
            pass
        return 'unknown'
        
    def start_monitoring(self):
        """Startet Echtzeit-Monitoring"""
        self.monitoring_active = True
        
        # Monitoring Thread
        monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        monitoring_thread.start()
        
        # Optimization Thread
        optimization_thread = threading.Thread(target=self._optimization_loop, daemon=True)
        optimization_thread.start()
        
        # Analytics Thread
        analytics_thread = threading.Thread(target=self._analytics_loop, daemon=True)
        analytics_thread.start()
        
    def stop_monitoring(self):
        """Stoppt Monitoring"""
        self.monitoring_active = False
        
    def _monitoring_loop(self):
        """Haupt-Monitoring-Schleife"""
        while self.monitoring_active:
            try:
                # System-Metriken sammeln
                metrics = self._collect_system_metrics()
                
                # In Historie speichern
                self.metrics_history.append(metrics)
                
                # In Datenbank speichern
                self._save_metrics_to_db(metrics)
                
                # Optimierungen prüfen
                if self.optimization_active:
                    optimizations = self._evaluate_optimizations(metrics)
                    for opt in optimizations:
                        self.optimization_queue.put(opt)
                        
                time.sleep(1)  # 1 Sekunde Intervall
                
            except Exception as e:
                print(f"Monitoring Error: {e}")
                time.sleep(5)
                
    def _collect_system_metrics(self):
        """Sammelt aktuelle System-Metriken"""
        # CPU
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # Memory
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Disk I/O
        disk_io = psutil.disk_io_counters()
        disk_read = disk_io.read_bytes if disk_io else 0
        disk_write = disk_io.write_bytes if disk_io else 0
        
        # Network I/O
        network_io = psutil.net_io_counters()
        network_sent = network_io.bytes_sent if network_io else 0
        network_recv = network_io.bytes_recv if network_io else 0
        
        # GPU (falls verfügbar)
        gpu_usage = self._get_gpu_usage()
        
        # Temperature
        temperature = self._get_cpu_temperature()
        
        # Battery
        battery_level = self._get_battery_level()
        
        return SystemMetrics(
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            disk_io={'read': disk_read, 'write': disk_write},
            network_io={'sent': network_sent, 'recv': network_recv},
            gpu_usage=gpu_usage,
            temperature=temperature,
            battery_level=battery_level,
            timestamp=datetime.now()
        )
        
    def _get_gpu_usage(self):
        """Ermittelt GPU-Auslastung"""
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                return gpus[0].load * 100
        except:
            pass
        return 0.0
        
    def _get_cpu_temperature(self):
        """Ermittelt CPU-Temperatur"""
        try:
            temps = psutil.sensors_temperatures()
            if 'coretemp' in temps:
                return temps['coretemp'][0].current
            elif 'cpu_thermal' in temps:
                return temps['cpu_thermal'][0].current
        except:
            pass
        return 0.0
        
    def _get_battery_level(self):
        """Ermittelt Batteriestand"""
        try:
            battery = psutil.sensors_battery()
            if battery:
                return battery.percent
        except:
            pass
        return 100.0  # Annahme: Desktop ohne Batterie
        
    def _save_metrics_to_db(self, metrics):
        """Speichert Metriken in Datenbank"""
        try:
            cursor = self.metrics_db.cursor()
            cursor.execute('''
                INSERT INTO system_metrics 
                (timestamp, cpu_percent, memory_percent, disk_read, disk_write,
                 network_sent, network_recv, gpu_usage, temperature, battery_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics.timestamp, metrics.cpu_percent, metrics.memory_percent,
                metrics.disk_io['read'], metrics.disk_io['write'],
                metrics.network_io['sent'], metrics.network_io['recv'],
                metrics.gpu_usage, metrics.temperature, metrics.battery_level
            ))
            self.metrics_db.commit()
        except Exception as e:
            print(f"Database save error: {e}")
            
    def _evaluate_optimizations(self, metrics):
        """Bewertet notwendige Optimierungen"""
        optimizations = []
        
        for rule_name, rule in self.optimization_rules.items():
            if rule['trigger'](metrics):
                for action in rule['actions']:
                    if action.name not in self.current_optimizations:
                        optimizations.append(action)
                        
        # Nach Priorität sortieren
        optimizations.sort(key=lambda x: x.priority)
        
        return optimizations
        
    def _optimization_loop(self):
        """Optimierungs-Schleife"""
        while self.monitoring_active:
            try:
                # Warte auf Optimierungsauftrag
                optimization = self.optimization_queue.get(timeout=1)
                
                # Optimierung anwenden
                success = self._apply_optimization(optimization)
                
                if success:
                    self.current_optimizations.add(optimization.name)
                    self._log_optimization(optimization, success=True)
                    
                    # Wirksamkeit überwachen
                    self._monitor_optimization_effectiveness(optimization)
                    
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Optimization error: {e}")
                
    def _apply_optimization(self, optimization):
        """Wendet Optimierung an"""
        try:
            if optimization.action_type == "thread_reduction":
                return self._reduce_thread_count(optimization.parameters)
            elif optimization.action_type == "memory_cleanup":
                return self._perform_memory_cleanup(optimization.parameters)
            elif optimization.action_type == "cache_reduction":
                return self._reduce_cache_size(optimization.parameters)
            elif optimization.action_type == "power_optimization":
                return self._enable_power_saving(optimization.parameters)
            elif optimization.action_type == "thermal_management":
                return self._apply_thermal_throttling(optimization.parameters)
            elif optimization.action_type == "feature_disable":
                return self._disable_feature(optimization.parameters)
                
        except Exception as e:
            print(f"Optimization application error: {e}")
            return False
            
        return False
        
    def _reduce_thread_count(self, params):
        """Reduziert Anzahl der Threads"""
        max_threads = params.get('max_threads', 2)
        
        # Thread-Pool Größe anpassen (wird in anderen Modulen verwendet)
        os.environ['CHECKER_MAX_THREADS'] = str(max_threads)
        
        return True
        
    def _perform_memory_cleanup(self, params):
        """Führt Memory-Cleanup durch"""
        if params.get('force_gc', False):
            # Aggressive Garbage Collection
            for i in range(3):
                gc.collect()
                
        # Cache leeren
        if hasattr(self, 'cache'):
            self.cache.clear()
            
        return True
        
    def _reduce_cache_size(self, params):
        """Reduziert Cache-Größe"""
        max_cache_mb = params.get('max_cache_mb', 100)
        
        # Cache-Limit setzen
        os.environ['CHECKER_MAX_CACHE_MB'] = str(max_cache_mb)
        
        return True
        
    def _enable_power_saving(self, params):
        """Aktiviert Stromsparmodus"""
        try:
            if params.get('reduce_cpu_freq', False):
                # CPU-Frequenz reduzieren (Windows)
                os.system('powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c')  # Power Saver
                
            return True
        except:
            return False
            
    def _apply_thermal_throttling(self, params):
        """Wendet thermische Drosselung an"""
        if params.get('reduce_load', False):
            # CPU-Last reduzieren
            self._reduce_thread_count({'max_threads': 1})
            
        return True
        
    def _disable_feature(self, params):
        """Deaktiviert Feature"""
        feature = params.get('feature')
        
        # Feature-Flag setzen
        os.environ[f'CHECKER_DISABLE_{feature.upper()}'] = 'true'
        
        return True
        
    def _monitor_optimization_effectiveness(self, optimization):
        """Überwacht Wirksamkeit der Optimierung"""
        def monitor():
            start_time = time.time()
            baseline_metrics = list(self.metrics_history)[-10:]  # Letzte 10 Messungen
            
            time.sleep(10)  # 10 Sekunden warten
            
            new_metrics = list(self.metrics_history)[-10:]
            effectiveness = self._calculate_effectiveness(baseline_metrics, new_metrics)
            
            if effectiveness < 0.1:  # Weniger als 10% Verbesserung
                self._revert_optimization(optimization)
                
            duration = time.time() - start_time
            self._log_optimization_effectiveness(optimization, effectiveness, duration)
            
        threading.Thread(target=monitor, daemon=True).start()
        
    def _calculate_effectiveness(self, baseline, current):
        """Berechnet Effektivität einer Optimierung"""
        if not baseline or not current:
            return 0.0
            
        # Durchschnittliche Verbesserung berechnen
        baseline_avg_cpu = np.mean([m.cpu_percent for m in baseline])
        current_avg_cpu = np.mean([m.cpu_percent for m in current])
        
        baseline_avg_memory = np.mean([m.memory_percent for m in baseline])
        current_avg_memory = np.mean([m.memory_percent for m in current])
        
        cpu_improvement = max(0, (baseline_avg_cpu - current_avg_cpu) / baseline_avg_cpu)
        memory_improvement = max(0, (baseline_avg_memory - current_avg_memory) / baseline_avg_memory)
        
        return (cpu_improvement + memory_improvement) / 2
        
    def _revert_optimization(self, optimization):
        """Macht Optimierung rückgängig"""
        try:
            if optimization.action_type == "thread_reduction":
                os.environ.pop('CHECKER_MAX_THREADS', None)
            elif optimization.action_type == "cache_reduction":
                os.environ.pop('CHECKER_MAX_CACHE_MB', None)
            elif optimization.action_type == "power_optimization":
                os.system('powercfg /setactive 381b4222-f694-41f0-9685-ff5bb260df2e')  # Balanced
            elif optimization.action_type == "feature_disable":
                feature = optimization.parameters.get('feature')
                os.environ.pop(f'CHECKER_DISABLE_{feature.upper()}', None)
                
            self.current_optimizations.discard(optimization.name)
            
        except Exception as e:
            print(f"Revert optimization error: {e}")
            
    def _analytics_loop(self):
        """Analytik-Schleife für Muster-Erkennung"""
        while self.monitoring_active:
            try:
                if len(self.metrics_history) >= 100:  # Mindestens 100 Messungen
                    patterns = self._analyze_performance_patterns()
                    self._update_adaptive_thresholds(patterns)
                    
                time.sleep(60)  # Alle 60 Sekunden
                
            except Exception as e:
                print(f"Analytics error: {e}")
                time.sleep(30)
                
    def _analyze_performance_patterns(self):
        """Analysiert Performance-Muster"""
        recent_metrics = list(self.metrics_history)[-100:]  # Letzte 100
        
        patterns = {
            'peak_hours': self._find_peak_usage_hours(recent_metrics),
            'cpu_patterns': self._analyze_cpu_patterns(recent_metrics),
            'memory_patterns': self._analyze_memory_patterns(recent_metrics),
            'performance_degradation': self._detect_performance_degradation(recent_metrics)
        }
        
        return patterns
        
    def get_performance_recommendations(self):
        """Erstellt Performance-Empfehlungen"""
        if len(self.metrics_history) < 50:
            return ["Sammle mehr Daten für bessere Empfehlungen"]
            
        recommendations = []
        recent_metrics = list(self.metrics_history)[-50:]
        
        # CPU-Empfehlungen
        avg_cpu = np.mean([m.cpu_percent for m in recent_metrics])
        if avg_cpu > 70:
            recommendations.append("CPU-Last ist hoch. Erwäge Thread-Reduzierung oder Feature-Deaktivierung.")
            
        # Memory-Empfehlungen
        avg_memory = np.mean([m.memory_percent for m in recent_metrics])
        if avg_memory > 80:
            recommendations.append("Speicherverbrauch ist hoch. Cache-Größe reduzieren oder Garbage Collection optimieren.")
            
        # Thermal-Empfehlungen
        max_temp = max([m.temperature for m in recent_metrics if m.temperature > 0], default=0)
        if max_temp > 75:
            recommendations.append("CPU-Temperatur ist hoch. Thermal Throttling aktivieren.")
            
        # Battery-Empfehlungen
        if self.system_profile['battery_present']:
            min_battery = min([m.battery_level for m in recent_metrics if m.battery_level > 0], default=100)
            if min_battery < 30:
                recommendations.append("Batteriestand niedrig. Stromsparmodus aktivieren.")
                
        return recommendations
        
    def create_performance_dashboard(self, parent):
        """Erstellt Performance-Dashboard"""
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        
        dashboard = ctk.CTkToplevel(parent)
        dashboard.title("Echtzeit-Performance Dashboard")
        dashboard.geometry("1200x800")
        
        # Notebook für verschiedene Ansichten
        notebook = ttk.Notebook(dashboard)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Live Metrics
        live_frame = ttk.Frame(notebook)
        notebook.add(live_frame, text="Live Metriken")
        self._create_live_metrics_view(live_frame)
        
        # Optimization History
        history_frame = ttk.Frame(notebook)
        notebook.add(history_frame, text="Optimierungs-Historie")
        self._create_optimization_history_view(history_frame)
        
        # Recommendations
        recommendations_frame = ttk.Frame(notebook)
        notebook.add(recommendations_frame, text="Empfehlungen")
        self._create_recommendations_view(recommendations_frame)
        
        # System Profile
        profile_frame = ttk.Frame(notebook)
        notebook.add(profile_frame, text="System-Profil")
        self._create_system_profile_view(profile_frame)
        
        return dashboard
        
    def _create_live_metrics_view(self, parent):
        """Erstellt Live-Metriken-Ansicht"""
        # Real-time Chart
        self.fig, ((self.ax1, self.ax2), (self.ax3, self.ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        
        # CPU Chart
        self.ax1.set_title('CPU Usage (%)')
        self.ax1.set_ylim(0, 100)
        self.cpu_line, = self.ax1.plot([], [], 'b-')
        
        # Memory Chart  
        self.ax2.set_title('Memory Usage (%)')
        self.ax2.set_ylim(0, 100)
        self.memory_line, = self.ax2.plot([], [], 'r-')
        
        # Temperature Chart
        self.ax3.set_title('Temperature (°C)')
        self.ax3.set_ylim(0, 100)
        self.temp_line, = self.ax3.plot([], [], 'orange')
        
        # Battery Chart
        self.ax4.set_title('Battery Level (%)')
        self.ax4.set_ylim(0, 100)
        self.battery_line, = self.ax4.plot([], [], 'green')
        
        canvas = FigureCanvasTkAgg(self.fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Update Loop für Live-Charts
        self._start_chart_updates()
        
    def _start_chart_updates(self):
        """Startet Chart-Updates"""
        def update_charts():
            while True:
                if len(self.metrics_history) > 0:
                    recent_metrics = list(self.metrics_history)[-50:]  # Letzte 50
                    
                    times = [i for i in range(len(recent_metrics))]
                    cpu_data = [m.cpu_percent for m in recent_metrics]
                    memory_data = [m.memory_percent for m in recent_metrics]
                    temp_data = [m.temperature for m in recent_metrics]
                    battery_data = [m.battery_level for m in recent_metrics]
                    
                    # Charts aktualisieren
                    self.cpu_line.set_data(times, cpu_data)
                    self.ax1.relim()
                    self.ax1.autoscale_view()
                    
                    self.memory_line.set_data(times, memory_data)
                    self.ax2.relim()
                    self.ax2.autoscale_view()
                    
                    self.temp_line.set_data(times, temp_data)
                    self.ax3.relim()
                    self.ax3.autoscale_view()
                    
                    self.battery_line.set_data(times, battery_data)
                    self.ax4.relim()
                    self.ax4.autoscale_view()
                    
                    self.fig.canvas.draw_idle()
                    
                time.sleep(2)  # Update alle 2 Sekunden
                
        threading.Thread(target=update_charts, daemon=True).start()

# Global instance
realtime_optimizer = RealTimePerformanceOptimizer()

def initialize_realtime_optimization(enable_monitoring=True):
    """Initialisiert Echtzeit-Optimierung"""
    if enable_monitoring:
        realtime_optimizer.start_monitoring()
        
def get_performance_recommendations():
    """Gibt aktuelle Performance-Empfehlungen zurück"""
    return realtime_optimizer.get_performance_recommendations()

def create_performance_dashboard(parent):
    """Erstellt Performance-Dashboard"""
    return realtime_optimizer.create_performance_dashboard(parent)

if __name__ == "__main__":
    # Test der Echtzeit-Optimierung
    print("Starte Echtzeit-Performance-Optimierung...")
    
    realtime_optimizer.start_monitoring()
    
    # Dashboard für Test
    import customtkinter as ctk
    ctk.set_appearance_mode("light")
    
    root = ctk.CTk()
    root.title("Echtzeit-Performance Test")
    root.geometry("1400x900")
    
    # Dashboard Button
    dashboard_btn = ctk.CTkButton(
        root,
        text="Performance Dashboard öffnen",
        command=lambda: realtime_optimizer.create_performance_dashboard(root),
        height=50
    )
    dashboard_btn.pack(pady=50)
    
    # Empfehlungen anzeigen
    def show_recommendations():
        recommendations = realtime_optimizer.get_performance_recommendations()
        messagebox.showinfo("Performance-Empfehlungen", "\n".join(recommendations))
    
    recommendations_btn = ctk.CTkButton(
        root,
        text="Empfehlungen anzeigen",
        command=show_recommendations,
        height=50
    )
    recommendations_btn.pack(pady=20)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        realtime_optimizer.stop_monitoring()
        print("Monitoring gestoppt.")
