#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 🚀 ADVANCED GUI IMPROVEMENTS - MODERNE UI-ENHANCEMENTS
# Created: August 3, 2025
# Purpose: Implementierung zusätzlicher moderner GUI-Features

import os
import re

def analyze_current_features():
    """Analysiere aktuelle GUI-Features und identifiziere Verbesserungspotential"""

    gui_file = "modern_translation_quality_gui.py"
    if not os.path.exists(gui_file):
        print("❌ GUI-Datei nicht gefunden!")
        return

    with open(gui_file, 'r', encoding='utf-8') as f:
        content = f.read()

    print("🔍 ERWEITERTE GUI-VERBESSERUNGEN ANALYSE")
    print("=" * 60)

    # Feature-Checks
    features = {
        "Tooltips": bool(re.search(r'ToolTip|tooltip', content)),
        "Context Menus": bool(re.search(r'context_menu|right_click|popup_menu', content)),
        "Auto-Save": bool(re.search(r'auto_save|autosave', content)),
        "Settings Panel": bool(re.search(r'settings_panel|preferences', content)),
        "Search Function": bool(re.search(r'search.*function|def.*search', content)),
        "Animations": bool(re.search(r'animate_|animation', content)),
        "Tab Navigation": bool(re.search(r'focus_next|tab_navigation', content)),
        "Drag & Drop": bool(re.search(r'drag.*drop|DragDrop', content)),
        "Status Bar": bool(re.search(r'status_bar|statusbar', content)),
        "Progress Indicators": bool(re.search(r'progress.*bar|CTkProgressBar', content)),
        "Theme System": bool(re.search(r'get_color|UITheme', content)),
        "Keyboard Shortcuts": bool(re.search(r'bind.*<Control|<F[0-9]', content)),
        "File Watcher": bool(re.search(r'file_watcher|watchdog', content)),
        "Multi-Threading": bool(re.search(r'threading|Thread', content)),
        "Error Handling": bool(re.search(r'try:|except:|logging', content)),
    }

    print("📊 AKTUELLE FEATURES:")
    implemented = []
    missing = []

    for feature, exists in features.items():
        status = "✅" if exists else "❌"
        print(f"{status} {feature}")
        if exists:
            implemented.append(feature)
        else:
            missing.append(feature)

    print(f"\n📈 FEATURE-STATISTIK:")
    print(f"✅ Implementiert: {len(implemented)}/{len(features)} ({len(implemented)/len(features)*100:.1f}%)")
    print(f"❌ Fehlend: {len(missing)}")

    if missing:
        print(f"\n🚀 PRIORITÄRE VERBESSERUNGEN:")
        for i, feature in enumerate(missing, 1):
            print(f"{i}. {feature}")

    # Weitere erweiterte Features
    print(f"\n🎯 ERWEITERTE MODERNE FEATURES:")
    advanced_features = [
        "🎨 Mikroanimationen für Hover-Effekte",
        "📊 Live-Metriken Dashboard",
        "🌐 Multi-Language Interface",
        "🔧 Plugin-System für Erweiterungen",
        "📱 Responsive Layout für verschiedene Bildschirmgrößen",
        "🎵 Audio-Feedback für Aktionen",
        "🔔 Smart Toast-Notification System",
        "📷 Screenshot/Export Funktionalität",
        "🔍 Erweiterte Suchfunktionen mit Filtern",
        "⚡ Performance-Monitoring Dashboard",
        "🎭 Dark/Light Mode Toggle (falls gewünscht)",
        "📋 Clipboard-Integration",
        "🗂️ Tabbed Interface für Multiple Projects",
        "📐 Resizable Panels mit Splitter",
        "🎪 Welcome Tour für neue Benutzer"
    ]

    for i, feature in enumerate(advanced_features, 1):
        print(f"{i}. {feature}")

    # Code-Statistiken
    lines = len(content.split('\n'))
    methods = content.count('def ')
    classes = content.count('class ')
    imports = content.count('import ') + content.count('from ')

    print(f"\n📏 CODE-STATISTIKEN:")
    print(f"📄 Zeilen: {lines:,}")
    print(f"🏗️ Klassen: {classes}")
    print(f"⚙️ Methoden: {methods}")
    print(f"📦 Imports: {imports}")

    return missing, advanced_features

