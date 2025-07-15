"""
PDF Export System
================

Comprehensive PDF export functionality for the Checker application.
Handles report generation, quality assessments, and batch processing.
"""

import logging
import os
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime


class PDFExportSystem:
    """Main PDF export system for reports and quality assessments."""
    
    def __init__(self, app_instance=None):
        """
        Initialize the PDF Export System.
        
        Args:
            app_instance: Reference to the main application instance
        """
        self.app = app_instance
        self.logger = logging.getLogger(__name__)
        self.templates = {}
        self.export_settings = {
            'default_format': 'PDF',
            'quality_level': 'high',
            'include_metadata': True,
            'auto_numbering': True,
            'watermark': False
        }
        
        # Initialize PDF capabilities
        self._init_pdf_capabilities()
    
    def _init_pdf_capabilities(self):
        """Initialize PDF generation capabilities."""
        try:
            # Try to import reportlab for PDF generation
            import reportlab
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4, letter
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
            
            self.pdf_available = True
            self.canvas = canvas
            self.pagesizes = {'A4': A4, 'letter': letter}
            self.styles = getSampleStyleSheet()
            self.SimpleDocTemplate = SimpleDocTemplate
            self.Paragraph = Paragraph
            self.Spacer = Spacer
            self.Table = Table
            
            self.logger.info("[PDF] ReportLab available - PDF export enabled")
            
        except ImportError:
            self.pdf_available = False
            self.logger.warning("[PDF] ReportLab not available - PDF export disabled")
    
    def is_pdf_available(self) -> bool:
        """Check if PDF export functionality is available."""
        return self.pdf_available
    
    def export_quality_report(self, data: Dict[str, Any], output_path: str = None) -> Tuple[bool, str]:
        """
        Export a quality assessment report to PDF.
        
        Args:
            data: Report data dictionary
            output_path: Optional output path, auto-generated if None
            
        Returns:
            Tuple of (success: bool, file_path: str)
        """
        try:
            if not self.pdf_available:
                return False, "PDF export not available - install reportlab"
            
            # Generate output path if not provided
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"quality_report_{timestamp}.pdf"
                output_path = self._get_default_export_path(filename)
            
            # Create PDF document
            doc = self.SimpleDocTemplate(output_path, pagesize=self.pagesizes['A4'])
            story = []
            
            # Title
            title_style = self.styles['Title']
            title = self.Paragraph("Translation Quality Report", title_style)
            story.append(title)
            story.append(self.Spacer(1, 20))
            
            # Report metadata
            normal_style = self.styles['Normal']
            
            if 'customer' in data:
                customer = self.Paragraph(f"<b>Customer:</b> {data['customer']}", normal_style)
                story.append(customer)
            
            if 'project' in data:
                project = self.Paragraph(f"<b>Project:</b> {data['project']}", normal_style)
                story.append(project)
            
            if 'date' in data:
                date = self.Paragraph(f"<b>Date:</b> {data['date']}", normal_style)
                story.append(date)
            
            story.append(self.Spacer(1, 20))
            
            # Quality metrics
            if 'metrics' in data:
                metrics_title = self.Paragraph("<b>Quality Metrics</b>", self.styles['Heading2'])
                story.append(metrics_title)
                
                for metric, value in data['metrics'].items():
                    metric_para = self.Paragraph(f"• {metric}: {value}", normal_style)
                    story.append(metric_para)
                
                story.append(self.Spacer(1, 20))
            
            # Issues found
            if 'issues' in data and data['issues']:
                issues_title = self.Paragraph("<b>Issues Found</b>", self.styles['Heading2'])
                story.append(issues_title)
                
                for i, issue in enumerate(data['issues'], 1):
                    issue_text = f"{i}. {issue.get('description', 'No description')}"
                    if 'severity' in issue:
                        issue_text += f" (Severity: {issue['severity']})"
                    
                    issue_para = self.Paragraph(issue_text, normal_style)
                    story.append(issue_para)
                
                story.append(self.Spacer(1, 20))
            
            # Recommendations
            if 'recommendations' in data and data['recommendations']:
                recs_title = self.Paragraph("<b>Recommendations</b>", self.styles['Heading2'])
                story.append(recs_title)
                
                for i, rec in enumerate(data['recommendations'], 1):
                    rec_para = self.Paragraph(f"{i}. {rec}", normal_style)
                    story.append(rec_para)
            
            # Build PDF
            doc.build(story)
            
            self.logger.info(f"[PDF] Quality report exported to: {output_path}")
            
            # Show notification if possible
            if (self.app and hasattr(self.app, 'notification_center') and 
                self.app.notification_center):
                self.app.notification_center.show_notification(
                    f"Report exported to {os.path.basename(output_path)}", "success"
                )
            
            return True, output_path
            
        except Exception as e:
            self.logger.error(f"[PDF] Error exporting quality report: {e}")
            return False, str(e)
    
    def export_comprehensive_assessment(self, data: Dict[str, Any], output_path: str = None) -> Tuple[bool, str]:
        """
        Export a comprehensive quality assessment to PDF.
        
        Args:
            data: Assessment data dictionary
            output_path: Optional output path, auto-generated if None
            
        Returns:
            Tuple of (success: bool, file_path: str)
        """
        try:
            if not self.pdf_available:
                return False, "PDF export not available - install reportlab"
            
            # Generate output path if not provided
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"comprehensive_assessment_{timestamp}.pdf"
                output_path = self._get_default_export_path(filename)
            
            # Create PDF document
            doc = self.SimpleDocTemplate(output_path, pagesize=self.pagesizes['A4'])
            story = []
            
            # Title
            title_style = self.styles['Title']
            title = self.Paragraph("Comprehensive Translation Assessment", title_style)
            story.append(title)
            story.append(self.Spacer(1, 20))
            
            # Executive Summary
            if 'summary' in data:
                summary_title = self.Paragraph("<b>Executive Summary</b>", self.styles['Heading2'])
                story.append(summary_title)
                summary_para = self.Paragraph(data['summary'], self.styles['Normal'])
                story.append(summary_para)
                story.append(self.Spacer(1, 20))
            
            # Detailed sections
            sections = ['methodology', 'findings', 'analysis', 'conclusions']
            for section in sections:
                if section in data:
                    section_title = self.Paragraph(f"<b>{section.title()}</b>", self.styles['Heading2'])
                    story.append(section_title)
                    section_content = self.Paragraph(data[section], self.styles['Normal'])
                    story.append(section_content)
                    story.append(self.Spacer(1, 15))
            
            # Build PDF
            doc.build(story)
            
            self.logger.info(f"[PDF] Comprehensive assessment exported to: {output_path}")
            
            # Show notification if possible
            if (self.app and hasattr(self.app, 'notification_center') and 
                self.app.notification_center):
                self.app.notification_center.show_notification(
                    f"Assessment exported to {os.path.basename(output_path)}", "success"
                )
            
            return True, output_path
            
        except Exception as e:
            self.logger.error(f"[PDF] Error exporting comprehensive assessment: {e}")
            return False, str(e)
    
    def batch_export_reports(self, reports: List[Dict[str, Any]], output_dir: str = None) -> Tuple[int, List[str]]:
        """
        Export multiple reports in batch mode.
        
        Args:
            reports: List of report data dictionaries
            output_dir: Optional output directory
            
        Returns:
            Tuple of (successful_exports: int, exported_files: List[str])
        """
        try:
            if not output_dir:
                output_dir = self._get_default_export_path()
            
            os.makedirs(output_dir, exist_ok=True)
            
            successful_exports = 0
            exported_files = []
            
            for i, report_data in enumerate(reports):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"batch_report_{i+1}_{timestamp}.pdf"
                output_path = os.path.join(output_dir, filename)
                
                success, result = self.export_quality_report(report_data, output_path)
                if success:
                    successful_exports += 1
                    exported_files.append(result)
                else:
                    self.logger.warning(f"[PDF] Failed to export report {i+1}: {result}")
            
            self.logger.info(f"[PDF] Batch export completed: {successful_exports}/{len(reports)} successful")
            
            return successful_exports, exported_files
            
        except Exception as e:
            self.logger.error(f"[PDF] Error in batch export: {e}")
            return 0, []
    
    def set_export_template(self, template_name: str, template_data: Dict[str, Any]):
        """
        Set a custom export template.
        
        Args:
            template_name: Name of the template
            template_data: Template configuration data
        """
        try:
            self.templates[template_name] = template_data
            self.logger.info(f"[PDF] Template '{template_name}' registered")
            
        except Exception as e:
            self.logger.error(f"[PDF] Error setting template: {e}")
    
    def get_export_settings(self) -> Dict[str, Any]:
        """Get current export settings."""
        return self.export_settings.copy()
    
    def update_export_settings(self, settings: Dict[str, Any]):
        """
        Update export settings.
        
        Args:
            settings: Dictionary of settings to update
        """
        try:
            self.export_settings.update(settings)
            self.logger.info("[PDF] Export settings updated")
            
        except Exception as e:
            self.logger.error(f"[PDF] Error updating settings: {e}")
    
    def _get_default_export_path(self, filename: str = None) -> str:
        """Get default export path."""
        try:
            # Try to use app's customer manager for context
            if (self.app and hasattr(self.app, 'kunden_manager') and 
                self.app.kunden_manager):
                base_path = os.path.join(self.app.kunden_manager.base_dir, "exports")
            else:
                base_path = os.path.join(os.getcwd(), "exports")
            
            os.makedirs(base_path, exist_ok=True)
            
            if filename:
                return os.path.join(base_path, filename)
            else:
                return base_path
                
        except Exception as e:
            self.logger.error(f"[PDF] Error getting default export path: {e}")
            return os.path.join(os.getcwd(), "exports")
    
    def cleanup_old_exports(self, days_old: int = 30):
        """
        Clean up old export files.
        
        Args:
            days_old: Files older than this many days will be deleted
        """
        try:
            export_path = self._get_default_export_path()
            if not os.path.exists(export_path):
                return
            
            import time
            current_time = time.time()
            cutoff_time = current_time - (days_old * 24 * 60 * 60)
            
            deleted_count = 0
            for filename in os.listdir(export_path):
                file_path = os.path.join(export_path, filename)
                if os.path.isfile(file_path):
                    file_time = os.path.getmtime(file_path)
                    if file_time < cutoff_time:
                        os.remove(file_path)
                        deleted_count += 1
            
            self.logger.info(f"[PDF] Cleaned up {deleted_count} old export files")
            
        except Exception as e:
            self.logger.error(f"[PDF] Error cleaning up old exports: {e}")


# Backward compatibility functions
def exportiere_bericht_pdf(data: Dict[str, Any], output_path: str = None, app_instance=None) -> bool:
    """Backward compatibility function for PDF report export."""
    try:
        pdf_system = PDFExportSystem(app_instance)
        success, _ = pdf_system.export_quality_report(data, output_path)
        return success
    except Exception as e:
        print(f"Error exporting PDF report: {e}")
        return False


def exportiere_umfassende_pruefung_pdf(data: Dict[str, Any], output_path: str = None, app_instance=None) -> bool:
    """Backward compatibility function for comprehensive assessment export."""
    try:
        pdf_system = PDFExportSystem(app_instance)
        success, _ = pdf_system.export_comprehensive_assessment(data, output_path)
        return success
    except Exception as e:
        print(f"Error exporting comprehensive assessment: {e}")
        return False
