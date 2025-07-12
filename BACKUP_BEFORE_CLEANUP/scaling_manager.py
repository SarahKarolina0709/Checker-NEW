"""
Zentralisierte CTK-Skalierungs- und DPI-Verwaltung
"""
import customtkinter as ctk
from app_logger import get_logger

class ScalingManager:
    """Zentrale Verwaltung für CustomTkinter-Skalierung und DPI-Einstellungen"""
    
    def __init__(self):
        self.logger = get_logger('scaling')
        self._initialized = False
        self.logger.info("Scaling manager created")
    
    def apply_scaling_config(self):
        """Wendet die Skalierungskonfiguration an"""
        if self._initialized:
            return
        
        self.logger.info("Applying scaling configuration")
        
        try:
            # DPI-Awareness deaktivieren
            ctk.deactivate_automatic_dpi_awareness()
            self.logger.debug("DPI awareness deactivated")
            
            # Skalierung setzen
            ctk.set_widget_scaling(1.0)
            ctk.set_window_scaling(1.0)
            self.logger.debug("Scaling set to 1.0")
            
            # ScalingTracker blockieren
            self._disable_scaling_tracker()
            
            self._initialized = True
            self.logger.info("Scaling configuration applied successfully")
            
        except Exception as e:
            self.logger.error(f"Error applying scaling configuration: {e}")
    
    def apply_post_import_patches(self):
        """Wendet Patches nach dem Import von CustomTkinter an"""
        try:
            self._disable_scaling_tracker()
            self.logger.debug("Post-import patches applied")
        except Exception as e:
            self.logger.warning(f"Error applying post-import patches: {e}")
    
    def configure_window(self, window):
        """Konfiguriert ein Fenster mit stabilisierten Einstellungen"""
        try:
            # Ensure no automatic scaling
            self.stabilize_scaling()
            self.logger.debug("Window configured with stable scaling")
        except Exception as e:
            self.logger.warning(f"Error configuring window: {e}")
    
    def stabilize_scaling(self):
        """Stabilisiert die Skalierung erneut"""
        try:
            ctk.deactivate_automatic_dpi_awareness()
            ctk.set_widget_scaling(1.0)
            ctk.set_window_scaling(1.0)
            self._disable_scaling_tracker()
            self.logger.debug("Scaling stabilized")
        except Exception as e:
            self.logger.warning(f"Error stabilizing scaling: {e}")
    
    def _disable_scaling_tracker(self):
        """Blockiert den CustomTkinter ScalingTracker"""
        try:
            from customtkinter.windows.widgets.scaling import ScalingTracker
            
            def disabled_check_dpi_scaling(*args, **kwargs):
                return None
            
            ScalingTracker.check_dpi_scaling = disabled_check_dpi_scaling
            self.logger.debug("ScalingTracker disabled")
            
        except Exception as e:
            self.logger.warning(f"Could not disable ScalingTracker: {e}")
    
    def configure_window_layout(self, window):
        """Konfiguriert das Layout eines Fensters"""
        try:
            # Propagation deaktivieren
            window.pack_propagate(False)
            window.grid_propagate(False)
            
            # Grid-Konfiguration
            window.grid_rowconfigure(0, weight=1)
            window.grid_columnconfigure(0, weight=1)
            
            self.logger.debug("Window layout configured")
            
        except Exception as e:
            self.logger.error(f"Error configuring window layout: {e}")