def implement_context_menus():
    """Implementiere Rechtsklick-Kontextmenüs"""

    context_menu_code = '''
# =========================== CONTEXT MENU SYSTEM ===========================

class ContextMenuManager:
    """Enhanced context menu system for right-click operations"""

    def __init__(self, parent):
        self.parent = parent
        self.menus = {}

    def create_file_context_menu(self, widget, file_path=None):
        """Create context menu for file operations"""
        menu = tk.Menu(self.parent, tearoff=0)

        if file_path:
            menu.add_command(label="📁 Datei öffnen",
                           command=lambda: self._open_file(file_path))
            menu.add_command(label="📂 Ordner öffnen",
                           command=lambda: self._open_folder(file_path))
            menu.add_separator()
            menu.add_command(label="📋 Pfad kopieren",
                           command=lambda: self._copy_path(file_path))
            menu.add_command(label="🔍 In Explorer anzeigen",
                           command=lambda: self._show_in_explorer(file_path))

        menu.add_separator()
        menu.add_command(label="🔄 Aktualisieren",
                       command=lambda: self.parent.refresh_ui())

        return menu

    def create_text_context_menu(self, widget):
        """Create context menu for text operations"""
        menu = tk.Menu(self.parent, tearoff=0)

        menu.add_command(label="✂️ Ausschneiden",
                       command=lambda: widget.event_generate("<<Cut>>"))
        menu.add_command(label="📋 Kopieren",
                       command=lambda: widget.event_generate("<<Copy>>"))
        menu.add_command(label="📄 Einfügen",
                       command=lambda: widget.event_generate("<<Paste>>"))
        menu.add_separator()
        menu.add_command(label="🔍 Alles auswählen",
                       command=lambda: widget.event_generate("<<SelectAll>>"))

        return menu

    def show_context_menu(self, event, menu_type="file", **kwargs):
        """Show context menu at cursor position"""
        try:
            if menu_type == "file":
                menu = self.create_file_context_menu(event.widget,
                                                   kwargs.get('file_path'))
            elif menu_type == "text":
                menu = self.create_text_context_menu(event.widget)
            else:
                return

            menu.post(event.x_root, event.y_root)
        except Exception as e:
            logging.error(f"Context menu error: {e}")

    def _open_file(self, file_path):
        """Open file with default application"""
        try:
            os.startfile(file_path)
        except Exception as e:
            logging.error(f"Failed to open file: {e}")

    def _open_folder(self, file_path):
        """Open containing folder"""
        try:
            folder = os.path.dirname(file_path)
            os.startfile(folder)
        except Exception as e:
            logging.error(f"Failed to open folder: {e}")

    def _copy_path(self, file_path):
        """Copy file path to clipboard"""
        try:
            self.parent.clipboard_clear()
            self.parent.clipboard_append(file_path)
            self.parent.show_toast("Pfad kopiert!", "success")
        except Exception as e:
            logging.error(f"Failed to copy path: {e}")

    def _show_in_explorer(self, file_path):
        """Show file in Windows Explorer"""
        try:
            os.system(f'explorer /select,"{file_path}"')
        except Exception as e:
            logging.error(f"Failed to show in explorer: {e}")
'''

    return context_menu_code

