import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
import os
import threading
from datetime import datetime
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import re
from docx import Document
import PyPDF2
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from ui_theme import UITheme # Import the new theme

class AngebotsAnalyzer:
    def __init__(self, root, data, back_callback):
        self.root = root
        self.data = data
        self.back_callback = back_callback
        
        # --- Styling ---
        self.font_h1 = ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=UITheme.H1_SPECS[0], weight=UITheme.H1_SPECS[1])
        self.font_h2 = ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=UITheme.H2_SPECS[0], weight=UITheme.H2_SPECS[1])
        self.font_body = ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=UITheme.BODY_SPECS[0], weight=UITheme.BODY_SPECS[1])
        self.font_button = ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=UITheme.BUTTON_SPECS[0], weight=UITheme.BUTTON_SPECS[1])
        self.font_mono = ctk.CTkFont(family=UITheme.FONT_FAMILY_MONO, size=UITheme.SMALL_SPECS[0], weight=UITheme.SMALL_SPECS[1])

        # Analysis results
        self.analysis_results = {
            "character_count": 0,
            "character_count_with_spaces": 0,
            "normzeilen_count": 0,
            "repetitions": [],
            "file_info": {},
            "ocr_used": False
        }
        
        self.create_angebot_ui()
        
    def create_angebot_ui(self):
        """Creates the Angebotsanalyse UI using the modern theme."""
        # Clear existing content
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Main container
        main_frame = ctk.CTkFrame(self.root, fg_color=UITheme.COLOR_BACKGROUND)
        main_frame.pack(fill="both", expand=True, padx=UITheme.PADDING_L, pady=UITheme.PADDING_L)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1) # Allow content to expand
        
        # Header
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, UITheme.PADDING_L))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Back button
        back_btn = ctk.CTkButton(
            header_frame,
            text="< Zurück",
            command=self.back_callback,
            font=self.font_button,
            **UITheme.BUTTON_STYLE_OUTLINE
        )
        back_btn.grid(row=0, column=0, sticky="w")
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="Angebotsanalyse",
            font=self.font_h1,
            text_color=UITheme.COLOR_TEXT_PRIMARY
        )
        title_label.grid(row=0, column=1, sticky="w", padx=UITheme.PADDING_M)

        # --- Main Content Area ---
        content_container = ctk.CTkFrame(main_frame, fg_color=UITheme.COLOR_SURFACE, corner_radius=8)
        content_container.grid(row=1, column=0, sticky="nsew")
        content_container.grid_columnconfigure(0, weight=1)
        content_container.grid_rowconfigure(1, weight=1)

        # Customer info
        info_frame = ctk.CTkFrame(content_container, fg_color="transparent")
        info_frame.grid(row=0, column=0, sticky="ew", padx=UITheme.PADDING_M, pady=UITheme.PADDING_M)
        
        info_text = f"Kunde: {self.data.get('kunde_name', 'N/A')} | Auftrag: {self.data.get('auftragsnummer', 'N/A')}"
        ctk.CTkLabel(info_frame, text=info_text, font=self.font_body, text_color=UITheme.COLOR_TEXT_SECONDARY).pack(anchor="w")
        
        # --- File list & Analysis Button ---
        files_frame = ctk.CTkFrame(content_container, fg_color="transparent")
        files_frame.grid(row=1, column=0, sticky="nsew", padx=UITheme.PADDING_M, pady=(0, UITheme.PADDING_M))
        files_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            files_frame,
            text="Zu analysierende Dateien:",
            font=self.font_h2,
            text_color=UITheme.COLOR_TEXT_PRIMARY
        ).grid(row=0, column=0, sticky="w", pady=(0, UITheme.PADDING_S))
        
        # Scrollable frame for file list
        file_list_frame = ctk.CTkScrollableFrame(files_frame, fg_color=UITheme.COLOR_BACKGROUND, border_width=1, border_color=UITheme.COLOR_BORDER, corner_radius=6)
        file_list_frame.grid(row=1, column=0, sticky="nsew", pady=(0, UITheme.PADDING_M))
        files_frame.grid_rowconfigure(1, weight=1)

        for i, file_path in enumerate(self.data.get("files", []), 1):
            file_info = f"{i}. {os.path.basename(file_path)} ({self.get_file_size(file_path)})"
            ctk.CTkLabel(
                file_list_frame,
                text=file_info,
                font=self.font_mono,
                text_color=UITheme.COLOR_TEXT_SECONDARY
            ).pack(anchor="w", padx=10, pady=2)
            
        # Analysis button
        self.analyze_btn = ctk.CTkButton(
            files_frame,
            text="Analyse starten",
            command=self.start_analysis,
            font=self.font_button,
            height=40,
            **UITheme.BUTTON_STYLE_PRIMARY
        )
        self.analyze_btn.grid(row=2, column=0, sticky="e", pady=(UITheme.PADDING_M, 0))

        # --- Results Area ---
        self.results_frame = ctk.CTkFrame(main_frame, fg_color=UITheme.COLOR_SURFACE, corner_radius=8)
        self.results_frame.grid(row=1, column=0, sticky="nsew", padx=UITheme.PADDING_M, pady=(0, UITheme.PADDING_L))
        main_frame.grid_rowconfigure(1, weight=1)

        self.results_text = ctk.CTkTextbox(
            self.results_frame,
            height=300,
            font=ctk.CTkFont(family="Courier", size=12)
        )
        self.results_text.pack(fill="both", expand=True, padx=10, pady=10)
        self.results_text.insert("1.0", "Bereit für Analyse...\n\nWählen Sie 'Analyse starten' um zu beginnen.")
        
        # Export buttons
        export_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        export_frame.grid(row=2, column=0, sticky="ew", pady=(0, UITheme.PADDING_L))
        
        self.export_pdf_btn = ctk.CTkButton(
            export_frame,
            text="📄 PDF-Bericht erstellen",
            command=self.export_pdf,
            state="disabled",
            width=150
        )
        self.export_pdf_btn.pack(side="left", padx=5)
        
        self.open_folder_btn = ctk.CTkButton(
            export_frame,
            text="📁 Ordner öffnen",
            command=self.open_project_folder,
            width=150
        )
        self.open_folder_btn.pack(side="left", padx=5)
        
        # Status
        self.status_label = ctk.CTkLabel(
            export_frame,
            text="Bereit",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.status_label.pack(side="right", padx=10)
        
    def get_file_size(self, file_path):
        """Get human-readable file size"""
        try:
            size = os.path.getsize(file_path)
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} TB"
        except:
            return "Unbekannt"
            
    def start_analysis(self):
        """Start the analysis in a separate thread"""
        self.status_label.configure(text="Analyse läuft...")
        self.results_text.delete("1.0", "end")
        self.results_text.insert("1.0", "🔍 Analyse gestartet...\n\n")
        
        # Run analysis in thread to prevent UI freezing
        threading.Thread(target=self.perform_analysis, daemon=True).start()
        
    def perform_analysis(self):
        """Perform the actual analysis"""
        try:
            total_chars = 0
            total_chars_with_spaces = 0
            all_text_content = ""
            file_results = []
            
            for i, file_path in enumerate(self.data["files"], 1):
                self.root.after(0, lambda i=i: self.update_status(f"Analysiere Datei {i}/{len(self.data['files'])}..."))
                
                # Extract text from file
                text_content, file_info = self.extract_text_from_file(file_path)
                
                if text_content:
                    chars_no_spaces = len(re.sub(r'\s', '', text_content))
                    chars_with_spaces = len(text_content)
                    
                    total_chars += chars_no_spaces
                    total_chars_with_spaces += chars_with_spaces
                    all_text_content += text_content + "\n"
                    
                    file_results.append({
                        "filename": os.path.basename(file_path),
                        "chars_no_spaces": chars_no_spaces,
                        "chars_with_spaces": chars_with_spaces,
                        "normzeilen": chars_no_spaces / 36,
                        "file_info": file_info
                    })
                    
                    self.root.after(0, lambda: self.append_result(f"✅ {os.path.basename(file_path)}: {chars_no_spaces:,} Zeichen\n"))
                else:
                    self.root.after(0, lambda: self.append_result(f"❌ {os.path.basename(file_path)}: Fehler beim Lesen\n"))
                    
            # Calculate total normzeilen (AC36)
            total_normzeilen = total_chars / 36
            
            # Detect repetitions
            self.root.after(0, lambda: self.update_status("Suche nach Wiederholungen..."))
            repetitions = self.detect_repetitions(all_text_content)
            
            # Store results
            self.analysis_results = {
                "character_count": total_chars,
                "character_count_with_spaces": total_chars_with_spaces,
                "normzeilen_count": total_normzeilen,
                "repetitions": repetitions,
                "file_results": file_results,
                "analysis_date": datetime.now().isoformat()
            }
            
            # Display final results
            self.root.after(0, self.display_final_results)
            
        except Exception as e:
            error_msg = f"Fehler bei der Analyse: {str(e)}"
            self.root.after(0, lambda: self.append_result(f"\n❌ {error_msg}\n"))
            self.root.after(0, lambda: self.update_status("Analyse fehlgeschlagen"))
            
    def extract_text_from_file(self, file_path):
        """Extract text from various file formats"""
        file_ext = os.path.splitext(file_path)[1].lower()
        file_info = {"type": file_ext, "ocr_used": False}
        
        try:
            if file_ext == ".txt":
                with open(file_path, "r", encoding="utf-8") as f:
                    return f.read(), file_info
                    
            elif file_ext == ".docx":
                doc = Document(file_path)
                text = "\n".join([para.text for para in doc.paragraphs])
                return text, file_info
                
            elif file_ext == ".pdf":
                # Try normal PDF text extraction first
                text = self.extract_pdf_text(file_path)
                if text.strip():
                    return text, file_info
                else:
                    # Try OCR if no text found
                    text = self.extract_pdf_ocr(file_path)
                    file_info["ocr_used"] = True
                    return text, file_info
                    
        except Exception as e:
            print(f"Fehler beim Lesen von {file_path}: {e}")
            
        return "", file_info
        
    def extract_pdf_text(self, file_path):
        """Extract text from PDF using PyPDF2"""
        text = ""
        try:
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() or ""
        except Exception as e:
            print(f"PDF-Text-Extraktion fehlgeschlagen: {e}")
        return text

    def extract_pdf_ocr(self, file_path):
        """Extract text from PDF using OCR (for scanned PDFs) - OPTIMIZED VERSION"""
        text = ""
        try:
            # Convert PDF to images with optimized settings
            from poppler_config import get_poppler_path_for_pdf2image
            poppler_path = get_poppler_path_for_pdf2image()
            images = convert_from_path(
                file_path, 
                poppler_path=poppler_path,
                dpi=150,  # Reduced DPI for faster processing
                thread_count=2,  # Parallel processing
                fmt='JPEG'  # Faster format
            )
            # Batch OCR processing with threading
            import concurrent.futures
            def ocr_page(image_tuple):
                i, image = image_tuple
                try:
                    # Optimize image for OCR
                    image = image.convert('L')  # Convert to grayscale
                    page_text = pytesseract.image_to_string(
                        image, 
                        lang='deu+eng',  # Support multiple languages
                        config='--oem 3 --psm 6'  # Optimized OCR settings
                    )
                    return f"\n--- Seite {i+1} ---\n{page_text}\n"
                except Exception as e:
                    return f"\n--- Seite {i+1} (Fehler) ---\n[OCR-Fehler: {str(e)}]\n"
            # Process pages in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                page_results = list(executor.map(ocr_page, enumerate(images)))
                text = "".join(page_results)
            self.analysis_results["ocr_used"] = True
        except Exception as e:
            print(f"OCR fehlgeschlagen: {e}")
            text = f"[OCR-Fehler: {str(e)}]"
        return text
        
    def detect_repetitions(self, text):
        """Detect repetitive phrases in the text"""
        repetitions = []
        
        # Simple repetition detection - look for repeated phrases
        sentences = re.split(r'[.!?]+', text)
        sentence_counts = {}
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20:  # Only consider longer sentences
                if sentence in sentence_counts:
                    sentence_counts[sentence] += 1
                else:
                    sentence_counts[sentence] = 1
                    
        # Find repetitions
        for sentence, count in sentence_counts.items():
            if count > 1:
                repetitions.append({
                    "text": sentence[:100] + "..." if len(sentence) > 100 else sentence,
                    "count": count
                })
                
        return sorted(repetitions, key=lambda x: x["count"], reverse=True)[:10]  # Top 10
        
    def display_final_results(self):
        """Display the final analysis results"""
        results = self.analysis_results
        
        result_text = "🎉 ANALYSE ABGESCHLOSSEN\n"
        result_text += "=" * 50 + "\n\n"
        
        # Summary
        result_text += f"📊 ZUSAMMENFASSUNG:\n"
        result_text += f"   Zeichen (ohne Leerzeichen): {results['character_count']:,}\n"
        result_text += f"   Zeichen (mit Leerzeichen):  {results['character_count_with_spaces']:,}\n"
        result_text += f"   Normzeilen (AC36):          {results['normzeilen_count']:.2f}\n\n"
        
        # File details
        result_text += f"📁 DATEI-DETAILS:\n"
        for file_result in results.get("file_results", []):
            result_text += f"   • {file_result['filename']}\n"
            result_text += f"     Zeichen: {file_result['chars_no_spaces']:,}\n"
            result_text += f"     Normzeilen: {file_result['normzeilen']:.2f}\n"
            if file_result['file_info'].get('ocr_used'):
                result_text += f"     (OCR verwendet)\n"
            result_text += "\n"
            
        # Repetitions
        if results["repetitions"]:
            result_text += f"🔄 WIEDERHOLUNGEN ERKANNT:\n"
            for rep in results["repetitions"]:
                result_text += f"   • {rep['count']}x: {rep['text']}\n"
        else:
            result_text += f"🔄 Keine signifikanten Wiederholungen erkannt\n"
            
        result_text += "\n" + "=" * 50 + "\n"
        result_text += f"📅 Analyse erstellt am: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
        
        self.results_text.delete("1.0", "end")
        self.results_text.insert("1.0", result_text)
        
        # Enable export button
        self.export_pdf_btn.configure(state="normal")
        self.update_status("Analyse abgeschlossen")
        
    def append_result(self, text):
        """Append text to results display"""
        self.results_text.insert("end", text)
        self.results_text.see("end")
        
    def update_status(self, message):
        """Update status message"""
        self.status_label.configure(text=message)
        
    def export_pdf(self):
        """Export analysis results as PDF"""
        try:
            # Create project folder
            kunde_name = self.data["kunde"] or "Unbekannter_Kunde"
            datum = datetime.now().strftime("%Y-%m-%d")
            
            project_folder = self.get_project_folder()
            analysis_folder = os.path.join(project_folder, "Kundenanalysen")
            os.makedirs(analysis_folder, exist_ok=True)
            
            # PDF filename
            pdf_filename = f"Angebotsanalyse_{kunde_name}_{datum}.pdf"
            pdf_path = os.path.join(analysis_folder, pdf_filename)
            
            # Create PDF
            self.create_analysis_pdf(pdf_path)
            
            # Open PDF
            os.startfile(pdf_path)
            
            self.update_status(f"PDF erstellt: {pdf_filename}")
            messagebox.showinfo("Export", f"PDF-Bericht wurde erstellt:\n{pdf_path}")
            
        except Exception as e:
            messagebox.showerror("Fehler", f"PDF-Export fehlgeschlagen:\n{str(e)}")
            
    def create_analysis_pdf(self, pdf_path):
        """Create the analysis PDF report"""
        c = canvas.Canvas(pdf_path, pagesize=A4)
        width, height = A4
        y = height - 50
        
        # Header
        c.setFont("Helvetica-Bold", 20)
        c.setFillColor(colors.HexColor("#1e90ff"))
        c.drawString(50, y, "Angebotsanalyse (AC36)")
        y -= 40
        
        # Customer info
        c.setFont("Helvetica", 12)
        c.setFillColor(colors.black)
        c.drawString(50, y, f"Kunde: {self.data['kunde']}")
        y -= 20
        c.drawString(50, y, f"Betreuer: {self.data['betreuer']}")
        y -= 20
        c.drawString(50, y, f"Auftragsnummer: {self.data['auftrag']}")
        y -= 20
        c.drawString(50, y, f"Analysedatum: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        y -= 40
        
        # Summary
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(colors.HexColor("#333333"))
        c.drawString(50, y, "Zusammenfassung:")
        y -= 25
        
        c.setFont("Helvetica", 11)
        c.setFillColor(colors.black)
        results = self.analysis_results
        
        summary_lines = [
            f"Zeichen ohne Leerzeichen: {results['character_count']:,}",
            f"Zeichen mit Leerzeichen: {results['character_count_with_spaces']:,}",
            f"Normzeilen (AC36): {results['normzeilen_count']:.2f}",
            f"Anzahl Dateien: {len(self.data['files'])}"
        ]
        
        for line in summary_lines:
            c.drawString(60, y, line)
            y -= 18
            
        y -= 20
        
        # File details
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(colors.HexColor("#333333"))
        c.drawString(50, y, "Datei-Details:")
        y -= 25
        
        c.setFont("Helvetica", 10)
        for file_result in results.get("file_results", []):
            if y < 100:  # New page if needed
                c.showPage()
                y = height - 50
                
            c.setFillColor(colors.HexColor("#1e90ff"))
            c.drawString(60, y, f"• {file_result['filename']}")
            y -= 15
            
            c.setFillColor(colors.black)
            c.drawString(70, y, f"Zeichen: {file_result['chars_no_spaces']:,}")
            y -= 12
            c.drawString(70, y, f"Normzeilen: {file_result['normzeilen']:.2f}")
            y -= 12
            
            if file_result['file_info'].get('ocr_used'):
                c.setFillColor(colors.red)
                c.drawString(70, y, "(OCR verwendet)")
                y -= 12
                c.setFillColor(colors.black)
                
            y -= 10
            
        # Repetitions
        if results["repetitions"]:
            y -= 10
            c.setFont("Helvetica-Bold", 14)
            c.setFillColor(colors.HexColor("#333333"))
            c.drawString(50, y, "Erkannte Wiederholungen:")
            y -= 25
            
            c.setFont("Helvetica", 10)
            for rep in results["repetitions"]:
                if y < 80:
                    c.showPage()
                    y = height - 50
                    
                c.setFillColor(colors.darkred)
                c.drawString(60, y, f"{rep['count']}x:")
                c.setFillColor(colors.black)
                c.drawString(90, y, rep['text'][:80] + "..." if len(rep['text']) > 80 else rep['text'])
                y -= 15
                
        c.save()
        
    def get_project_folder(self):
        """Get or create project folder"""
        kunde_name = self.data["kunde"] or "Unbekannter_Kunde"
        auftrag = self.data["auftrag"] or "Ohne_Auftragsnummer"
        
        # Sanitize folder names
        kunde_clean = re.sub(r'[<>:"/\\|?*]', '_', kunde_name)
        auftrag_clean = re.sub(r'[<>:"/\\|?*]', '_', auftrag)
        
        base_dir = os.path.join(os.path.dirname(__file__), "Checker_Projekte")
        project_folder = os.path.join(base_dir, kunde_clean, auftrag_clean)
        
        os.makedirs(project_folder, exist_ok=True)
        return project_folder
        
    def open_project_folder(self):
        """Open the project folder in file explorer"""
        try:
            project_folder = self.get_project_folder()
            os.startfile(project_folder)
        except Exception as e:
            messagebox.showerror("Fehler", f"Ordner konnte nicht geöffnet werden:\n{str(e)}")
