# -*- coding: utf-8 -*-
"""
Machine Learning Optimizer für Checker App
Intelligente Performance-Optimierung und Vorhersagen
"""

import os
import json
import pickle
import time
from datetime import datetime, timedelta
import threading
from collections import defaultdict
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import warnings
warnings.filterwarnings('ignore')

class MLOptimizer:
    def __init__(self):
        self.usage_data = []
        self.performance_metrics = defaultdict(list)
        self.models = {}
        self.scalers = {}
        self.anomaly_detector = None
        self.optimization_suggestions = []
        self.prediction_cache = {}
        self.load_historical_data()
        
    def load_historical_data(self):
        """Lädt historische Nutzungsdaten"""
        try:
            with open("ml_usage_data.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                self.usage_data = data.get("usage_data", [])
                self.performance_metrics = defaultdict(list, data.get("performance_metrics", {}))
        except FileNotFoundError:
            self.initialize_empty_data()
    
    def initialize_empty_data(self):
        """Initialisiert leere Datenstrukturen"""
        self.usage_data = []
        self.performance_metrics = {
            "ocr_times": [],
            "analysis_times": [],
            "file_sizes": [],
            "memory_usage": [],
            "cpu_usage": [],
            "user_interactions": [],
            "error_rates": []
        }
    
    def save_data(self):
        """Speichert Daten für ML-Modelle"""
        try:
            data = {
                "usage_data": self.usage_data[-1000:],  # Nur letzte 1000 Einträge
                "performance_metrics": dict(self.performance_metrics)
            }
            with open("ml_usage_data.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Fehler beim Speichern der ML-Daten: {e}")
    
    def log_usage_event(self, event_type, duration=None, file_size=None, 
                       memory_usage=None, cpu_usage=None, error_occurred=False):
        """Protokolliert Nutzungsereignis für ML-Analyse"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "duration": duration,
            "file_size": file_size,
            "memory_usage": memory_usage,
            "cpu_usage": cpu_usage,
            "error_occurred": error_occurred,
            "day_of_week": datetime.now().weekday(),
            "hour_of_day": datetime.now().hour
        }
        
        self.usage_data.append(event)
        
        # Performance Metrics aktualisieren
        if duration and event_type == "ocr_processing":
            self.performance_metrics["ocr_times"].append(duration)
        elif duration and event_type == "text_analysis":
            self.performance_metrics["analysis_times"].append(duration)
        
        if file_size:
            self.performance_metrics["file_sizes"].append(file_size)
        if memory_usage:
            self.performance_metrics["memory_usage"].append(memory_usage)
        if cpu_usage:
            self.performance_metrics["cpu_usage"].append(cpu_usage)
        
        self.performance_metrics["error_rates"].append(1 if error_occurred else 0)
        
        # Periodisch Daten speichern
        if len(self.usage_data) % 10 == 0:
            self.save_data()
    
    def train_performance_predictor(self):
        """Trainiert ML-Modell zur Performance-Vorhersage"""
        if len(self.usage_data) < 50:
            return False
        
        try:
            # Daten vorbereiten
            df = pd.DataFrame(self.usage_data)
            df = df.dropna()
            
            if len(df) < 20:
                return False
            
            # Features und Targets definieren
            feature_columns = ['file_size', 'day_of_week', 'hour_of_day']
            target_column = 'duration'
            
            # Nur Zeilen mit allen benötigten Spalten
            valid_rows = df[feature_columns + [target_column]].dropna()
            
            if len(valid_rows) < 20:
                return False
            
            X = valid_rows[feature_columns]
            y = valid_rows[target_column]
            
            # Train-Test Split
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Skalierung
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Modell trainieren
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_train_scaled, y_train)
            
            # Evaluierung
            y_pred = model.predict(X_test_scaled)
            mse = mean_squared_error(y_test, y_pred)
            
            # Modell speichern
            self.models['performance_predictor'] = model
            self.scalers['performance_predictor'] = scaler
            
            print(f"Performance Predictor trainiert. MSE: {mse:.4f}")
            return True
            
        except Exception as e:
            print(f"Fehler beim Training des Performance Predictors: {e}")
            return False
    
    def train_anomaly_detector(self):
        """Trainiert Anomalieerkennung für ungewöhnliche Performance"""
        if len(self.usage_data) < 30:
            return False
        
        try:
            # Features für Anomalieerkennung vorbereiten
            features = []
            for event in self.usage_data:
                if all(key in event and event[key] is not None 
                      for key in ['duration', 'file_size', 'memory_usage']):
                    features.append([
                        event['duration'],
                        event['file_size'],
                        event['memory_usage'],
                        event['hour_of_day']
                    ])
            
            if len(features) < 20:
                return False
            
            X = np.array(features)
            
            # Isolation Forest für Anomalieerkennung
            self.anomaly_detector = IsolationForest(
                contamination=0.1,
                random_state=42
            )
            self.anomaly_detector.fit(X)
            
            print("Anomaly Detector trainiert")
            return True
            
        except Exception as e:
            print(f"Fehler beim Training des Anomaly Detectors: {e}")
            return False
    
    def predict_processing_time(self, file_size, current_time=None):
        """Vorhersage der Verarbeitungszeit"""
        if 'performance_predictor' not in self.models:
            return None
        
        try:
            if current_time is None:
                current_time = datetime.now()
            
            # Features vorbereiten
            features = np.array([[
                file_size,
                current_time.weekday(),
                current_time.hour
            ]])
            
            # Vorhersage
            scaler = self.scalers['performance_predictor']
            model = self.models['performance_predictor']
            
            features_scaled = scaler.transform(features)
            prediction = model.predict(features_scaled)[0]
            
            return max(0.1, prediction)  # Mindestens 0.1 Sekunden
            
        except Exception as e:
            print(f"Fehler bei Performance-Vorhersage: {e}")
            return None
    
    def detect_performance_anomalies(self, duration, file_size, memory_usage):
        """Erkennt Performance-Anomalien"""
        if self.anomaly_detector is None:
            return False
        
        try:
            features = np.array([[
                duration,
                file_size,
                memory_usage,
                datetime.now().hour
            ]])
            
            anomaly_score = self.anomaly_detector.decision_function(features)[0]
            is_anomaly = self.anomaly_detector.predict(features)[0] == -1
            
            if is_anomaly:
                self.log_anomaly(duration, file_size, memory_usage, anomaly_score)
            
            return is_anomaly
            
        except Exception as e:
            print(f"Fehler bei Anomalieerkennung: {e}")
            return False
    
    def log_anomaly(self, duration, file_size, memory_usage, score):
        """Protokolliert erkannte Anomalie"""
        anomaly = {
            "timestamp": datetime.now().isoformat(),
            "duration": duration,
            "file_size": file_size,
            "memory_usage": memory_usage,
            "anomaly_score": score,
            "type": "performance_anomaly"
        }
        
        print(f"Performance-Anomalie erkannt: {anomaly}")
    
    def generate_smart_suggestions(self):
        """Generiert intelligente Optimierungsvorschläge"""
        suggestions = []
        
        # Analyse der Performance-Trends
        if len(self.performance_metrics["ocr_times"]) > 10:
            recent_ocr_times = self.performance_metrics["ocr_times"][-10:]
            avg_ocr_time = np.mean(recent_ocr_times)
            
            if avg_ocr_time > 5.0:  # Über 5 Sekunden
                suggestions.append({
                    "type": "ocr_optimization",
                    "priority": "high",
                    "suggestion": "OCR-Verarbeitung ist langsam. Reduzieren Sie DPI oder aktivieren Sie Parallel-Processing.",
                    "potential_improvement": "30-50% Zeitersparnis",
                    "action": "adjust_ocr_settings"
                })
        
        # Speicherverbrauch-Analyse
        if len(self.performance_metrics["memory_usage"]) > 5:
            recent_memory = self.performance_metrics["memory_usage"][-5:]
            avg_memory = np.mean(recent_memory)
            
            if avg_memory > 500:  # Über 500 MB
                suggestions.append({
                    "type": "memory_optimization",
                    "priority": "medium",
                    "suggestion": "Hoher Speicherverbrauch erkannt. Aktivieren Sie Garbage Collection zwischen Verarbeitungen.",
                    "potential_improvement": "20-30% weniger RAM-Verbrauch",
                    "action": "enable_memory_management"
                })
        
        # Dateigröße-basierte Vorschläge
        if len(self.performance_metrics["file_sizes"]) > 5:
            recent_sizes = self.performance_metrics["file_sizes"][-5:]
            avg_size = np.mean(recent_sizes)
            
            if avg_size > 10 * 1024 * 1024:  # Über 10 MB
                suggestions.append({
                    "type": "file_optimization",
                    "priority": "medium",
                    "suggestion": "Große Dateien erkannt. Aktivieren Sie Batch-Processing oder Datei-Komprimierung.",
                    "potential_improvement": "40-60% Zeitersparnis",
                    "action": "enable_batch_processing"
                })
        
        # Fehlerrate-Analyse
        if len(self.performance_metrics["error_rates"]) > 10:
            recent_errors = self.performance_metrics["error_rates"][-10:]
            error_rate = np.mean(recent_errors)
            
            if error_rate > 0.1:  # Über 10% Fehlerrate
                suggestions.append({
                    "type": "reliability_improvement",
                    "priority": "high",
                    "suggestion": "Hohe Fehlerrate erkannt. Überprüfen Sie Eingabedateien und aktivieren Sie erweiterte Fehlerbehandlung.",
                    "potential_improvement": "50-80% weniger Fehler",
                    "action": "improve_error_handling"
                })
        
        # Nutzungsmuster-Analyse
        usage_by_hour = defaultdict(int)
        for event in self.usage_data[-50:]:  # Letzte 50 Events
            if 'hour_of_day' in event:
                usage_by_hour[event['hour_of_day']] += 1
        
        if usage_by_hour:
            peak_hour = max(usage_by_hour, key=usage_by_hour.get)
            suggestions.append({
                "type": "usage_optimization",
                "priority": "low",
                "suggestion": f"Hauptnutzungszeit: {peak_hour}:00 Uhr. Planen Sie wartungsintensive Aufgaben außerhalb dieser Zeit.",
                "potential_improvement": "Bessere Systemverfügbarkeit",
                "action": "schedule_maintenance"
            })
        
        self.optimization_suggestions = suggestions
        return suggestions
    
    def get_performance_forecast(self, days_ahead=7):
        """Erstellt Performance-Prognose für die nächsten Tage"""
        if 'performance_predictor' not in self.models:
            return None
        
        forecast = {}
        current_time = datetime.now()
        
        # Durchschnittliche Dateigröße der letzten Bearbeitungen
        recent_sizes = self.performance_metrics["file_sizes"][-10:] if self.performance_metrics["file_sizes"] else [1024*1024]
        avg_file_size = np.mean(recent_sizes)
        
        for day in range(days_ahead):
            future_date = current_time + timedelta(days=day)
            
            # Vorhersagen für verschiedene Tageszeiten
            daily_predictions = {}
            for hour in [9, 12, 15, 18]:  # Arbeitszeiten
                prediction_time = future_date.replace(hour=hour, minute=0, second=0)
                predicted_duration = self.predict_processing_time(avg_file_size, prediction_time)
                
                if predicted_duration:
                    daily_predictions[f"{hour}:00"] = predicted_duration
            
            if daily_predictions:
                forecast[future_date.strftime("%Y-%m-%d")] = daily_predictions
        
        return forecast
    
    def optimize_workflow_parameters(self):
        """Optimiert Workflow-Parameter basierend auf ML-Erkenntnissen"""
        optimizations = {}
        
        # OCR-Parameter optimieren
        if len(self.performance_metrics["ocr_times"]) > 20:
            ocr_times = np.array(self.performance_metrics["ocr_times"][-20:])
            file_sizes = np.array(self.performance_metrics["file_sizes"][-20:])
            
            # Korrelation zwischen Dateigröße und OCR-Zeit
            if len(file_sizes) == len(ocr_times):
                correlation = np.corrcoef(file_sizes, ocr_times)[0, 1]
                
                if correlation > 0.7:  # Starke Korrelation
                    optimizations["ocr_batch_size"] = min(10, max(1, int(20 / correlation)))
                    optimizations["ocr_parallel_threads"] = min(4, max(1, int(correlation * 4)))
        
        # Memory Management optimieren
        if len(self.performance_metrics["memory_usage"]) > 10:
            memory_usage = np.array(self.performance_metrics["memory_usage"][-10:])
            max_memory = np.max(memory_usage)
            avg_memory = np.mean(memory_usage)
            
            if max_memory > avg_memory * 2:  # Speicher-Spitzen
                optimizations["garbage_collection_frequency"] = "high"
                optimizations["memory_cleanup_threshold"] = int(avg_memory * 1.5)
        
        # Adaptive Threading
        cpu_usage = self.performance_metrics["cpu_usage"][-10:] if self.performance_metrics["cpu_usage"] else [50]
        avg_cpu = np.mean(cpu_usage)
        
        if avg_cpu < 50:  # CPU unterausgelastet
            optimizations["max_worker_threads"] = min(8, max(2, int((100 - avg_cpu) / 20)))
        elif avg_cpu > 80:  # CPU überlastet
            optimizations["max_worker_threads"] = max(1, int(4 * (100 - avg_cpu) / 100))
        
        return optimizations
    
    def create_performance_report(self):
        """Erstellt detaillierten Performance-Report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "data_points": len(self.usage_data),
            "performance_summary": {},
            "trends": {},
            "recommendations": self.generate_smart_suggestions(),
            "forecasts": self.get_performance_forecast(),
            "optimizations": self.optimize_workflow_parameters()
        }
        
        # Performance Summary
        if self.performance_metrics["ocr_times"]:
            report["performance_summary"]["avg_ocr_time"] = np.mean(self.performance_metrics["ocr_times"])
            report["performance_summary"]["max_ocr_time"] = np.max(self.performance_metrics["ocr_times"])
        
        if self.performance_metrics["memory_usage"]:
            report["performance_summary"]["avg_memory_usage"] = np.mean(self.performance_metrics["memory_usage"])
            report["performance_summary"]["peak_memory_usage"] = np.max(self.performance_metrics["memory_usage"])
        
        # Trends berechnen
        if len(self.performance_metrics["ocr_times"]) > 5:
            recent_times = self.performance_metrics["ocr_times"][-5:]
            older_times = self.performance_metrics["ocr_times"][-10:-5] if len(self.performance_metrics["ocr_times"]) >= 10 else recent_times
            
            if older_times:
                trend = (np.mean(recent_times) - np.mean(older_times)) / np.mean(older_times) * 100
                report["trends"]["ocr_performance_trend"] = f"{trend:+.1f}%"
        
        return report
    
    def auto_train_models(self):
        """Automatisches Training der ML-Modelle"""
        def train_periodically():
            while True:
                time.sleep(3600)  # Jede Stunde
                if len(self.usage_data) >= 50:
                    print("Automatisches ML-Training gestartet...")
                    self.train_performance_predictor()
                    self.train_anomaly_detector()
                    print("ML-Training abgeschlossen")
        
        training_thread = threading.Thread(target=train_periodically, daemon=True)
        training_thread.start()
    
    def save_models(self):
        """Speichert trainierte ML-Modelle"""
        try:
            model_data = {
                'models': self.models,
                'scalers': self.scalers,
                'anomaly_detector': self.anomaly_detector
            }
            
            with open('ml_models.pkl', 'wb') as f:
                pickle.dump(model_data, f)
                
        except Exception as e:
            print(f"Fehler beim Speichern der ML-Modelle: {e}")
    
    def load_models(self):
        """Lädt gespeicherte ML-Modelle"""
        try:
            with open('ml_models.pkl', 'rb') as f:
                model_data = pickle.load(f)
                
            self.models = model_data.get('models', {})
            self.scalers = model_data.get('scalers', {})
            self.anomaly_detector = model_data.get('anomaly_detector', None)
            
            print("ML-Modelle erfolgreich geladen")
            
        except FileNotFoundError:
            print("Keine gespeicherten ML-Modelle gefunden")
        except Exception as e:
            print(f"Fehler beim Laden der ML-Modelle: {e}")