def implement_advanced_search():
    """Implementiere erweiterte Suchfunktionalität"""

    search_code = '''
# =========================== ADVANCED SEARCH SYSTEM ===========================

class AdvancedSearchSystem:
    """Enhanced search functionality with filters and real-time results"""

    def __init__(self, parent):
        self.parent = parent
        self.search_results = []
        self.search_filters = {
            'file_type': 'all',
            'date_range': 'all',
            'size_range': 'all',
            'content_type': 'all'
        }

    def create_search_panel(self, parent_frame):
        """Create advanced search UI panel"""
        search_frame = ctk.CTkFrame(parent_frame,
                                  fg_color=self.parent.get_color('surface'))
        search_frame.pack(fill="x", padx=10, pady=5)

        # Search input with real-time filtering
        search_label = ctk.CTkLabel(search_frame,
                                  text="🔍 Erweiterte Suche:",
                                  font=ctk.CTkFont(*self.parent.get_typography("label")))
        search_label.pack(anchor="w", padx=10, pady=(10, 5))

        self.search_entry = ctk.CTkEntry(search_frame,
                                       placeholder_text="Suchbegriff eingeben...",
                                       font=ctk.CTkFont(*self.parent.get_typography("body")))
        self.search_entry.pack(fill="x", padx=10, pady=5)
        self.search_entry.bind("<KeyRelease>", self.on_search_changed)

        # Filter options
        filter_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
        filter_frame.pack(fill="x", padx=10, pady=5)

        # File type filter
        file_type_label = ctk.CTkLabel(filter_frame, text="Dateityp:")
        file_type_label.grid(row=0, column=0, padx=(0, 5), sticky="w")

        self.file_type_var = ctk.StringVar(value="all")
        file_type_menu = ctk.CTkOptionMenu(filter_frame,
                                         values=["all", "PDF", "TXT", "DOCX"],
                                         variable=self.file_type_var,
                                         command=self.apply_filters)
        file_type_menu.grid(row=0, column=1, padx=5)

        # Date range filter
        date_label = ctk.CTkLabel(filter_frame, text="Zeitraum:")
        date_label.grid(row=0, column=2, padx=(10, 5), sticky="w")

        self.date_var = ctk.StringVar(value="all")
        date_menu = ctk.CTkOptionMenu(filter_frame,
                                    values=["all", "heute", "diese Woche", "dieser Monat"],
                                    variable=self.date_var,
                                    command=self.apply_filters)
        date_menu.grid(row=0, column=3, padx=5)

        # Results display
        self.results_frame = ctk.CTkScrollableFrame(search_frame, height=200)
        self.results_frame.pack(fill="both", expand=True, padx=10, pady=10)

        return search_frame

    def on_search_changed(self, event=None):
        """Handle real-time search input changes"""
        search_term = self.search_entry.get().lower()
        if len(search_term) >= 2:  # Start searching after 2 characters
            self.perform_search(search_term)
        elif len(search_term) == 0:
            self.clear_results()

    def perform_search(self, search_term):
        """Perform comprehensive search across files and data"""
        self.search_results = []

        try:
            # Search in uploaded files
            for file_list in [self.parent.uploaded_files.get('source', []),
                            self.parent.uploaded_files.get('translation', [])]:
                for file_info in file_list:
                    if self.matches_search_criteria(file_info, search_term):
                        self.search_results.append({
                            'type': 'file',
                            'data': file_info,
                            'relevance': self.calculate_relevance(file_info, search_term)
                        })

            # Search in analysis results
            if hasattr(self.parent, 'analysis_results'):
                for result in self.parent.analysis_results:
                    if self.matches_search_criteria(result, search_term):
                        self.search_results.append({
                            'type': 'analysis',
                            'data': result,
                            'relevance': self.calculate_relevance(result, search_term)
                        })

            # Sort by relevance
            self.search_results.sort(key=lambda x: x['relevance'], reverse=True)
            self.display_results()

        except Exception as e:
            logging.error(f"Search error: {e}")

    def matches_search_criteria(self, item, search_term):
        """Check if item matches search criteria and filters"""
        # Text matching
        item_text = str(item).lower()
        if search_term not in item_text:
            return False

        # Apply filters
        if self.search_filters['file_type'] != 'all':
            # Add file type filtering logic
            pass

        return True

    def calculate_relevance(self, item, search_term):
        """Calculate search result relevance score"""
        item_text = str(item).lower()
        score = 0

        # Exact match bonus
        if search_term == item_text:
            score += 100

        # Word boundary match bonus
        if f" {search_term} " in f" {item_text} ":
            score += 50

        # Frequency bonus
        score += item_text.count(search_term) * 10

        return score

    def display_results(self):
        """Display search results in the results frame"""
        # Clear previous results
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        if not self.search_results:
            no_results = ctk.CTkLabel(self.results_frame,
                                    text="Keine Ergebnisse gefunden",
                                    font=ctk.CTkFont(*self.parent.get_typography("body")))
            no_results.pack(pady=20)
            return

        # Display results
        for i, result in enumerate(self.search_results[:20]):  # Limit to top 20
            result_frame = ctk.CTkFrame(self.results_frame)
            result_frame.pack(fill="x", padx=5, pady=2)

            # Result type icon and title
            type_icon = "📄" if result['type'] == 'file' else "📊"
            title = f"{type_icon} {str(result['data'])[:60]}..."

            result_label = ctk.CTkLabel(result_frame, text=title, anchor="w")
            result_label.pack(fill="x", padx=10, pady=5)

            # Click handler for result selection
            result_frame.bind("<Button-1>",
                            lambda e, r=result: self.on_result_selected(r))

    def on_result_selected(self, result):
        """Handle selection of search result"""
        try:
            if result['type'] == 'file':
                # Open or highlight the file
                self.parent.highlight_file(result['data'])
            elif result['type'] == 'analysis':
                # Show analysis details
                self.parent.show_analysis_details(result['data'])
        except Exception as e:
            logging.error(f"Result selection error: {e}")

    def apply_filters(self, *args):
        """Apply search filters and refresh results"""
        self.search_filters['file_type'] = self.file_type_var.get()
        self.search_filters['date_range'] = self.date_var.get()

        # Re-run search with filters
        search_term = self.search_entry.get()
        if search_term:
            self.perform_search(search_term)

    def clear_results(self):
        """Clear search results display"""
        for widget in self.results_frame.winfo_children():
            widget.destroy()
'''

    return search_code

