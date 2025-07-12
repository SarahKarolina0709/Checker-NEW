"""
Performance tests for CheckerApp.
Tests performance characteristics and benchmarks.
"""

import unittest
import sys
import time
import gc
import threading
from pathlib import Path
from unittest.mock import MagicMock, patch
import concurrent.futures

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Test imports with fallbacks
try:
    from view_stack import ViewStack, EnhancedViewStack
    VIEWSTACK_AVAILABLE = True
except ImportError:
    VIEWSTACK_AVAILABLE = False

try:
    import customtkinter as ctk
    CTK_AVAILABLE = True
except ImportError:
    CTK_AVAILABLE = False


class TestPerformance(unittest.TestCase):
    """Performance tests for key components."""
    
    def setUp(self):
        """Set up performance testing environment."""
        self.performance_data = {}
        gc.collect()  # Clean up before each test
    
    def tearDown(self):
        """Clean up after performance tests."""
        # Log performance data if needed
        if self.performance_data:
            print(f"Performance data: {self.performance_data}")
    
    def benchmark_execution_time(self, func, *args, **kwargs):
        """Benchmark function execution time."""
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        return result, execution_time
    
    def benchmark_memory_usage(self, func, *args, **kwargs):
        """Benchmark memory usage during function execution."""
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        result = func(*args, **kwargs)
        
        gc.collect()
        final_objects = len(gc.get_objects())
        
        memory_delta = final_objects - initial_objects
        return result, memory_delta

    @unittest.skipUnless(VIEWSTACK_AVAILABLE, "ViewStack not available")
    def test_viewstack_switching_performance(self):
        """Test ViewStack switching performance."""
        # Create mock root
        mock_root = MagicMock()
        
        # Create ViewStack
        viewstack = EnhancedViewStack(mock_root)
        
        # Add multiple views
        num_views = 100
        for i in range(num_views):
            view = MagicMock()
            viewstack.add(f'view_{i}', view)
        
        # Benchmark switching between views
        switch_times = []
        for i in range(50):  # 50 random switches
            view_name = f'view_{i % num_views}'
            _, exec_time = self.benchmark_execution_time(viewstack.show, view_name)
            switch_times.append(exec_time)
        
        # Performance assertions
        avg_switch_time = sum(switch_times) / len(switch_times)
        max_switch_time = max(switch_times)
        
        # ViewStack should maintain O(1) performance
        self.assertLess(avg_switch_time, 0.001)  # Average < 1ms
        self.assertLess(max_switch_time, 0.005)  # Max < 5ms
        
        self.performance_data['viewstack_avg_switch_time'] = avg_switch_time
        self.performance_data['viewstack_max_switch_time'] = max_switch_time

    @unittest.skipUnless(CTK_AVAILABLE, "CustomTkinter not available")
    def test_widget_creation_performance(self):
        """Test widget creation performance."""
        # Create root window
        root = ctk.CTk()
        root.withdraw()
        
        try:
            # Benchmark widget creation
            widget_creation_times = []
            widget_types = [
                ctk.CTkFrame,
                ctk.CTkLabel,
                ctk.CTkButton,
                ctk.CTkEntry,
                ctk.CTkTextbox
            ]
            
            for widget_type in widget_types:
                # Create multiple widgets of each type
                widgets = []
                start_time = time.perf_counter()
                
                for i in range(20):
                    if widget_type == ctk.CTkLabel:
                        widget = widget_type(root, text=f"Label {i}")
                    elif widget_type == ctk.CTkButton:
                        widget = widget_type(root, text=f"Button {i}")
                    elif widget_type == ctk.CTkEntry:
                        widget = widget_type(root, placeholder_text=f"Entry {i}")
                    else:
                        widget = widget_type(root)
                    
                    widgets.append(widget)
                
                end_time = time.perf_counter()
                creation_time = end_time - start_time
                widget_creation_times.append(creation_time)
                
                # Clean up widgets
                for widget in widgets:
                    widget.destroy()
            
            # Performance assertions
            avg_creation_time = sum(widget_creation_times) / len(widget_creation_times)
            self.assertLess(avg_creation_time, 0.1)  # Should be under 100ms for 20 widgets
            
            self.performance_data['widget_creation_avg_time'] = avg_creation_time
            
        finally:
            root.destroy()

    def test_data_processing_performance(self):
        """Test data processing performance."""
        # Test large data processing
        large_dataset = list(range(10000))
        
        # Benchmark data processing operations
        operations = {
            'filter': lambda data: [x for x in data if x % 2 == 0],
            'map': lambda data: [x * 2 for x in data],
            'reduce': lambda data: sum(data),
            'sort': lambda data: sorted(data, reverse=True)
        }
        
        operation_times = {}
        for op_name, op_func in operations.items():
            _, exec_time = self.benchmark_execution_time(op_func, large_dataset)
            operation_times[op_name] = exec_time
        
        # Performance assertions
        for op_name, exec_time in operation_times.items():
            self.assertLess(exec_time, 1.0)  # Should be under 1 second
        
        self.performance_data['data_processing_times'] = operation_times

    def test_memory_efficiency(self):
        """Test memory efficiency of components."""
        # Test memory usage patterns
        def create_large_structure():
            """Create a large data structure."""
            return {
                'data': list(range(1000)),
                'nested': {
                    'level1': {
                        'level2': list(range(500))
                    }
                },
                'strings': [f"string_{i}" for i in range(200)]
            }
        
        # Benchmark memory usage
        _, memory_delta = self.benchmark_memory_usage(create_large_structure)
        
        # Clean up and verify memory is released
        gc.collect()
        
        # Memory usage should be reasonable
        self.assertLess(memory_delta, 5000)  # Less than 5000 new objects
        
        self.performance_data['memory_delta'] = memory_delta

    def test_concurrent_operations_performance(self):
        """Test performance under concurrent operations."""
        # Test concurrent data processing
        def worker_function(data_chunk):
            """Worker function for concurrent processing."""
            return sum(x * 2 for x in data_chunk)
        
        # Create test data
        large_data = list(range(10000))
        chunk_size = 1000
        data_chunks = [large_data[i:i+chunk_size] for i in range(0, len(large_data), chunk_size)]
        
        # Sequential processing benchmark
        start_time = time.perf_counter()
        sequential_results = [worker_function(chunk) for chunk in data_chunks]
        sequential_time = time.perf_counter() - start_time
        
        # Concurrent processing benchmark
        start_time = time.perf_counter()
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            concurrent_results = list(executor.map(worker_function, data_chunks))
        concurrent_time = time.perf_counter() - start_time
        
        # Verify results are the same
        self.assertEqual(sequential_results, concurrent_results)
        
        # Concurrent processing should be faster (or at least not significantly slower)
        performance_ratio = concurrent_time / sequential_time
        self.assertLess(performance_ratio, 2.0)  # Should not be more than 2x slower
        
        self.performance_data['sequential_time'] = sequential_time
        self.performance_data['concurrent_time'] = concurrent_time
        self.performance_data['performance_ratio'] = performance_ratio

    def test_scaling_performance(self):
        """Test performance scaling with different data sizes."""
        # Test scaling with different data sizes
        data_sizes = [100, 500, 1000, 5000, 10000]
        processing_times = []
        
        for size in data_sizes:
            test_data = list(range(size))
            _, exec_time = self.benchmark_execution_time(
                lambda data: [x * 2 for x in data if x % 2 == 0],
                test_data
            )
            processing_times.append(exec_time)
        
        # Performance should scale reasonably (not exponentially)
        # Check that doubling the data size doesn't quadruple the time
        for i in range(1, len(processing_times)):
            size_ratio = data_sizes[i] / data_sizes[i-1]
            time_ratio = processing_times[i] / processing_times[i-1]
            
            # Time ratio should not be much larger than size ratio
            self.assertLess(time_ratio, size_ratio * 2)
        
        self.performance_data['scaling_data'] = {
            'sizes': data_sizes,
            'times': processing_times
        }

    def test_repeated_operations_performance(self):
        """Test performance consistency across repeated operations."""
        # Test repeated operations for consistency
        def test_operation():
            """Test operation to repeat."""
            data = list(range(1000))
            return sum(x * 2 for x in data)
        
        # Repeat operation multiple times
        execution_times = []
        for _ in range(100):
            _, exec_time = self.benchmark_execution_time(test_operation)
            execution_times.append(exec_time)
        
        # Calculate statistics
        avg_time = sum(execution_times) / len(execution_times)
        min_time = min(execution_times)
        max_time = max(execution_times)
        
        # Performance should be consistent
        variance = max_time - min_time
        self.assertLess(variance, avg_time * 2)  # Variance should be reasonable
        
        self.performance_data['repeated_operations'] = {
            'avg_time': avg_time,
            'min_time': min_time,
            'max_time': max_time,
            'variance': variance
        }

    def test_resource_cleanup_performance(self):
        """Test resource cleanup performance."""
        # Test resource creation and cleanup
        def create_and_cleanup_resources():
            """Create and cleanup resources."""
            resources = []
            
            # Create resources
            for i in range(100):
                resource = {
                    'id': i,
                    'data': list(range(100)),
                    'cleanup_callback': lambda: None
                }
                resources.append(resource)
            
            # Cleanup resources
            for resource in resources:
                resource['cleanup_callback']()
            
            return len(resources)
        
        # Benchmark resource lifecycle
        _, exec_time = self.benchmark_execution_time(create_and_cleanup_resources)
        
        # Resource cleanup should be fast
        self.assertLess(exec_time, 0.1)  # Should be under 100ms
        
        self.performance_data['resource_cleanup_time'] = exec_time

    def test_ui_responsiveness_simulation(self):
        """Test UI responsiveness simulation."""
        # Simulate UI update operations
        def simulate_ui_updates():
            """Simulate UI update operations."""
            updates = []
            
            # Simulate multiple UI updates
            for i in range(50):
                # Simulate widget update
                update = {
                    'widget_id': f'widget_{i}',
                    'property': 'text',
                    'value': f'Updated text {i}',
                    'timestamp': time.time()
                }
                updates.append(update)
                
                # Simulate small delay (like real UI updates)
                time.sleep(0.001)
            
            return updates
        
        # Benchmark UI simulation
        _, exec_time = self.benchmark_execution_time(simulate_ui_updates)
        
        # UI updates should be responsive
        self.assertLess(exec_time, 0.5)  # Should be under 500ms for 50 updates
        
        self.performance_data['ui_simulation_time'] = exec_time

    def test_startup_performance_simulation(self):
        """Test application startup performance simulation."""
        # Simulate application startup sequence
        def simulate_startup():
            """Simulate application startup."""
            startup_stages = []
            
            # Stage 1: Initialize configuration
            start_time = time.perf_counter()
            config = {'theme': 'light', 'language': 'de'}
            startup_stages.append(('config', time.perf_counter() - start_time))
            
            # Stage 2: Initialize UI components
            start_time = time.perf_counter()
            ui_components = ['menu', 'toolbar', 'main_area', 'status_bar']
            startup_stages.append(('ui_components', time.perf_counter() - start_time))
            
            # Stage 3: Initialize workflows
            start_time = time.perf_counter()
            workflows = ['angebots', 'pruefung', 'finalisierung', 'projekt']
            startup_stages.append(('workflows', time.perf_counter() - start_time))
            
            # Stage 4: Final setup
            start_time = time.perf_counter()
            final_setup = 'complete'
            startup_stages.append(('final_setup', time.perf_counter() - start_time))
            
            return startup_stages
        
        # Benchmark startup simulation
        stages, total_time = self.benchmark_execution_time(simulate_startup)
        
        # Startup should be fast
        self.assertLess(total_time, 0.1)  # Should be under 100ms
        
        # Individual stages should be fast
        for stage_name, stage_time in stages:
            self.assertLess(stage_time, 0.05)  # Each stage under 50ms
        
        self.performance_data['startup_simulation'] = {
            'total_time': total_time,
            'stages': dict(stages)
        }


