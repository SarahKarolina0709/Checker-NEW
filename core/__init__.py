"""
Core management systems for Checker Application
==============================================

This package provides centralized management systems that address
the logic issues identified in the comprehensive review:

- ThreadManager: Centralized thread lifecycle management
- StateManager: Unified state management with validation
- WorkflowFactory: Consistent workflow creation and lifecycle
"""

from .thread_manager import (
    ThreadManager,
    ThreadPriority,
    ThreadState,
    ThreadInfo,
    start_background_task,
    wait_for_task,
    stop_background_task,
    get_task_status,
    shutdown_all_threads
)

from .state_manager import (
    StateManager,
    StateChangeType,
    WorkflowState,
    StateValidator,
    WorkflowContext,
    get_state,
    set_state,
    get_current_workflow,
    set_current_workflow,
    get_project_data,
    set_project_data
)

from .workflow_factory import (
    WorkflowFactory,
    WorkflowType,
    WorkflowLifecycle,
    WorkflowConfig,
    WorkflowProtocol,
    create_workflow,
    release_workflow,
    cleanup_workflow,
    cleanup_all_workflows
)

from .memory_manager import (
    MemoryManager,
    MemoryThreshold,
    MemorySnapshot,
    ObjectTracker,
    track_large_object,
    untrack_object,
    get_memory_usage,
    force_memory_cleanup,
    add_memory_cleanup_callback
)

__all__ = [
    # Thread Management
    'ThreadManager',
    'ThreadPriority',
    'ThreadState',
    'ThreadInfo',
    'start_background_task',
    'wait_for_task',
    'stop_background_task',
    'get_task_status',
    'shutdown_all_threads',

    # State Management
    'StateManager',
    'StateChangeType',
    'WorkflowState',
    'StateValidator',
    'WorkflowContext',
    'get_state',
    'set_state',
    'get_current_workflow',
    'set_current_workflow',
    'get_project_data',
    'set_project_data',

    # Workflow Management
    'WorkflowFactory',
    'WorkflowType',
    'WorkflowLifecycle',
    'WorkflowConfig',
    'WorkflowProtocol',
    'create_workflow',
    'release_workflow',
    'cleanup_workflow',
    'cleanup_all_workflows',

    # Memory Management
    'MemoryManager',
    'MemoryThreshold',
    'MemorySnapshot',
    'ObjectTracker',
    'track_large_object',
    'untrack_object',
    'get_memory_usage',
    'force_memory_cleanup',
    'add_memory_cleanup_callback'
]

__version__ = "1.0.0"
__author__ = "Checker Application Logic Improvements"