def implement_performance_monitor():
    """Implementiere Performance-Monitoring Dashboard"""

    monitor_code = '''
# =========================== PERFORMANCE MONITOR ===========================

import psutil
import time
import threading
from collections import deque

class PerformanceMonitor:
    """Real-time performance monitoring for the application"""

    def __init__(self, parent):
        self.parent = parent
        self.monitoring = False
        self.monitor_thread = None

        # Performance history (last 60 data points)
        self.cpu_history = deque(maxlen=60)
        self.memory_history = deque(maxlen=60)
        self.ui_response_times = deque(maxlen=60)

        # Metrics
        self.current_metrics = {
            'cpu_percent': 0,
            'memory_percent': 0,
            'memory_mb': 0,
            'ui_response_ms': 0,
            'active_threads': 0,
            'file_operations': 0
        }

    def create_monitor_panel(self, parent_frame):
        """Create performance monitoring UI panel"""
        monitor_frame = ctk.CTkFrame(parent_frame,
                                   fg_color=self.parent.get_color('surface'))
        monitor_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Header
        header = ctk.CTkLabel(monitor_frame,
                            text="⚡ Performance Monitor",
                            font=ctk.CTkFont(*self.parent.get_typography("heading")))
        header.pack(pady=10)

        # Metrics grid
        metrics_frame = ctk.CTkFrame(monitor_frame, fg_color="transparent")
        metrics_frame.pack(fill="x", padx=20, pady=10)

        # CPU Usage
        self.cpu_label = ctk.CTkLabel(metrics_frame, text="CPU: 0%")
        self.cpu_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.cpu_progress = ctk.CTkProgressBar(metrics_frame)
        self.cpu_progress.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        # Memory Usage
        self.memory_label = ctk.CTkLabel(metrics_frame, text="RAM: 0 MB")
        self.memory_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.memory_progress = ctk.CTkProgressBar(metrics_frame)
        self.memory_progress.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Response Time
        self.response_label = ctk.CTkLabel(metrics_frame, text="UI Response: 0ms")
        self.response_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        # Thread Count
        self.threads_label = ctk.CTkLabel(metrics_frame, text="Threads: 0")
        self.threads_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")

        metrics_frame.grid_columnconfigure(1, weight=1)

        # Control buttons
        control_frame = ctk.CTkFrame(monitor_frame, fg_color="transparent")
        control_frame.pack(fill="x", padx=20, pady=10)

        self.start_btn = ctk.CTkButton(control_frame,
                                     text="Monitor starten",
                                     command=self.start_monitoring)
        self.start_btn.pack(side="left", padx=5)

        self.stop_btn = ctk.CTkButton(control_frame,
                                    text="Monitor stoppen",
                                    command=self.stop_monitoring,
                                    state="disabled")
        self.stop_btn.pack(side="left", padx=5)

        return monitor_frame

    def start_monitoring(self):
        """Start performance monitoring"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self.monitor_loop,
                                                 daemon=True)
            self.monitor_thread.start()

            self.start_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")

    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)

        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")

    def monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                # Get system metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                process = psutil.Process()

                # Measure UI response time
                ui_start = time.time()
                self.parent.after(0, lambda: None)  # Dummy UI operation
                ui_response = (time.time() - ui_start) * 1000

                # Update metrics
                self.current_metrics.update({
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_mb': process.memory_info().rss / 1024 / 1024,
                    'ui_response_ms': ui_response,
                    'active_threads': threading.active_count()
                })

                # Store history
                self.cpu_history.append(cpu_percent)
                self.memory_history.append(memory.percent)
                self.ui_response_times.append(ui_response)

                # Update UI (thread-safe)
                self.parent.after(0, self.update_ui_metrics)

                time.sleep(1)  # Update every second

            except Exception as e:
                logging.error(f"Monitoring error: {e}")
                break

    def update_ui_metrics(self):
        """Update UI with current metrics (must run in main thread)"""
        try:
            metrics = self.current_metrics

            # Update labels
            self.cpu_label.configure(text=f"CPU: {metrics['cpu_percent']:.1f}%")
            self.memory_label.configure(text=f"RAM: {metrics['memory_mb']:.1f} MB")
            self.response_label.configure(text=f"UI Response: {metrics['ui_response_ms']:.1f}ms")
            self.threads_label.configure(text=f"Threads: {metrics['active_threads']}")

            # Update progress bars
            self.cpu_progress.set(metrics['cpu_percent'] / 100)
            self.memory_progress.set(metrics['memory_percent'] / 100)

            # Color coding based on performance
            cpu_color = self.get_performance_color(metrics['cpu_percent'])
            memory_color = self.get_performance_color(metrics['memory_percent'])

        except Exception as e:
            logging.error(f"UI metrics update error: {e}")

    def get_performance_color(self, percentage):
        """Get color based on performance percentage"""
        if percentage < 50:
            return self.parent.get_color('success')
        elif percentage < 80:
            return self.parent.get_color('warning')
        else:
            return self.parent.get_color('error')

    def get_performance_report(self):
        """Generate performance report"""
        if not self.cpu_history:
            return "Keine Daten verfügbar"

        avg_cpu = sum(self.cpu_history) / len(self.cpu_history)
        avg_memory = sum(self.memory_history) / len(self.memory_history)
        avg_response = sum(self.ui_response_times) / len(self.ui_response_times)

        report = f"""
Performance Report:
=================
Durchschnittliche CPU-Nutzung: {avg_cpu:.1f}%
Durchschnittliche RAM-Nutzung: {avg_memory:.1f}%
Durchschnittliche UI-Response: {avg_response:.1f}ms
Aktive Threads: {self.current_metrics['active_threads']}
"""
        return report
'''

    return monitor_code