class TestLoadTesting(unittest.TestCase):
    """Load testing for stress scenarios."""
    
    def test_high_volume_data_processing(self):
        """Test high volume data processing."""
        # Process large amounts of data
        data_sizes = [50000, 100000, 200000]
        
        for size in data_sizes:
            with self.subTest(size=size):
                test_data = list(range(size))
                
                start_time = time.perf_counter()
                processed_data = [x * 2 for x in test_data if x % 10 == 0]
                end_time = time.perf_counter()
                
                processing_time = end_time - start_time
                
                # Should handle large data reasonably well
                self.assertLess(processing_time, 5.0)  # Under 5 seconds
                self.assertGreater(len(processed_data), 0)

    def test_many_concurrent_operations(self):
        """Test many concurrent operations."""
        # Test with many concurrent threads
        def worker_task(task_id):
            """Worker task for concurrent testing."""
            result = sum(range(1000))
            return task_id, result
        
        # Run many tasks concurrently
        num_tasks = 50
        
        start_time = time.perf_counter()
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_task = {executor.submit(worker_task, i): i for i in range(num_tasks)}
            results = []
            
            for future in concurrent.futures.as_completed(future_to_task):
                task_id = future_to_task[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    self.fail(f"Task {task_id} failed: {e}")
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        
        # Should complete all tasks
        self.assertEqual(len(results), num_tasks)
        
        # Should be reasonably fast
        self.assertLess(total_time, 10.0)  # Under 10 seconds

    def test_memory_stress(self):
        """Test memory usage under stress."""
        # Create and destroy many objects
        object_count = 10000
        
        start_time = time.perf_counter()
        
        # Create many objects
        objects = []
        for i in range(object_count):
            obj = {
                'id': i,
                'data': list(range(10)),
                'metadata': f'object_{i}'
            }
            objects.append(obj)
        
        # Verify objects were created
        self.assertEqual(len(objects), object_count)
        
        # Clear objects
        objects.clear()
        
        # Force garbage collection
        gc.collect()
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        
        # Should handle memory operations efficiently
        self.assertLess(total_time, 2.0)  # Under 2 seconds


if __name__ == '__main__':
    unittest.main()
