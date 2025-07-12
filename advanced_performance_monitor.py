#!/usr/bin/env python3
"""
Performance Monitor for Checker Application
Continuous monitoring of system health, memory usage, and performance metrics
"""

import time
import psutil
import threading
import json
import os
from datetime import datetime, timedelta
import gc
import sys
from pathlib import Path

class PerformanceMonitor:
    def __init__(self, log_interval=60, max_log_days=30):
        self.log_interval = log_interval  # seconds
        self.max_log_days = max_log_days
        self.monitoring = False
        self.monitor_thread = None
        self.performance_data = []
        self.log_file = f"logs/performance_{datetime.now().strftime('%Y%m%d')}.json"
        
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        # Performance thresholds
        self.thresholds = {
            'memory_mb': 500,  # MB
            'cpu_percent': 80,  # %
            'disk_usage_percent': 90,  # %
            'thread_count': 50
        }
        
    def start_monitoring(self):
        """Start continuous performance monitoring"""
        if self.monitoring:
            print("⚠️ Monitoring already active")
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("📊 Performance monitoring started")
        
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        print("📊 Performance monitoring stopped")
        
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                metrics = self._collect_metrics()
                self.performance_data.append(metrics)
                self._log_metrics(metrics)
                self._check_thresholds(metrics)
                
                # Keep only last 1000 entries in memory
                if len(self.performance_data) > 1000:
                    self.performance_data = self.performance_data[-1000:]
                    
                time.sleep(self.log_interval)
                
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                time.sleep(self.log_interval)
                
    def _collect_metrics(self):
        """Collect current system metrics"""
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('.')
            
            # Process metrics (Python processes)
            python_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
                try:
                    if 'python' in proc.info['name'].lower():
                        python_processes.append({
                            'pid': proc.info['pid'],
                            'memory_mb': proc.info['memory_info'].rss / 1024 / 1024,
                            'cpu_percent': proc.info['cpu_percent']
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Thread count
            thread_count = threading.active_count()
            
            # Garbage collection stats
            gc_stats = {
                'collected': gc.get_count(),
                'threshold': gc.get_threshold()
            }
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'system': {
                    'cpu_percent': cpu_percent,
                    'memory_total_gb': memory.total / (1024**3),
                    'memory_used_gb': memory.used / (1024**3),
                    'memory_percent': memory.percent,
                    'disk_total_gb': disk.total / (1024**3),
                    'disk_used_gb': disk.used / (1024**3),
                    'disk_percent': (disk.used / disk.total) * 100
                },
                'python': {
                    'processes': python_processes,
                    'thread_count': thread_count,
                    'gc_stats': gc_stats
                }
            }
            
            return metrics
            
        except Exception as e:
            print(f"❌ Error collecting metrics: {e}")
            return None
            
    def _log_metrics(self, metrics):
        """Log metrics to file"""
        if not metrics:
            return
            
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                json.dump(metrics, f)
                f.write('\n')
        except Exception as e:
            print(f"❌ Error logging metrics: {e}")
            
    def _check_thresholds(self, metrics):
        """Check if any thresholds are exceeded"""
        if not metrics:
            return
            
        alerts = []
        
        # Check system memory
        if metrics['system']['memory_percent'] > self.thresholds['memory_mb']:
            alerts.append(f"High memory usage: {metrics['system']['memory_percent']:.1f}%")
            
        # Check CPU
        if metrics['system']['cpu_percent'] > self.thresholds['cpu_percent']:
            alerts.append(f"High CPU usage: {metrics['system']['cpu_percent']:.1f}%")
            
        # Check disk usage
        if metrics['system']['disk_percent'] > self.thresholds['disk_usage_percent']:
            alerts.append(f"High disk usage: {metrics['system']['disk_percent']:.1f}%")
            
        # Check thread count
        if metrics['python']['thread_count'] > self.thresholds['thread_count']:
            alerts.append(f"High thread count: {metrics['python']['thread_count']}")
            
        # Check Python process memory
        for proc in metrics['python']['processes']:
            if proc['memory_mb'] > 200:  # 200MB per process
                alerts.append(f"High process memory PID {proc['pid']}: {proc['memory_mb']:.1f}MB")
                
        if alerts:
            timestamp = datetime.now().strftime('%H:%M:%S')
            print(f"⚠️ [{timestamp}] Performance alerts:")
            for alert in alerts:
                print(f"   {alert}")
                
    def get_performance_summary(self, hours=24):
        """Get performance summary for the last N hours"""
        if not self.performance_data:
            return "No performance data available"
            
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_data = [
            entry for entry in self.performance_data 
            if datetime.fromisoformat(entry['timestamp']) > cutoff_time
        ]
        
        if not recent_data:
            return f"No data available for the last {hours} hours"
            
        # Calculate averages
        cpu_avg = sum(entry['system']['cpu_percent'] for entry in recent_data) / len(recent_data)
        memory_avg = sum(entry['system']['memory_percent'] for entry in recent_data) / len(recent_data)
        thread_avg = sum(entry['python']['thread_count'] for entry in recent_data) / len(recent_data)
        
        # Find peaks
        cpu_max = max(entry['system']['cpu_percent'] for entry in recent_data)
        memory_max = max(entry['system']['memory_percent'] for entry in recent_data)
        thread_max = max(entry['python']['thread_count'] for entry in recent_data)
        
        summary = f"""
📊 PERFORMANCE SUMMARY (Last {hours} hours)
{'='*50}
Data Points: {len(recent_data)}
Time Range: {recent_data[0]['timestamp'][:19]} to {recent_data[-1]['timestamp'][:19]}

💻 CPU Usage:
   Average: {cpu_avg:.1f}%
   Peak: {cpu_max:.1f}%
   
🧠 Memory Usage:
   Average: {memory_avg:.1f}%
   Peak: {memory_max:.1f}%
   
🧵 Thread Count:
   Average: {thread_avg:.1f}
   Peak: {thread_max}
   
🔍 Current Status:
   CPU: {recent_data[-1]['system']['cpu_percent']:.1f}%
   Memory: {recent_data[-1]['system']['memory_percent']:.1f}%
   Threads: {recent_data[-1]['python']['thread_count']}
"""
        return summary
        
    def detect_memory_leaks(self, threshold_increase=50):
        """Detect potential memory leaks"""
        if len(self.performance_data) < 10:
            return "Insufficient data for leak detection"
            
        # Analyze memory trends
        memory_values = [entry['system']['memory_percent'] for entry in self.performance_data[-100:]]
        
        if len(memory_values) < 10:
            return "Insufficient data for trend analysis"
            
        # Simple trend detection: compare first and last quartiles
        first_quarter = memory_values[:len(memory_values)//4]
        last_quarter = memory_values[-len(memory_values)//4:]
        
        avg_first = sum(first_quarter) / len(first_quarter)
        avg_last = sum(last_quarter) / len(last_quarter)
        
        increase = avg_last - avg_first
        
        if increase > threshold_increase:
            return f"⚠️ Potential memory leak detected: {increase:.1f}% increase over time"
        else:
            return f"✅ No significant memory leaks detected (trend: {increase:+.1f}%)"
            
    def cleanup_old_logs(self):
        """Clean up old performance logs"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.max_log_days)
            logs_dir = Path("logs")
            
            if not logs_dir.exists():
                return
                
            deleted_count = 0
            for log_file in logs_dir.glob("performance_*.json"):
                try:
                    # Extract date from filename
                    date_str = log_file.stem.split('_')[1]
                    file_date = datetime.strptime(date_str, '%Y%m%d')
                    
                    if file_date < cutoff_date:
                        log_file.unlink()
                        deleted_count += 1
                        
                except (ValueError, IndexError):
                    continue
                    
            if deleted_count > 0:
                print(f"🧹 Cleaned up {deleted_count} old performance logs")
                
        except Exception as e:
            print(f"❌ Error cleaning up logs: {e}")

def main():
    """Main performance monitoring interface"""
    monitor = PerformanceMonitor()
    
    print("🚀 Checker Application Performance Monitor")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "start":
            print("Starting continuous monitoring...")
            monitor.start_monitoring()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n⏹️ Stopping monitor...")
                monitor.stop_monitoring()
                
        elif command == "summary":
            hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24
            print(monitor.get_performance_summary(hours))
            
        elif command == "leaks":
            print(monitor.detect_memory_leaks())
            
        elif command == "cleanup":
            monitor.cleanup_old_logs()
            
        else:
            print(f"❌ Unknown command: {command}")
            
    else:
        # Interactive mode
        print("\nAvailable commands:")
        print("1. start - Start continuous monitoring")
        print("2. summary [hours] - Show performance summary")
        print("3. leaks - Check for memory leaks")
        print("4. cleanup - Clean old logs")
        print("5. quick - Quick system check")
        
        while True:
            try:
                choice = input("\nEnter command (or 'quit'): ").strip().lower()
                
                if choice == 'quit':
                    break
                elif choice == 'start':
                    monitor.start_monitoring()
                    print("Monitoring started. Press Ctrl+C to stop.")
                    try:
                        while monitor.monitoring:
                            time.sleep(1)
                    except KeyboardInterrupt:
                        monitor.stop_monitoring()
                elif choice.startswith('summary'):
                    hours = 24
                    if ' ' in choice:
                        try:
                            hours = int(choice.split()[1])
                        except ValueError:
                            pass
                    print(monitor.get_performance_summary(hours))
                elif choice == 'leaks':
                    print(monitor.detect_memory_leaks())
                elif choice == 'cleanup':
                    monitor.cleanup_old_logs()
                elif choice == 'quick':
                    metrics = monitor._collect_metrics()
                    if metrics:
                        print(f"\n📊 Current System State:")
                        print(f"CPU: {metrics['system']['cpu_percent']:.1f}%")
                        print(f"Memory: {metrics['system']['memory_percent']:.1f}%")
                        print(f"Threads: {metrics['python']['thread_count']}")
                        print(f"Python processes: {len(metrics['python']['processes'])}")
                else:
                    print("❌ Unknown command")
                    
            except KeyboardInterrupt:
                break
                
    print("👋 Performance monitor stopped")

if __name__ == "__main__":
    main()