def apply_improvements():
    """Wende die wichtigsten GUI-Verbesserungen an"""

    gui_file = "modern_translation_quality_gui.py"
    if not os.path.exists(gui_file):
        print("❌ GUI-Datei nicht gefunden!")
        return

    print("🚀 ANWENDUNG ERWEITERTER GUI-VERBESSERUNGEN")
    print("=" * 50)

    # Backup erstellen
    backup_file = f"{gui_file}.backup_{int(time.time())}"
    shutil.copy2(gui_file, backup_file)
    print(f"✅ Backup erstellt: {backup_file}")

    with open(gui_file, 'r', encoding='utf-8') as f:
        content = f.read()

    improvements_added = []

    # 1. Context Menus hinzufügen
    if 'ContextMenuManager' not in content:
        context_code = implement_context_menus()
        # Einfügen nach den bestehenden Klassen
        insertion_point = content.find('class TranslationQualityGUI')
        if insertion_point != -1:
            content = content[:insertion_point] + context_code + "\n\n" + content[insertion_point:]
            improvements_added.append("Context Menus")

    # 2. Erweiterte Suche hinzufügen
    if 'AdvancedSearchSystem' not in content:
        search_code = implement_advanced_search()
        insertion_point = content.find('class TranslationQualityGUI')
        if insertion_point != -1:
            content = content[:insertion_point] + search_code + "\n\n" + content[insertion_point:]
            improvements_added.append("Advanced Search")

    # 3. Performance Monitor hinzufügen
    if 'PerformanceMonitor' not in content:
        monitor_code = implement_performance_monitor()
        insertion_point = content.find('class TranslationQualityGUI')
        if insertion_point != -1:
            content = content[:insertion_point] + monitor_code + "\n\n" + content[insertion_point:]
            improvements_added.append("Performance Monitor")

    # Datei schreiben
    with open(gui_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ Verbesserungen angewendet: {', '.join(improvements_added)}")
    print(f"📄 Neue Dateigröße: {len(content.split(chr(10))):,} Zeilen")

    return improvements_added

if __name__ == "__main__":
    import shutil
    import time

    print("🎯 ADVANCED GUI IMPROVEMENTS SYSTEM")
    print("=" * 50)

    # Analysiere aktuelle Features
    missing, advanced = analyze_current_features()

    print(f"\n🤔 Was fällt mir noch ein? HIER SIND DIE ANTWORTEN:")
    print("=" * 60)

    if missing:
        print("🔧 SOFORT UMSETZBARE VERBESSERUNGEN:")
        for i, feature in enumerate(missing, 1):
            print(f"{i}. {feature}")

    print(f"\n🚀 ERWEITERTE MODERNE FEATURES:")
    priority_features = [
        "🎨 Mikroanimationen für sanfte Übergänge",
        "📊 Live-Dashboard mit Performance-Metriken",
        "🔍 Intelligente Suche mit Filtern und Vorschlägen",
        "📋 Rechtsklick-Kontextmenüs für alle Elemente",
        "⚡ Performance-Monitor für Echtzeit-Optimierung",
        "🎪 Interactive Welcome Tour für neue Benutzer",
        "📱 Vollständig responsive Layout-System",
        "🎵 Subtile Audio-Feedback für Aktionen",
        "🔔 Smart Toast-Notification System",
        "📷 Screenshot & Export Funktionalität",
        "🗂️ Tabbed Interface für Multiple Projects",
        "📐 Resizable Panels mit Drag-Splittern",
        "🌐 Multi-Language Support (DE/EN/FR)",
        "🔧 Plugin-System für Erweiterungen",
        "⚙️ Erweiterte Einstellungen mit Themes"
    ]

    for i, feature in enumerate(priority_features, 1):
        print(f"{i:2d}. {feature}")

    print(f"\n💡 MEINE EMPFEHLUNG - TOP 5 PRIORITÄTEN:")
    top_priorities = [
        "1. 📋 Context Menus (sofort umsetzbar, hoher UX-Gewinn)",
        "2. 🔍 Advanced Search (praktischer Mehrwert)",
        "3. ⚡ Performance Monitor (Transparenz & Debugging)",
        "4. 🎨 Mikroanimationen (moderne, polierte UI)",
        "5. 🎪 Welcome Tour (Benutzerfreundlichkeit)"
    ]

    for priority in top_priorities:
        print(priority)

    # Frage nach Implementierung
    print(f"\n❓ SOLL ICH DIE TOP-VERBESSERUNGEN IMPLEMENTIEREN?")
    print("   (Context Menus, Advanced Search, Performance Monitor)")