class PerformanceLogger:
    """Decorator und Context Manager für Performance-Logging"""
    
    def __init__(self, ml_optimizer: MLOptimizer):
        self.ml_optimizer = ml_optimizer
        
    def __call__(self, event_type):
        """Decorator für Funktionen"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                error_occurred = False
                
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    error_occurred = True
                    raise e
                finally:
                    duration = time.time() - start_time
                    
                    # Zusätzliche Metriken sammeln
                    file_size = kwargs.get('file_size', None)
                    
                    self.ml_optimizer.log_usage_event(
                        event_type=event_type,
                        duration=duration,
                        file_size=file_size,
                        error_occurred=error_occurred
                    )
            
            return wrapper
        return decorator
    
    def __enter__(self):
        """Context Manager Entry"""
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context Manager Exit"""
        duration = time.time() - self.start_time
        error_occurred = exc_type is not None
        
        self.ml_optimizer.log_usage_event(
            event_type="context_operation",
            duration=duration,
            error_occurred=error_occurred
        )

# Global ML Optimizer Instance
ml_optimizer = MLOptimizer()
performance_logger = PerformanceLogger(ml_optimizer)

def initialize_ml_optimizer():
    """Initialisiert ML Optimizer"""
    ml_optimizer.load_models()
    ml_optimizer.auto_train_models()
    
    # Initiales Training wenn genug Daten vorhanden
    if len(ml_optimizer.usage_data) >= 20:
        ml_optimizer.train_performance_predictor()
        ml_optimizer.train_anomaly_detector()

