import sys
import os
import platform
import subprocess
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.lib.units import cm

# A more robust way to handle resource paths
try:
    # Assuming file_operations is in the parent directory or PYTHONPATH
    from file_operations import resource_path
    print("INFO: Using resource_path from file_operations.")
except ImportError:
    print("WARNING: Could not import resource_path from file_operations. Using fallback.")
    def resource_path(relative_path):
        """Fallback resource_path function."""
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)

class PDFExporter:
    """Handles PDF export functionality for the Checker application."""

    def __init__(self):
        """Initializes the PDF exporter with centralized styles."""
        self.styles = {
            'default_font': "Helvetica",
            'bold_font': "Helvetica-Bold",
            'font_size_normal': 10,
            'font_size_title': 18,
            'font_size_header': 14,
            'font_size_small': 8,
            'color_title': colors.darkblue,
            'color_header': colors.darkblue,
            'color_text': colors.black,
            'color_muted': colors.grey,
            'color_error': colors.darkred,
            'color_warning': colors.orange,
            'color_info': colors.blue,
            'color_background': colors.lightblue,
            'color_background_error': colors.mistyrose,
        }
        self.margin = 2 * cm
        self.line_height = 14
        self.logo_path = self._find_logo()

    def _find_logo(self):
        """Finds the path to the company logo."""
        possible_paths = [
            "Profi-Logo.png",
            resource_path("Profi-Logo.png")
        ]
        for path in possible_paths:
            if os.path.exists(path):
                print(f"INFO: Logo found at {path}")
                return path
        print("WARNING: Logo 'Profi-Logo.png' not found.")
        return None

    def _create_canvas(self, output_path):
        """Creates and returns a new PDF canvas."""
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        return canvas.Canvas(output_path, pagesize=A4)

    def _draw_header(self, c, width, height):
        """Draws the header on each page."""
        if not self.logo_path:
            return
        try:
            logo = ImageReader(self.logo_path)
            logo_width = 100
            logo_height = 35
            c.drawImage(logo, width - self.margin - logo_width, height - self.margin,
                        width=logo_width, height=logo_height, mask='auto')
        except Exception as e:
            print(f"ERROR: Could not draw logo: {e}")

    def _draw_footer(self, c, width):
        """Draws the footer on each page."""
        c.saveState()
        c.setFont(self.styles['default_font'], self.styles['font_size_small'])
        c.setFillColor(self.styles['color_muted'])
        
        footer_text = f"Generiert von Checker-App • {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        c.drawString(self.margin, self.margin / 2, footer_text)
        
        page_num_text = f"Seite {c.getPageNumber()}"
        c.drawRightString(width - self.margin, self.margin / 2, page_num_text)
        c.restoreState()

    def _draw_wrapped_text(self, c, text, x, y, max_width, **kwargs):
        """Draws text that wraps to fit within a specified width, respecting newlines."""
        if not text:
            return y
        
        font_name = kwargs.get('font_name', self.styles['default_font'])
        font_size = kwargs.get('font_size', self.styles['font_size_normal'])
        color = kwargs.get('color', self.styles['color_text'])
        line_height = kwargs.get('line_height', self.line_height)

        c.setFont(font_name, font_size)
        c.setFillColor(color)

        for line in str(text).split('\n'):
            words = line.split()
            if not words:
                y -= line_height # Treat empty line as a paragraph break
                continue

            current_line_segment = ""
            for word in words:
                if c.stringWidth(current_line_segment + word + " ", font_name, font_size) < max_width:
                    current_line_segment += word + " "
                else:
                    if y < self.margin + line_height:
                        self._draw_footer(c, A4[0])
                        c.showPage()
                        self._draw_header(c, A4[0], A4[1])
                        y = A4[1] - self.margin
                        c.setFont(font_name, font_size)
                        c.setFillColor(color)
                    
                    c.drawString(x, y, current_line_segment)
                    y -= line_height
                    current_line_segment = word + " "
            
            if y < self.margin + line_height:
                self._draw_footer(c, A4[0])
                c.showPage()
                self._draw_header(c, A4[0], A4[1])
                y = A4[1] - self.margin
                c.setFont(font_name, font_size)
                c.setFillColor(color)
                
            c.drawString(x, y, current_line_segment)
            y -= line_height
        
        return y

    def export_to_pdf(self, export_data, output_path):
        """
        Main export function. Dispatches to the correct workflow-specific method.
        """
        workflow_type = export_data.get('type', 'generic')
        
        c = self._create_canvas(output_path)
        width, height = A4

        self._draw_header(c, width, height)
        
        y = height - self.margin - 40 # Start content below header

        if workflow_type == 'pruefung':
            self._export_pruefung_content(c, y, width, export_data)
        else:
            self._export_generic_content(c, y, width, export_data, workflow_type.capitalize())

        self._draw_footer(c, width)
        c.save()
        
        print(f"INFO: PDF report generated at {output_path}")
        self._open_file(output_path)

    def _export_pruefung_content(self, c, y, width, export_data):
        """Creates the content for the 'Prüfung' PDF report."""
        # Title
        c.setFont(self.styles['bold_font'], self.styles['font_size_title'])
        c.setFillColor(self.styles['color_title'])
        c.drawString(self.margin, y, "Prüfbericht")
        y -= self.line_height * 2

        # Project Info
        y = self._draw_project_info(c, y, width, export_data.get('project_data', {}), export_data)
        y -= self.line_height

        # Results Table
        y = self._draw_results_table(c, y, width, export_data.get('results', {}))
        y -= self.line_height

        # Recommendations
        recommendations = export_data.get('recommendations')
        if recommendations:
            self._draw_recommendations(c, y, width, recommendations)

    def _draw_project_info(self, c, y, width, project_data, export_data):
        """Draws the project information section."""
        c.setFont(self.styles['bold_font'], self.styles['font_size_header'])
        c.setFillColor(self.styles['color_header'])
        c.drawString(self.margin, y, "Projektinformationen")
        y -= self.line_height * 1.5

        timestamp = export_data.get('timestamp', datetime.now().isoformat())
        try:
            formatted_date = datetime.fromisoformat(timestamp).strftime("%d.%m.%Y %H:%M:%S")
        except:
            formatted_date = timestamp

        details = {
            "Betreuer": project_data.get('supervisor_name', project_data.get('betreuer', 'N/A')),
            "Auftragsnummer": project_data.get('order_number', project_data.get('auftrag', 'N/A')),
            "Geprüfte Datei": export_data.get('file_name', 'N/A'),
            "Datum der Prüfung": formatted_date
        }

        for label, value in details.items():
            y = self._draw_wrapped_text(c, f"{label}: {value}", self.margin, y, width - 2 * self.margin)
        return y

    def _draw_results_table(self, c, y, width, results):
        """Draws the table of check results."""
        c.setFont(self.styles['bold_font'], self.styles['font_size_header'])
        c.setFillColor(self.styles['color_header'])
        c.drawString(self.margin, y, "Fehlerübersicht")
        y -= self.line_height * 1.5

        # Table Header
        headers = {"Schweregrad": 80, "Kategorie": 120, "Beschreibung": 200, "Vorschlag": 150, "Zeile": 40}
        x = self.margin
        c.setFont(self.styles['bold_font'], self.styles['font_size_normal'])
        c.setFillColor(self.styles['color_text'])
        for header, col_width in headers.items():
            c.drawString(x, y, header)
            x += col_width
        y -= self.line_height

        # Table Rows
        all_items = []
        for check_type, result_list in results.items():
            if isinstance(result_list, list):
                for item in result_list:
                    if isinstance(item, dict):
                        item['check_type'] = self._get_display_name(check_type)
                        all_items.append(item)
        
        # Sort by severity
        all_items.sort(key=lambda i: {'critical': 0, 'medium': 1, 'info': 2}.get(i.get('severity', 'info').lower(), 3))

        for item in all_items:
            severity = item.get('severity', 'info').lower()
            color_map = {'critical': self.styles['color_error'], 'medium': self.styles['color_warning'], 'info': self.styles['color_info']}
            icon_map = {'critical': '🔴', 'medium': '🟡', 'info': '🔵'}
            
            col_values = [
                f"{icon_map.get(severity, '⚪️')} {severity.capitalize()}",
                item.get('check_type', 'N/A'),
                item.get('message', ''),
                item.get('suggestion', ''),
                str(item.get('line', ''))
            ]
            
            x = self.margin
            max_row_height = 0
            
            # Use a temporary text object to calculate wrapped line heights without drawing
            temp_y = y
            for i, (header, col_width) in enumerate(headers.items()):
                text = col_values[i]
                # This is a simplification. For perfect alignment, one would need to calculate the number of lines for each cell and use the max.
                # For now, we just wrap and draw.
                pass

            # Draw the row
            current_y = y
            next_y = y
            for i, (header, col_width) in enumerate(headers.items()):
                text = col_values[i]
                color = color_map.get(severity) if i == 0 else self.styles['color_text']
                wrapped_y = self._draw_wrapped_text(c, text, x, current_y, col_width - 10, color=color)
                next_y = min(next_y, wrapped_y)
                x += col_width
            
            y = next_y - self.line_height * 0.5 # Add some padding

            if y < self.margin + self.line_height * 2:
                self._draw_footer(c, width)
                c.showPage()
                self._draw_header(c, width, A4[1])
                y = A4[1] - self.margin
                # Redraw table header on new page
                x = self.margin
                c.setFont(self.styles['bold_font'], self.styles['font_size_normal'])
                c.setFillColor(self.styles['color_text'])
                for header, col_width in headers.items():
                    c.drawString(x, y, header)
                    x += col_width
                y -= self.line_height

        return y

    def _draw_recommendations(self, c, y, width, recommendations):
        """Draws the recommendations section."""
        c.setFont(self.styles['bold_font'], self.styles['font_size_header'])
        c.setFillColor(self.styles['color_header'])
        c.drawString(self.margin, y, "Empfehlungen / Aktionsplan")
        y -= self.line_height * 1.5
        
        y = self._draw_wrapped_text(c, recommendations, self.margin, y, width - 2 * self.margin)
        return y

    def _export_generic_content(self, c, y, width, export_data, title):
        """Creates a generic PDF report for other workflows."""
        c.setFont(self.styles['bold_font'], self.styles['font_size_title'])
        c.setFillColor(self.styles['color_title'])
        c.drawString(self.margin, y, f"{title} Bericht")
        y -= self.line_height * 2

        c.setFont(self.styles['default_font'], self.styles['font_size_normal'])
        c.setFillColor(self.styles['color_text'])
        
        y = self._draw_wrapped_text(c, "Dieser Bericht wurde automatisch von der Checker-Anwendung generiert.",
                                    self.margin, y, width - 2 * self.margin)
        y -= self.line_height

        for key, value in export_data.items():
            if key in ['type', 'project_data', 'results']: continue # Already handled or not for generic display
            
            value_str = str(value)
            if len(value_str) > 200:
                value_str = value_str[:200] + "..."
            
            y = self._draw_wrapped_text(c, f"{key.replace('_', ' ').title()}: {value_str}",
                                        self.margin, y, width - 2 * self.margin)
            y -= self.line_height * 0.2

    def export_text_report(self, text_content, output_path, title="Detaillierter Bericht"):
        """Exports a large block of pre-formatted text to a styled PDF."""
        c = self._create_canvas(output_path)
        width, height = A4
        
        self._draw_header(c, width, height)
        y = height - self.margin - 40

        c.setFont(self.styles['bold_font'], self.styles['font_size_title'])
        c.setFillColor(self.styles['color_title'])
        c.drawString(self.margin, y, title)
        y -= self.line_height * 2

        # The _draw_wrapped_text method handles its own pagination.
        self._draw_wrapped_text(
            c, 
            text_content, 
            self.margin, 
            y, 
            width - 2 * self.margin, 
            font_size=9,
            line_height=12
        )

        # The footer is drawn on each page by _draw_wrapped_text, but we need one on the last page too.
        self._draw_footer(c, width)
        c.save()
        print(f"INFO: Text report generated at {output_path}")
        self._open_file(output_path)

    def _get_display_name(self, check_type):
        """Converts a check_type key to a human-readable name."""
        return {
            'grammar': 'Grammatik',
            'spelling': 'Rechtschreibung',
            'style': 'Stil',
            'quality': 'Qualität',
            'terminology': 'Terminologie',
            'ki_general': 'KI Allgemein',
        }.get(check_type, check_type.replace('_', ' ').title())

    def _open_file(self, file_path):
        """Opens a file with the default application."""
        try:
            if not os.path.exists(file_path):
                print(f"ERROR: Cannot open file, path does not exist: {file_path}")
                return
            
            print(f"INFO: Attempting to open {file_path}")
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', file_path], check=True)
            else:  # Linux
                subprocess.run(['xdg-open', file_path], check=True)
            print(f"INFO: File opened successfully.")
        except Exception as e:
            print(f"ERROR: Failed to open file '{file_path}': {e}")

# Keep legacy functions for now to ensure backward compatibility if they are called from elsewhere
def exportiere_ki_pdf(bericht, dateiname="ki_bericht.pdf"):
    print("WARNING: 'exportiere_ki_pdf' is a legacy function. Use PDFExporter class instead.")
    exporter = PDFExporter()
    c = exporter._create_canvas(dateiname)
    width, height = A4
    y = height - exporter.margin
    y = exporter._draw_wrapped_text(c, bericht, exporter.margin, y, width - 2 * exporter.margin)
    c.save()
    exporter._open_file(dateiname)

def erstelle_angebots_pdf(analysis_results, output_path):
    print("WARNING: 'erstelle_angebots_pdf' is a legacy function. Use PDFExporter class instead.")
    exporter = PDFExporter()
    export_data = {
        'type': 'angebot',
        **analysis_results
    }
    exporter.export_to_pdf(export_data, output_path)
