# -*- coding: utf-8 -*-
"""
Logging Configuration for CheckerApp
Configures structured logging for the entire application.
"""

import logging
import logging.handlers
import os
from datetime import datetime
from structured_logging import LoggerFactory, StructuredLogFormatter


def setup_application_logging(
    log_level=logging.INFO,
    log_file='checker_app.log',
    max_log_size=10*1024*1024,  # 10MB
    backup_count=5,
    console_logging=True,
    structured_logging=True
):
    """
    Set up comprehensive logging for the CheckerApp.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file
        max_log_size: Maximum size of log file before rotation
        backup_count: Number of backup log files to keep
        console_logging: Whether to enable console logging
        structured_logging: Whether to use structured logging format
    """
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(log_file) if os.path.dirname(log_file) else 'logs'
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatters
    if structured_logging:
        formatter = StructuredLogFormatter(include_context=True)
        simple_formatter = StructuredLogFormatter(include_context=False)
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        simple_formatter = logging.Formatter(
            '%(levelname)s [%(name)s] %(message)s'
        )
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_log_size,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Console handler
    if console_logging:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(simple_formatter)
        root_logger.addHandler(console_handler)
    
    # Set up specialized loggers
    _setup_component_loggers(log_level)
    
    # Log startup message
    startup_logger = logging.getLogger('CheckerApp.Startup')
    startup_logger.info(f"Logging system initialized", {
        'log_level': logging.getLevelName(log_level),
        'log_file': log_file,
        'structured_logging': structured_logging,
        'console_logging': console_logging,
        'timestamp': datetime.now().isoformat()
    })


def _setup_component_loggers(log_level):
    """Set up component-specific loggers with appropriate levels."""
    
    # Component log levels
    component_levels = {
        'app_managers': log_level,
        'workflow': log_level,
        'ui': log_level,
        'performance': log_level,
        'memory': log_level,
        'thread_safety': log_level,
        'angebots_workflow': log_level,
        'pruefung_workflow': log_level,
        'finalisierung_workflow': log_level,
        'projekt_workflow': log_level,
        'notifications': log_level,
        'errors': log_level
    }
    
    # Set levels for component loggers
    for component, level in component_levels.items():
        logger = logging.getLogger(component)
        logger.setLevel(level)


def setup_development_logging():
    """Set up logging for development environment."""
    setup_application_logging(
        log_level=logging.DEBUG,
        log_file='logs/checker_app_dev.log',
        console_logging=True,
        structured_logging=True
    )


def setup_production_logging():
    """Set up logging for production environment."""
    setup_application_logging(
        log_level=logging.INFO,
        log_file='logs/checker_app_prod.log',
        console_logging=False,
        structured_logging=True
    )


def setup_testing_logging():
    """Set up logging for testing environment."""
    setup_application_logging(
        log_level=logging.WARNING,
        log_file='logs/checker_app_test.log',
        console_logging=False,
        structured_logging=True
    )


def get_workflow_logger(workflow_name: str, module_name: str = None):
    """
    Get a workflow-specific logger.
    
    Args:
        workflow_name: Name of the workflow
        module_name: Name of the module (optional)
    
    Returns:
        WorkflowLogger instance
    """
    logger_name = f"{module_name}.{workflow_name}" if module_name else workflow_name
    
    if LoggerFactory:
        return LoggerFactory.get_workflow_logger(logger_name, workflow_name)
    else:
        return logging.getLogger(logger_name)


def get_ui_logger(component_name: str):
    """
    Get a UI-specific logger.
    
    Args:
        component_name: Name of the UI component
    
    Returns:
        UILogger instance
    """
    if LoggerFactory:
        return LoggerFactory.get_ui_logger(f"ui.{component_name}")
    else:
        return logging.getLogger(f"ui.{component_name}")


def get_performance_logger(component_name: str):
    """
    Get a performance-specific logger.
    
    Args:
        component_name: Name of the component
    
    Returns:
        PerformanceLogger instance
    """
    if LoggerFactory:
        return LoggerFactory.get_performance_logger(f"performance.{component_name}")
    else:
        return logging.getLogger(f"performance.{component_name}")


def create_log_context(workflow=None, component=None, operation=None, **kwargs):
    """
    Create a log context dictionary.
    
    Args:
        workflow: Workflow name
        component: Component name
        operation: Operation name
        **kwargs: Additional context
    
    Returns:
        Dictionary with log context
    """
    context = {}
    
    if workflow:
        context['workflow'] = workflow
    if component:
        context['component'] = component
    if operation:
        context['operation'] = operation
    
    # Add additional context
    context.update(kwargs)
    
    return context


# Example usage and configuration
if __name__ == "__main__":
    # Test different logging setups
    print("Testing logging configurations...")
    
    # Development logging
    setup_development_logging()
    
    # Test workflow logger
    workflow_logger = get_workflow_logger('test_workflow', 'test_module')
    workflow_logger.info("Test workflow log", create_log_context(
        workflow='test_workflow',
        operation='test_operation',
        test_param='test_value'
    ))
    
    # Test UI logger
    ui_logger = get_ui_logger('test_component')
    ui_logger.info("Test UI log", create_log_context(
        component='test_component',
        operation='ui_update',
        widget_type='button'
    ))
    
    # Test performance logger
    perf_logger = get_performance_logger('test_perf')
    perf_logger.info("Test performance log", create_log_context(
        component='test_perf',
        operation='performance_test',
        duration_ms=150.5
    ))
    
    print("Logging test completed. Check logs/checker_app_dev.log for output.")
