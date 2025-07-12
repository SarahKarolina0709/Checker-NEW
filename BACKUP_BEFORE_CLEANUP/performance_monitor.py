# -*- coding: utf-8 -*-
"""
Performance Monitor - Track and optimize translation office workflows
"""

import time
import json
import os
from datetime import datetime, timedelta
from collections import defaultdict, deque
import threading
from typing import Dict, List, Any

class PerformanceMonitor:
    def __init__(self):
        self.metrics_file = "performance_metrics.json"
        self.metrics = self._load_metrics()
        self.current_sessions = {}
        self.bottleneck_tracker = defaultdict(deque)
        
    def _load_metrics(self):
        """Load performance metrics from file"""
        try:
            if os.path.exists(self.metrics_file):
                with open(self.metrics_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        
        return {
            "workflow_times": {},
            "bottlenecks": {},
            "optimization_suggestions": [],
            "daily_stats": {},
            "file_processing_times": {},
            "memory_usage": {},
            "last_updated": datetime.now().isoformat()
        }
    
    def start_workflow_timing(self, workflow_name: str, session_id: str = None):
        """Start timing a workflow"""
        if session_id is None:
            session_id = f"{workflow_name}_{int(time.time())}"
        
        self.current_sessions[session_id] = {
            "workflow": workflow_name,
            "start_time": time.time(),
            "steps": {},
            "memory_start": self._get_memory_usage()
        }
        
        return session_id
    
    def log_workflow_step(self, session_id: str, step_name: str, duration: float = None):
        """Log a workflow step completion"""
        if session_id in self.current_sessions:
            if duration is None:
                duration = time.time() - self.current_sessions[session_id]["start_time"]
            
            self.current_sessions[session_id]["steps"][step_name] = {
                "duration": duration,
                "timestamp": datetime.now().isoformat()
            }
    
    def end_workflow_timing(self, session_id: str):
        """End workflow timing and save metrics"""
        if session_id not in self.current_sessions:
            return
        
        session = self.current_sessions[session_id]
        workflow_name = session["workflow"]
        total_duration = time.time() - session["start_time"]
        
        # Initialize workflow metrics if not exists
        if workflow_name not in self.metrics["workflow_times"]:
            self.metrics["workflow_times"][workflow_name] = {
                "executions": [],
                "average_duration": 0,
                "step_averages": {},
                "bottleneck_steps": []
            }
        
        # Add execution data
        execution_data = {
            "duration": total_duration,
            "timestamp": datetime.now().isoformat(),
            "steps": session["steps"],
            "memory_usage": self._get_memory_usage() - session["memory_start"]
        }
        
        self.metrics["workflow_times"][workflow_name]["executions"].append(execution_data)
        
        # Keep only last 100 executions
        if len(self.metrics["workflow_times"][workflow_name]["executions"]) > 100:
            self.metrics["workflow_times"][workflow_name]["executions"] = \
                self.metrics["workflow_times"][workflow_name]["executions"][-100:]
        
        # Update averages
        self._update_averages(workflow_name)
        
        # Detect bottlenecks
        self._detect_bottlenecks(workflow_name, session["steps"])
        
        # Clean up session
        del self.current_sessions[session_id]
        
        # Save metrics
        self._save_metrics()
    
    def _update_averages(self, workflow_name: str):
        """Update average durations for workflow and steps"""
        executions = self.metrics["workflow_times"][workflow_name]["executions"]
        
        if not executions:
            return
        
        # Overall average
        total_durations = [ex["duration"] for ex in executions]
        self.metrics["workflow_times"][workflow_name]["average_duration"] = sum(total_durations) / len(total_durations)
        
        # Step averages
        step_totals = defaultdict(list)
        for execution in executions:
            for step_name, step_data in execution["steps"].items():
                step_totals[step_name].append(step_data["duration"])
        
        step_averages = {}
        for step_name, durations in step_totals.items():
            step_averages[step_name] = sum(durations) / len(durations)
        
        self.metrics["workflow_times"][workflow_name]["step_averages"] = step_averages
    
    def _detect_bottlenecks(self, workflow_name: str, steps: Dict[str, Any]):
        """Detect performance bottlenecks"""
        step_averages = self.metrics["workflow_times"][workflow_name].get("step_averages", {})
        
        bottlenecks = []
        for step_name, step_data in steps.items():
            if step_name in step_averages:
                average_duration = step_averages[step_name]
                current_duration = step_data["duration"]
                
                # If current duration is 50% longer than average, it's a bottleneck
                if current_duration > average_duration * 1.5:
                    bottlenecks.append({
                        "step": step_name,
                        "current_duration": current_duration,
                        "average_duration": average_duration,
                        "slowdown_factor": current_duration / average_duration
                    })
        
        if bottlenecks:
            self.metrics["workflow_times"][workflow_name]["bottleneck_steps"] = bottlenecks
            self._generate_optimization_suggestions(workflow_name, bottlenecks)
    
    def _generate_optimization_suggestions(self, workflow_name: str, bottlenecks: List[Dict]):
        """Generate optimization suggestions based on bottlenecks"""
        suggestions = []
        
        for bottleneck in bottlenecks:
            step_name = bottleneck["step"]
            
            if "ocr" in step_name.lower():
                suggestions.append({
                    "workflow": workflow_name,
                    "issue": f"OCR processing slow in {step_name}",
                    "suggestion": "Consider reducing OCR DPI or implementing parallel page processing",
                    "priority": "high" if bottleneck["slowdown_factor"] > 2 else "medium"
                })
            
            elif "ki" in step_name.lower() or "ai" in step_name.lower():
                suggestions.append({
                    "workflow": workflow_name,
                    "issue": f"KI analysis slow in {step_name}",
                    "suggestion": "Consider implementing KI result caching or batch processing",
                    "priority": "medium"
                })
            
            elif "languagetool" in step_name.lower():
                suggestions.append({
                    "workflow": workflow_name,
                    "issue": f"LanguageTool checking slow in {step_name}",
                    "suggestion": "Consider text segmentation or rule filtering",
                    "priority": "high" if bottleneck["slowdown_factor"] > 3 else "medium"
                })
            
            elif "file" in step_name.lower():
                suggestions.append({
                    "workflow": workflow_name,
                    "issue": f"File processing slow in {step_name}",
                    "suggestion": "Check file size limits and consider streaming for large files",
                    "priority": "high"
                })
        
        # Add unique suggestions to metrics
        for suggestion in suggestions:
            if suggestion not in self.metrics["optimization_suggestions"]:
                self.metrics["optimization_suggestions"].append(suggestion)
        
        # Keep only last 50 suggestions
        if len(self.metrics["optimization_suggestions"]) > 50:
            self.metrics["optimization_suggestions"] = self.metrics["optimization_suggestions"][-50:]
    
    def get_daily_stats(self, date_str: str = None):
        """Get daily performance statistics"""
        if date_str is None:
            date_str = datetime.now().strftime('%Y-%m-%d')
        
        if date_str not in self.metrics["daily_stats"]:
            self.metrics["daily_stats"][date_str] = {
                "workflows_completed": 0,
                "files_processed": 0,
                "average_processing_time": 0,
                "bottlenecks_detected": 0,
                "optimization_implemented": 0
            }
        
        return self.metrics["daily_stats"][date_str]
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        report = {
            "summary": {
                "total_workflows": len(self.metrics["workflow_times"]),
                "active_sessions": len(self.current_sessions),
                "pending_optimizations": len(self.metrics["optimization_suggestions"])
            },
            "workflow_performance": {},
            "bottlenecks": {},
            "recommendations": []
        }
        
        # Workflow performance summary
        for workflow_name, workflow_data in self.metrics["workflow_times"].items():
            if workflow_data["executions"]:
                recent_executions = workflow_data["executions"][-10:]  # Last 10
                avg_duration = sum(ex["duration"] for ex in recent_executions) / len(recent_executions)
                
                report["workflow_performance"][workflow_name] = {
                    "average_duration": avg_duration,
                    "total_executions": len(workflow_data["executions"]),
                    "slowest_step": max(workflow_data["step_averages"].items(), 
                                      key=lambda x: x[1], default=("N/A", 0))[0],
                    "efficiency_score": self._calculate_efficiency_score(workflow_data)
                }
        
        # Generate recommendations
        report["recommendations"] = self._generate_general_recommendations()
        
        return report
    
    def _calculate_efficiency_score(self, workflow_data: Dict) -> float:
        """Calculate efficiency score (0-100) for a workflow"""
        if not workflow_data["executions"]:
            return 0
        
        recent_executions = workflow_data["executions"][-10:]
        durations = [ex["duration"] for ex in recent_executions]
        
        # Calculate based on consistency and speed
        avg_duration = sum(durations) / len(durations)
        duration_variance = sum((d - avg_duration) ** 2 for d in durations) / len(durations)
        
        # Lower variance and shorter duration = higher score
        consistency_score = max(0, 100 - (duration_variance * 10))
        speed_score = max(0, 100 - (avg_duration * 5))  # Assuming 20s = 0 score
        
        return (consistency_score + speed_score) / 2
    
    def _generate_general_recommendations(self) -> List[Dict[str, str]]:
        """Generate general performance recommendations"""
        recommendations = []
        
        # Check for consistently slow workflows
        for workflow_name, workflow_data in self.metrics["workflow_times"].items():
            if workflow_data["average_duration"] > 60:  # Over 1 minute
                recommendations.append({
                    "type": "performance",
                    "priority": "high",
                    "message": f"{workflow_name} durchschnittlich über 1 Minute - Optimierung erforderlich"
                })
        
        # Check memory usage
        high_memory_workflows = []
        for workflow_name, workflow_data in self.metrics["workflow_times"].items():
            if workflow_data["executions"]:
                recent_memory = [ex.get("memory_usage", 0) for ex in workflow_data["executions"][-5:]]
                avg_memory = sum(recent_memory) / len(recent_memory) if recent_memory else 0
                
                if avg_memory > 500:  # Over 500MB
                    high_memory_workflows.append(workflow_name)
        
        if high_memory_workflows:
            recommendations.append({
                "type": "memory",
                "priority": "medium",
                "message": f"Hoher Speicherverbrauch in: {', '.join(high_memory_workflows)}"
            })
        
        return recommendations
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # Convert to MB
        except:
            return 0
    
    def _save_metrics(self):
        """Save metrics to file"""
        try:
            self.metrics["last_updated"] = datetime.now().isoformat()
            with open(self.metrics_file, 'w', encoding='utf-8') as f:
                json.dump(self.metrics, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving performance metrics: {e}")
    
    def start_monitoring(self):
        """Dummy-Methode für Kompatibilität (macht nichts)"""
        pass

# Global instance
performance_monitor = PerformanceMonitor()
