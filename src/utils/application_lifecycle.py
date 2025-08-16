"""
Application Lifecycle Utilities
===============================

Contains utility functions for application startup, shutdown, cleanup,
and lifecycle management used throughout the Checker application.
"""

from typing import Optional, Any, Dict
import logging

class ApplicationLifecycle:
    """Utility class for application lifecycle management."""

    def __init__(self, app_instance=None):
        """
        Initialize ApplicationLifecycle.

        Args:
            app_instance: Reference to the main application instance
        """
        self.app = app_instance
        self.logger = logging.getLogger(__name__)
        self._cleanup_callbacks = []

    def handle_application_closing(self) -> bool:
        """
        Handle application closing event with comprehensive cleanup.

        Returns:
            True if cleanup was successful, False otherwise
        """
        try:
            self.logger.info("[LIFECYCLE] Application closing...")

            # Stop memory monitoring
            self._stop_memory_monitoring()

            # Clean up memory optimization resources
            self._cleanup_memory()

            # Clean up UI resources
            self._cleanup_ui_resources()

            # Clean up icon manager
            self._cleanup_icon_manager()

            # Clean up enhanced UI components
            self._cleanup_enhanced_ui()

            # Clean up error monitor
            self._cleanup_error_monitor()

            # Run custom cleanup callbacks
            self._run_cleanup_callbacks()

            # Final cleanup
            self._final_cleanup()

            self.logger.info("[LIFECYCLE] Application cleanup completed successfully")
            return True

        except Exception as e:
            self.logger.error(f"[LIFECYCLE] Error during application closing: {e}")
            return False

    def register_cleanup_callback(self, callback: callable, name: str = None):
        """
        Register a cleanup callback to be called during application shutdown.

        Args:
            callback: Function to call during cleanup
            name: Optional name for the callback (for logging)
        """
        try:
            self._cleanup_callbacks.append({
                'callback': callback,
                'name': name or callback.__name__
            })
            self.logger.debug(f"[LIFECYCLE] Registered cleanup callback: {name or callback.__name__}")
        except Exception as e:
            self.logger.error(f"[LIFECYCLE] Error registering cleanup callback: {e}")

    def setup_application_logging(self, log_level: str = "INFO") -> bool:
        """
        Setup enhanced logging for the application.

        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert string to logging level
            level = getattr(logging, log_level.upper(), logging.INFO)

            # Configure logging
            logging.basicConfig(
                level=level,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler('checker_app.log', encoding='utf-8'),
                    logging.StreamHandler()
                ]
            )

            self.logger.info(f"[LIFECYCLE] Logging setup completed with level: {log_level}")
            return True

        except Exception as e:
            print(f"[LIFECYCLE] Error setting up logging: {e}")
            return False

    def initialize_application_components(self) -> bool:
        """
        Initialize core application components in proper order.

        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info("[LIFECYCLE] Initializing application components...")

            # Initialize error handling first
            self._initialize_error_handling()

            # Initialize managers
            self._initialize_managers()

            # Initialize UI components
            self._initialize_ui_components()

            # Initialize monitoring
            self._initialize_monitoring()

            self.logger.info("[LIFECYCLE] Application components initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"[LIFECYCLE] Error initializing application components: {e}")
            return False

    def get_application_state(self) -> Dict[str, Any]:
        """
        Get current application state for debugging or state persistence.

        Returns:
            Dictionary with application state information
        """
        try:
            state = {
                'initialized': True,
                'components': {},
                'memory_usage': None,
                'error_count': 0
            }

            if not self.app:
                state['initialized'] = False
                return state

            # Check component states
            components = ['kunden_manager', 'upload_manager', 'icon_manager',
                         'error_monitor', 'memory_monitor', 'enhanced_ui']

            for component in components:
                state['components'][component] = hasattr(self.app, component) and getattr(self.app, component) is not None

            # Get memory usage if possible
            try:
                import psutil
                process = psutil.Process()
                state['memory_usage'] = round(process.memory_info().rss / (1024 * 1024), 2)
            except ImportError:
                pass

            # Get error count if available
            if hasattr(self.app, 'error_monitor') and self.app.error_monitor:
                try:
                    state['error_count'] = len(getattr(self.app.error_monitor, 'error_history', []))
                except:
                    pass

            return state

        except Exception as e:
            self.logger.error(f"[LIFECYCLE] Error getting application state: {e}")
            return {'initialized': False, 'error': str(e)}

    def _stop_memory_monitoring(self):
        """Stop memory monitoring if active."""
        try:
            if (hasattr(self.app, 'memory_monitor') and
                self.app.memory_monitor and
                hasattr(self.app.memory_monitor, 'stop_monitoring')):
                self.app.memory_monitor.stop_monitoring()
                self.logger.debug("[LIFECYCLE] Memory monitoring stopped")
        except Exception as e:
            self.logger.error(f"[LIFECYCLE] Error stopping memory monitoring: {e}")

    def _cleanup_memory(self):
        """Clean up memory optimization resources."""
        try:
            if hasattr(self.app, '_cleanup_memory'):
                self.app._cleanup_memory()
                self.logger.debug("[LIFECYCLE] Memory cleanup completed")
        except Exception as e:
            self.logger.error(f"[LIFECYCLE] Error during memory cleanup: {e}")

    def _cleanup_ui_resources(self):
        """Clean up UI resources."""
        try:
            if (hasattr(self.app, 'ui_initializer') and
                self.app.ui_initializer and
                hasattr(self.app.ui_initializer, 'cleanup_ui_resources')):
                self.app.ui_initializer.cleanup_ui_resources()
                self.logger.debug("[LIFECYCLE] UI resources cleaned up")
        except Exception as e:
            self.logger.error(f"[LIFECYCLE] Error cleaning up UI resources: {e}")

    def _cleanup_icon_manager(self):
        """Clean up icon manager resources."""
        try:
            if (hasattr(self.app, 'icon_manager') and
                self.app.icon_manager and
                hasattr(self.app.icon_manager, 'cleanup_resources')):
                self.app.icon_manager.cleanup_resources()
                self.logger.debug("[LIFECYCLE] Icon manager cleaned up")
        except Exception as e:
            self.logger.error(f"[LIFECYCLE] Error cleaning up icon manager: {e}")

    def _cleanup_enhanced_ui(self):
        """Clean up enhanced UI components."""
        try:
            if (hasattr(self.app, 'enhanced_ui') and
                self.app.enhanced_ui and
                hasattr(self.app.enhanced_ui, 'cleanup')):
                self.app.enhanced_ui.cleanup()
                self.logger.debug("[LIFECYCLE] Enhanced UI cleaned up")
        except Exception as e:
            self.logger.error(f"[LIFECYCLE] Error cleaning up enhanced UI: {e}")

    def _cleanup_error_monitor(self):
        """Clean up error monitor."""
        try:
            if (hasattr(self.app, 'error_monitor') and
                self.app.error_monitor and
                hasattr(self.app.error_monitor, 'cleanup')):
                self.app.error_monitor.cleanup()
                self.logger.debug("[LIFECYCLE] Error monitor cleaned up")
        except Exception as e:
            self.logger.error(f"[LIFECYCLE] Error cleaning up error monitor: {e}")

    def _run_cleanup_callbacks(self):
        """Run registered cleanup callbacks."""
        for callback_info in self._cleanup_callbacks:
            try:
                callback_info['callback']()
                self.logger.debug(f"[LIFECYCLE] Executed cleanup callback: {callback_info['name']}")
            except Exception as e:
                self.logger.error(f"[LIFECYCLE] Error in cleanup callback {callback_info['name']}: {e}")

    def _final_cleanup(self):
        """Perform final cleanup operations."""
        try:
            # Force garbage collection
            import gc
            collected = gc.collect()
            self.logger.debug(f"[LIFECYCLE] Final garbage collection: {collected} objects")

            # Log final state
            self.logger.info("[LIFECYCLE] Application shutdown completed")

        except Exception as e:
            self.logger.error(f"[LIFECYCLE] Error during final cleanup: {e}")

    def _initialize_error_handling(self):
        """Initialize error handling components."""
        try:
            if hasattr(self.app, '_init_error_handling'):
                self.app._init_error_handling()
                self.logger.debug("[LIFECYCLE] Error handling initialized")
        except Exception as e:
            self.logger.error(f"[LIFECYCLE] Error initializing error handling: {e}")

    def _initialize_managers(self):
        """Initialize manager components."""
        try:
            if hasattr(self.app, '_init_managers'):
                self.app._init_managers()
                self.logger.debug("[LIFECYCLE] Managers initialized")
        except Exception as e:
            self.logger.error(f"[LIFECYCLE] Error initializing managers: {e}")

    def _initialize_ui_components(self):
        """Initialize UI components."""
        try:
            if hasattr(self.app, '_init_ui_components'):
                self.app._init_ui_components()
                self.logger.debug("[LIFECYCLE] UI components initialized")
        except Exception as e:
            self.logger.error(f"[LIFECYCLE] Error initializing UI components: {e}")

    def _initialize_monitoring(self):
        """Initialize monitoring components."""
        try:
            if hasattr(self.app, '_init_monitoring'):
                self.app._init_monitoring()
                self.logger.debug("[LIFECYCLE] Monitoring initialized")
        except Exception as e:
            self.logger.error(f"[LIFECYCLE] Error initializing monitoring: {e}")