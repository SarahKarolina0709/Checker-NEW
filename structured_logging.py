# -*- coding: utf-8 -*-
"""
Structured Logging Module for CheckerApp
Provides workflow-aware logging with contextual information.
"""

import logging
import json
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, Union
import threading
from contextlib import contextmanager


class StructuredLogger:
    """Enhanced logger with structured context support."""
    
    def __init__(self, name: str, base_context: Optional[Dict[str, Any]] = None):
        self.logger = logging.getLogger(name)
        self.base_context = base_context or {}
        self._context_stack = threading.local()
    
    def _get_context_stack(self):
        """Get thread-local context stack."""
        if not hasattr(self._context_stack, 'stack'):
            self._context_stack.stack = []
        return self._context_stack.stack
    
    def _build_context(self, additional_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Build complete context from base, stack, and additional context."""
        context = self.base_context.copy()
        
        # Add stacked contexts
        for stack_context in self._get_context_stack():
            context.update(stack_context)
        
        # Add additional context
        if additional_context:
            context.update(additional_context)
        
        return context
    
    def _log_with_context(self, level: int, msg: str, context: Optional[Dict[str, Any]] = None, 
                         exc_info: bool = False, **kwargs):
        """Log with structured context."""
        extra_context = self._build_context(context)
        
        # Add timestamp and thread info
        extra_context.update({
            'timestamp': datetime.now().isoformat(),
            'thread_id': threading.current_thread().ident,
            'thread_name': threading.current_thread().name
        })
        
        # Add exception info if present
        if exc_info and not kwargs.get('exc_info'):
            kwargs['exc_info'] = True
        
        # Log with extra context
        self.logger.log(level, msg, extra=extra_context, **kwargs)
    
    def debug(self, msg: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        """Log debug message with context."""
        self._log_with_context(logging.DEBUG, msg, context, **kwargs)
    
    def info(self, msg: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        """Log info message with context."""
        self._log_with_context(logging.INFO, msg, context, **kwargs)
    
    def warning(self, msg: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        """Log warning message with context."""
        self._log_with_context(logging.WARNING, msg, context, **kwargs)
    
    def error(self, msg: str, context: Optional[Dict[str, Any]] = None, exc_info: bool = False, **kwargs):
        """Log error message with context."""
        self._log_with_context(logging.ERROR, msg, context, exc_info=exc_info, **kwargs)
    
    def critical(self, msg: str, context: Optional[Dict[str, Any]] = None, exc_info: bool = False, **kwargs):
        """Log critical message with context."""
        self._log_with_context(logging.CRITICAL, msg, context, exc_info=exc_info, **kwargs)
    
    @contextmanager
    def context(self, **context_data):
        """Context manager for adding contextual information to logs."""
        stack = self._get_context_stack()
        stack.append(context_data)
        try:
            yield
        finally:
            stack.pop()


class WorkflowLogger(StructuredLogger):
    """Specialized logger for workflow operations."""
    
    def __init__(self, name: str, workflow_name: str, base_context: Optional[Dict[str, Any]] = None):
        workflow_context = {'workflow': workflow_name}
        if base_context:
            workflow_context.update(base_context)
        super().__init__(name, workflow_context)
        self.workflow_name = workflow_name
    
    def workflow_started(self, **context):
        """Log workflow start event."""
        self.info(f"Workflow '{self.workflow_name}' started", context)
    
    def workflow_completed(self, **context):
        """Log workflow completion event."""
        self.info(f"Workflow '{self.workflow_name}' completed", context)
    
    def workflow_error(self, error_msg: str, **context):
        """Log workflow error event."""
        self.error(f"Workflow '{self.workflow_name}' error: {error_msg}", context, exc_info=True)
    
    def workflow_step(self, step_name: str, **context):
        """Log workflow step event."""
        step_context = {'step': step_name}
        step_context.update(context)
        self.info(f"Workflow step: {step_name}", step_context)
    
    def file_processed(self, file_path: str, **context):
        """Log file processing event."""
        file_context = {'file_path': file_path}
        file_context.update(context)
        self.info(f"File processed: {file_path}", file_context)
    
    def analysis_result(self, result_type: str, result_data: Dict[str, Any], **context):
        """Log analysis result event."""
        analysis_context = {
            'result_type': result_type,
            'result_data': result_data
        }
        analysis_context.update(context)
        self.info(f"Analysis result: {result_type}", analysis_context)


class PerformanceLogger(StructuredLogger):
    """Specialized logger for performance monitoring."""
    
    def __init__(self, name: str, base_context: Optional[Dict[str, Any]] = None):
        perf_context = {'category': 'performance'}
        if base_context:
            perf_context.update(base_context)
        super().__init__(name, perf_context)
    
    def memory_usage(self, usage_mb: float, component: str = None, **context):
        """Log memory usage event."""
        memory_context = {'memory_mb': usage_mb}
        if component:
            memory_context['component'] = component
        memory_context.update(context)
        self.info(f"Memory usage: {usage_mb:.2f}MB", memory_context)
    
    def execution_time(self, operation: str, duration_ms: float, **context):
        """Log execution time event."""
        time_context = {
            'operation': operation,
            'duration_ms': duration_ms
        }
        time_context.update(context)
        self.info(f"Execution time - {operation}: {duration_ms:.2f}ms", time_context)
    
    def cache_stats(self, cache_name: str, hits: int, misses: int, size: int, **context):
        """Log cache statistics event."""
        cache_context = {
            'cache_name': cache_name,
            'hits': hits,
            'misses': misses,
            'size': size,
            'hit_ratio': hits / (hits + misses) if (hits + misses) > 0 else 0
        }
        cache_context.update(context)
        self.info(f"Cache stats - {cache_name}: {hits}/{hits+misses} hits, {size} items", cache_context)


class UILogger(StructuredLogger):
    """Specialized logger for UI operations."""
    
    def __init__(self, name: str, base_context: Optional[Dict[str, Any]] = None):
        ui_context = {'category': 'ui'}
        if base_context:
            ui_context.update(base_context)
        super().__init__(name, ui_context)
    
    def component_initialized(self, component_name: str, **context):
        """Log UI component initialization."""
        comp_context = {'component': component_name}
        comp_context.update(context)
        self.info(f"UI component initialized: {component_name}", comp_context)
    
    def layout_updated(self, layout_type: str, parent: str = None, **context):
        """Log layout update event."""
        layout_context = {'layout_type': layout_type}
        if parent:
            layout_context['parent'] = parent
        layout_context.update(context)
        self.debug(f"Layout updated: {layout_type}", layout_context)
    
    def user_interaction(self, action: str, widget: str = None, **context):
        """Log user interaction event."""
        interaction_context = {'action': action}
        if widget:
            interaction_context['widget'] = widget
        interaction_context.update(context)
        self.info(f"User interaction: {action}", interaction_context)
    
    def theme_changed(self, new_theme: str, **context):
        """Log theme change event."""
        theme_context = {'new_theme': new_theme}
        theme_context.update(context)
        self.info(f"Theme changed to: {new_theme}", theme_context)


class StructuredLogFormatter(logging.Formatter):
    """Custom formatter for structured logging."""
    
    def __init__(self, include_context: bool = True):
        super().__init__()
        self.include_context = include_context
    
    def format(self, record):
        # Basic format
        formatted = f"{record.levelname} [{record.name}] {record.getMessage()}"
        
        # Add context if available and requested
        if self.include_context and hasattr(record, 'workflow'):
            formatted += f" [workflow: {record.workflow}]"
        
        if self.include_context and hasattr(record, 'component'):
            formatted += f" [component: {record.component}]"
        
        if self.include_context and hasattr(record, 'category'):
            formatted += f" [category: {record.category}]"
        
        # Add exception info if present
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"
        
        return formatted


class LoggerFactory:
    """Factory for creating specialized loggers."""
    
    _formatters = {
        'structured': StructuredLogFormatter(include_context=True),
        'simple': StructuredLogFormatter(include_context=False),
        'standard': logging.Formatter('%(levelname)s [%(name)s] %(message)s')
    }
    
    @classmethod
    def get_logger(cls, name: str, logger_type: str = 'structured', 
                   base_context: Optional[Dict[str, Any]] = None) -> StructuredLogger:
        """Get a structured logger instance."""
        return StructuredLogger(name, base_context)
    
    @classmethod
    def get_workflow_logger(cls, name: str, workflow_name: str, 
                           base_context: Optional[Dict[str, Any]] = None) -> WorkflowLogger:
        """Get a workflow-specific logger instance."""
        return WorkflowLogger(name, workflow_name, base_context)
    
    @classmethod
    def get_performance_logger(cls, name: str, 
                              base_context: Optional[Dict[str, Any]] = None) -> PerformanceLogger:
        """Get a performance monitoring logger instance."""
        return PerformanceLogger(name, base_context)
    
    @classmethod
    def get_ui_logger(cls, name: str, 
                     base_context: Optional[Dict[str, Any]] = None) -> UILogger:
        """Get a UI operations logger instance."""
        return UILogger(name, base_context)
    
    @classmethod
    def setup_logging(cls, level: int = logging.INFO, formatter_type: str = 'structured'):
        """Setup logging configuration with structured formatting."""
        # Configure root logger
        logging.basicConfig(
            level=level,
            format='%(levelname)s [%(name)s] %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('checker_app.log', encoding='utf-8')
            ]
        )
        
        # Set formatter for handlers
        formatter = cls._formatters.get(formatter_type, cls._formatters['structured'])
        for handler in logging.getLogger().handlers:
            handler.setFormatter(formatter)


# Convenience function for quick logger creation
def get_logger(name: str, workflow: str = None, category: str = None) -> Union[StructuredLogger, WorkflowLogger]:
    """Get an appropriate logger based on context."""
    if workflow:
        return LoggerFactory.get_workflow_logger(name, workflow)
    elif category == 'performance':
        return LoggerFactory.get_performance_logger(name)
    elif category == 'ui':
        return LoggerFactory.get_ui_logger(name)
    else:
        return LoggerFactory.get_logger(name)


# Example usage and testing
if __name__ == "__main__":
    # Setup logging
    LoggerFactory.setup_logging(level=logging.DEBUG, formatter_type='structured')
    
    # Test workflow logger
    workflow_logger = LoggerFactory.get_workflow_logger("test", "angebots_workflow")
    workflow_logger.workflow_started(customer="Test GmbH", project_id="P001")
    workflow_logger.workflow_step("file_analysis", file_count=5)
    workflow_logger.file_processed("test.pdf", file_size=1024, processing_time=2.5)
    workflow_logger.analysis_result("quality_check", {"errors": 0, "warnings": 2})
    workflow_logger.workflow_completed(duration=45.2)
    
    # Test performance logger
    perf_logger = LoggerFactory.get_performance_logger("test_perf")
    perf_logger.memory_usage(125.5, "icon_cache")
    perf_logger.execution_time("file_scan", 1250.3)
    perf_logger.cache_stats("icon_cache", 45, 5, 50)
    
    # Test UI logger
    ui_logger = LoggerFactory.get_ui_logger("test_ui")
    ui_logger.component_initialized("WorkflowRouter")
    ui_logger.layout_updated("grid", "main_container")
    ui_logger.user_interaction("button_click", "start_workflow_btn")
    ui_logger.theme_changed("dark_mode")
    
    # Test context manager
    logger = LoggerFactory.get_logger("test_context")
    with logger.context(session_id="sess_123", user="admin"):
        logger.info("User logged in")
        with logger.context(action="file_upload"):
            logger.info("Starting file upload")
            logger.error("Upload failed", {'error_code': 'NETWORK_ERROR'})
    
    print("Structured logging test completed. Check checker_app.log for output.")
