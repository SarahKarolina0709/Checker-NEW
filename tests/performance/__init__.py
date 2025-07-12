"""
Performance tests package initialization.
"""

# Performance test configuration
PERFORMANCE_CONFIG = {
    'max_execution_time': 10.0,  # Maximum execution time in seconds
    'max_memory_delta': 10000,   # Maximum memory delta in objects
    'concurrent_workers': 4,     # Number of concurrent workers
    'benchmark_iterations': 100  # Number of benchmark iterations
}

# Performance thresholds
PERFORMANCE_THRESHOLDS = {
    'viewstack_switch_time': 0.001,  # 1ms
    'widget_creation_time': 0.1,     # 100ms
    'data_processing_time': 1.0,     # 1 second
    'startup_time': 0.5,             # 500ms
    'ui_update_time': 0.05           # 50ms
}

__all__ = ['PERFORMANCE_CONFIG', 'PERFORMANCE_THRESHOLDS']