def get_performance_insights():
    """Holt aktuelle Performance-Insights"""
    return ml_optimizer.create_performance_report()

def log_performance(event_type, **kwargs):
    """Einfache Funktion zum Performance-Logging"""
    ml_optimizer.log_usage_event(event_type, **kwargs)

# Beispiel-Verwendung als Decorator
@performance_logger("ocr_processing")
def example_ocr_function(file_path, dpi=150):
    """Beispiel OCR-Funktion mit Performance-Logging"""
    time.sleep(2)  # Simuliert OCR-Verarbeitung
    return f"OCR completed for {file_path}"

# Beispiel-Verwendung als Context Manager
def example_with_context():
    """Beispiel mit Context Manager"""
    with performance_logger:
        time.sleep(1)  # Simuliert Operation
        return "Operation completed"

if __name__ == "__main__":
    # Test des ML Optimizers
    initialize_ml_optimizer()
    
    # Simuliere einige Ereignisse
    for i in range(25):
        ml_optimizer.log_usage_event(
            event_type="ocr_processing",
            duration=np.random.normal(3.0, 0.5),
            file_size=np.random.randint(1024*1024, 10*1024*1024),
            memory_usage=np.random.randint(100, 600),
            cpu_usage=np.random.randint(20, 90)
        )
    
    # Trainiere Modelle
    print("Training ML models...")
    ml_optimizer.train_performance_predictor()
    ml_optimizer.train_anomaly_detector()
    
    # Generiere Report
    report = ml_optimizer.create_performance_report()
    print("\nPerformance Report:")
    print(json.dumps(report, indent=2, ensure_ascii=False, default=str))
    
    # Test Vorhersage
    prediction = ml_optimizer.predict_processing_time(5*1024*1024)
    print(f"\nVorhersage für 5MB Datei: {prediction:.2f} Sekunden")
    
    # Test Anomalieerkennung
    is_anomaly = ml_optimizer.detect_performance_anomalies(10.0, 1024*1024, 200)
    print(f"Anomalie erkannt: {is_anomaly}")
    
    # Speichere Modelle
    ml_optimizer.save_models()
