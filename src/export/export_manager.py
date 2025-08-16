"""
Export System Manager
====================

Main export system coordinator that integrates PDF export and format management.
Provides unified interface for all export operations in the Checker application.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple, Union
import logging
import os

from .format_manager import FormatExportManager
from .pdf_system import PDFExportSystem

class ExportSystemManager:
    """Main export system manager integrating all export capabilities."""

    def __init__(self, app_instance=None):
        """
        Initialize the Export System Manager.

        Args:
            app_instance: Reference to the main application instance
        """
        self.app = app_instance
        self.logger = logging.getLogger(__name__)

        # Initialize sub-systems
        self.pdf_system = PDFExportSystem(app_instance)
        self.format_manager = FormatExportManager(app_instance)

        # Export statistics
        self.export_stats = {
            'total_exports': 0,
            'successful_exports': 0,
            'failed_exports': 0,
            'formats_used': {},
            'last_export': None
        }

        self.logger.info("[EXPORT] Export System Manager initialized")

    def get_available_formats(self) -> List[str]:
        """Get all available export formats."""
        formats = ['PDF'] + self.format_manager.get_supported_formats()
        return list(set(formats))  # Remove duplicates

    def export_report(self, data: Dict[str, Any], format_type: str = 'PDF', output_path: str = None) -> Tuple[bool, str]:
        """
        Export a report in the specified format.

        Args:
            data: Report data dictionary
            format_type: Target format (PDF, JSON, HTML, etc.)
            output_path: Optional output path

        Returns:
            Tuple of (success: bool, result_path_or_error: str)
        """
        try:
            self.export_stats['total_exports'] += 1
            format_upper = format_type.upper()

            # Route to appropriate export system
            if format_upper == 'PDF':
                success, result = self.pdf_system.export_quality_report(data, output_path)
            else:
                success, result = self.format_manager.export_data(data, format_type, output_path)

            # Update statistics
            if success:
                self.export_stats['successful_exports'] += 1
                self.export_stats['formats_used'][format_upper] = self.export_stats['formats_used'].get(format_upper, 0) + 1
                self.export_stats['last_export'] = datetime.now().isoformat()

                self.logger.info(f"[EXPORT] Report exported successfully to {format_type}: {result}")
            else:
                self.export_stats['failed_exports'] += 1
                self.logger.error(f"[EXPORT] Report export failed: {result}")

            return success, result

        except Exception as e:
            self.export_stats['failed_exports'] += 1
            error_msg = f"Error exporting report: {e}"
            self.logger.error(f"[EXPORT] {error_msg}")
            return False, error_msg

    def export_comprehensive_assessment(self, data: Dict[str, Any], format_type: str = 'PDF', output_path: str = None) -> Tuple[bool, str]:
        """
        Export a comprehensive assessment.

        Args:
            data: Assessment data dictionary
            format_type: Target format
            output_path: Optional output path

        Returns:
            Tuple of (success: bool, result_path_or_error: str)
        """
        try:
            self.export_stats['total_exports'] += 1
            format_upper = format_type.upper()

            # Route to appropriate export system
            if format_upper == 'PDF':
                success, result = self.pdf_system.export_comprehensive_assessment(data, output_path)
            else:
                success, result = self.format_manager.export_data(data, format_type, output_path)

            # Update statistics
            if success:
                self.export_stats['successful_exports'] += 1
                self.export_stats['formats_used'][format_upper] = self.export_stats['formats_used'].get(format_upper, 0) + 1
                self.export_stats['last_export'] = datetime.now().isoformat()

                self.logger.info(f"[EXPORT] Assessment exported successfully to {format_type}: {result}")
            else:
                self.export_stats['failed_exports'] += 1
                self.logger.error(f"[EXPORT] Assessment export failed: {result}")

            return success, result

        except Exception as e:
            self.export_stats['failed_exports'] += 1
            error_msg = f"Error exporting assessment: {e}"
            self.logger.error(f"[EXPORT] {error_msg}")
            return False, error_msg

    def batch_export_reports(self, reports: List[Dict[str, Any]], format_type: str = 'PDF', output_dir: str = None) -> Tuple[int, List[str]]:
        """
        Export multiple reports in batch mode.

        Args:
            reports: List of report data dictionaries
            format_type: Target format
            output_dir: Optional output directory

        Returns:
            Tuple of (successful_exports: int, exported_files: List[str])
        """
        try:
            format_upper = format_type.upper()

            if format_upper == 'PDF':
                successful, files = self.pdf_system.batch_export_reports(reports, output_dir)
            else:
                successful, files = self.format_manager.batch_export(reports, format_type, output_dir)

            # Update statistics
            self.export_stats['total_exports'] += len(reports)
            self.export_stats['successful_exports'] += successful
            self.export_stats['failed_exports'] += (len(reports) - successful)
            self.export_stats['formats_used'][format_upper] = self.export_stats['formats_used'].get(format_upper, 0) + successful

            if successful > 0:
                self.export_stats['last_export'] = datetime.now().isoformat()

            self.logger.info(f"[EXPORT] Batch export completed: {successful}/{len(reports)} successful")

            return successful, files

        except Exception as e:
            self.export_stats['failed_exports'] += len(reports) if reports else 1
            error_msg = f"Error in batch export: {e}"
            self.logger.error(f"[EXPORT] {error_msg}")
            return 0, []

    def export_customer_data(self, customer_name: str, format_type: str = 'JSON', output_path: str = None) -> Tuple[bool, str]:
        """
        Export customer data and projects.

        Args:
            customer_name: Name of the customer
            format_type: Target format
            output_path: Optional output path

        Returns:
            Tuple of (success: bool, result_path_or_error: str)
        """
        try:
            if not (self.app and hasattr(self.app, 'kunden_manager') and self.app.kunden_manager):
                return False, "Customer manager not available"

            kunden_manager = self.app.kunden_manager

            # Gather customer data
            customer_data = {
                'customer_name': customer_name,
                'export_date': datetime.now().isoformat(),
                'projects': [],
                'statistics': {}
            }

            # Get customer projects
            projects = kunden_manager.liste_kundenprojekte(customer_name)
            for project_id in projects:
                project_path = kunden_manager.get_projekt_pfad(customer_name, project_id)

                project_info = {
                    'project_id': project_id,
                    'project_path': project_path,
                    'workflows': {}
                }

                # Get workflow information
                for workflow in kunden_manager.workflows:
                    workflow_path = kunden_manager.get_projekt_workflow_ordner(customer_name, project_id, workflow)

                    if os.path.exists(workflow_path):
                        files = [f for f in os.listdir(workflow_path) if os.path.isfile(os.path.join(workflow_path, f))]
                        project_info['workflows'][workflow] = {
                            'path': workflow_path,
                            'file_count': len(files),
                            'files': files
                        }

                customer_data['projects'].append(project_info)

            # Add statistics
            customer_data['statistics'] = {
                'total_projects': len(projects),
                'total_workflows': len(kunden_manager.workflows),
                'customer_path': kunden_manager.kunden_ordner(customer_name)
            }

            # Export the data
            return self.format_manager.export_data(customer_data, format_type, output_path)

        except Exception as e:
            error_msg = f"Error exporting customer data: {e}"
            self.logger.error(f"[EXPORT] {error_msg}")
            return False, error_msg

    def export_project_summary(self, customer_name: str, project_id: str, format_type: str = 'PDF', output_path: str = None) -> Tuple[bool, str]:
        """
        Export a project summary report.

        Args:
            customer_name: Name of the customer
            project_id: Project identifier
            format_type: Target format
            output_path: Optional output path

        Returns:
            Tuple of (success: bool, result_path_or_error: str)
        """
        try:
            if not (self.app and hasattr(self.app, 'kunden_manager') and self.app.kunden_manager):
                return False, "Customer manager not available"

            kunden_manager = self.app.kunden_manager

            # Gather project data
            project_data = {
                'customer': customer_name,
                'project': project_id,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'project_path': kunden_manager.get_projekt_pfad(customer_name, project_id),
                'workflows': {},
                'summary': f"Project summary for {customer_name} - {project_id}"
            }

            # Get workflow details
            total_files = 0
            for workflow in kunden_manager.workflows:
                workflow_path = kunden_manager.get_projekt_workflow_ordner(customer_name, project_id, workflow)

                if os.path.exists(workflow_path):
                    files = [f for f in os.listdir(workflow_path) if os.path.isfile(os.path.join(workflow_path, f))]
                    file_count = len(files)
                    total_files += file_count

                    project_data['workflows'][workflow] = {
                        'file_count': file_count,
                        'files': files[:10] if len(files) > 10 else files,  # Limit file list
                        'status': 'Active' if file_count > 0 else 'Empty'
                    }

            project_data['metrics'] = {
                'Total Files': total_files,
                'Active Workflows': sum(1 for w in project_data['workflows'].values() if w['status'] == 'Active'),
                'Project Status': 'Active' if total_files > 0 else 'Empty'
            }

            # Export based on format
            if format_type.upper() == 'PDF':
                return self.export_report(project_data, format_type, output_path)
            else:
                return self.format_manager.export_data(project_data, format_type, output_path)

        except Exception as e:
            error_msg = f"Error exporting project summary: {e}"
            self.logger.error(f"[EXPORT] {error_msg}")
            return False, error_msg

    def get_export_statistics(self) -> Dict[str, Any]:
        """Get export system statistics."""
        return self.export_stats.copy()

    def reset_statistics(self):
        """Reset export statistics."""
        self.export_stats = {
            'total_exports': 0,
            'successful_exports': 0,
            'failed_exports': 0,
            'formats_used': {},
            'last_export': None
        }
        self.logger.info("[EXPORT] Export statistics reset")

    def cleanup_old_exports(self, days_old: int = 30):
        """
        Clean up old export files.

        Args:
            days_old: Files older than this many days will be deleted
        """
        try:
            # Clean up PDF exports
            self.pdf_system.cleanup_old_exports(days_old)

            # Clean up other format exports
            export_path = self.format_manager._get_default_export_path()
            if os.path.exists(export_path):
                import time
                current_time = time.time()
                cutoff_time = current_time - (days_old * 24 * 60 * 60)

                deleted_count = 0
                for filename in os.listdir(export_path):
                    file_path = os.path.join(export_path, filename)
                    if os.path.isfile(file_path) and not filename.endswith('.pdf'):  # PDFs handled by pdf_system
                        file_time = os.path.getmtime(file_path)
                        if file_time < cutoff_time:
                            os.remove(file_path)
                            deleted_count += 1

                self.logger.info(f"[EXPORT] Cleaned up {deleted_count} old export files")

        except Exception as e:
            self.logger.error(f"[EXPORT] Error cleaning up old exports: {e}")

    def get_pdf_availability(self) -> bool:
        """Check if PDF export is available."""
        return self.pdf_system.is_pdf_available()

    def configure_pdf_settings(self, settings: Dict[str, Any]):
        """Configure PDF export settings."""
        try:
            self.pdf_system.update_export_settings(settings)
            self.logger.info("[EXPORT] PDF settings updated")
        except Exception as e:
            self.logger.error(f"[EXPORT] Error updating PDF settings: {e}")

    def set_pdf_template(self, template_name: str, template_data: Dict[str, Any]):
        """Set a custom PDF template."""
        try:
            self.pdf_system.set_export_template(template_name, template_data)
            self.logger.info(f"[EXPORT] PDF template '{template_name}' configured")
        except Exception as e:
            self.logger.error(f"[EXPORT] Error setting PDF template: {e}")


# Backward compatibility wrapper functions
def create_modern_export_system(app_instance=None) -> ExportSystemManager:
    """Create and return the modern export system."""
    return ExportSystemManager(app_instance)


def export_bericht_wrapper(data: Dict[str, Any], format_type: str = 'PDF', output_path: str = None, app_instance=None) -> bool:
    """Backward compatibility wrapper for report export."""
    try:
        export_manager = ExportSystemManager(app_instance)
        success, _ = export_manager.export_report(data, format_type, output_path)
        return success
    except Exception as e:
        print(f"Error in export wrapper: {e}")
        return False


def export_umfassende_pruefung_wrapper(data: Dict[str, Any], format_type: str = 'PDF', output_path: str = None, app_instance=None) -> bool:
    """Backward compatibility wrapper for comprehensive assessment export."""
    try:
        export_manager = ExportSystemManager(app_instance)
        success, _ = export_manager.export_comprehensive_assessment(data, format_type, output_path)
        return success
    except Exception as e:
        print(f"Error in assessment export wrapper: {e}")
        return False