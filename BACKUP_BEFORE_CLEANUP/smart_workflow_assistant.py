# -*- coding: utf-8 -*-
"""
Smart Workflow Assistant - KI-basierter Workflow-Assistent
Lernt aus Benutzerverhalten und schlägt Optimierungen vor
"""
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
from ui_theme import UITheme
from collections import defaultdict
from tkinter import messagebox
# import lite_nuclear_ctk_patch as ctk_patch # Apply nuclear anti-dark-mode patch

class SmartWorkflowAssistant(ctk.CTkToplevel):
    def __init__(self, master, checker_app, workflow_type='angebot'):
        super().__init__(master)

        self.checker_app = checker_app
        self.workflow_type = workflow_type

        # UI-Elemente
        self.title_label = None
        self.description_label = None
        self.icon_label = None

        # Workflow-Daten
        self.workflow_data = None

        # Kontext
        self.context = {
            'user_id': None,
            'session_id': None,
            'file_path': None,
            'file_type': None,
            'file_size': 0,
            'ocr_language': 'deu',
            'workflow_steps': [],
            'current_step': 0,
            'start_time': None,
            'end_time': None,
            'duration': 0,
            'success': False,
            'error': None
        }

        # ML-Modelle
        self.pattern_detector = None
        self.efficiency_predictor = None

        # UI initialisieren
        self._init_ui()

        # Kontext-Tracking starten
        self.after(1000, self._track_context)

    def _init_ui(self):
        """Initialisiert die Benutzeroberfläche"""
        self.title("Smart Workflow Assistant")
        self.geometry("800x600")
        self.configure(fg_color=UITheme.APP_BG_COLOR)

        # Titel
        self.title_label = ctk.CTkLabel(self, text="Smart Workflow Assistant",
                                        font=UITheme.get_font("large_bold"), text_color=UITheme.TEXT_COLOR)
        self.title_label.pack(pady=(20, 10))

        # Beschreibung
        self.description_label = ctk.CTkLabel(self, text="Lernt aus Ihrem Verhalten und schlägt proaktiv Optimierungen vor.",
                                            font=UITheme.get_font("default"), text_color=UITheme.TEXT_COLOR_SECONDARY)
        self.description_label.pack(pady=10)

        # Icon
        self.icon_label = ctk.CTkLabel(self, text="", image=self._load_icon(),
                                       font=UITheme.get_font("large"), text_color=UITheme.TEXT_COLOR)
        self.icon_label.pack(pady=(10, 20))

        # Workflow-Daten anzeigen
        self._display_workflow_data()

        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=20)

        ctk.CTkButton(button_frame, text="📊 Dashboard",
                     command=self._open_dashboard, **UITheme.get_button_style()).pack(side="left", padx=10)

        ctk.CTkButton(button_frame, text="💡 Empfehlungen",
                     command=self._show_recommendations, **UITheme.get_button_style("secondary")).pack(side="left", padx=10)

        ctk.CTkButton(button_frame, text="🔄 Muster lernen",
                     command=self.learn_patterns, **UITheme.get_button_style("secondary")).pack(side="left", padx=10)

        # Footer
        ctk.CTkLabel(self, text="© 2024 Checker-App",
                    font=UITheme.get_font("small"), text_color=UITheme.TEXT_COLOR_SECONDARY).pack(side="bottom", pady=10)

    def _load_icon(self):
        """Lädt das Icon-Bild"""
        try:
            image = Image.open("assets/images/assistant_icon.png")
            image = image.resize((64, 64), Image.ANTIALIAS)
            return ImageTk.PhotoImage(image)
        except Exception as e:
            print(f"Error loading icon: {e}")
            return None

    def _display_workflow_data(self):
        """Zeigt die aktuellen Workflow-Daten an"""
        if self.workflow_data is None:
            return

        # Beispielhafte Anzeige der Workflow-Daten
        data_text = f"Workflow-Daten:\n\n"
        for key, value in self.workflow_data.items():
            data_text += f"{key}: {value}\n"

        label = ctk.CTkLabel(self, text=data_text, font=UITheme.get_font("default"), text_color=UITheme.TEXT_COLOR)
        label.pack(pady=10)

    def _open_dashboard(self):
        """Öffnet das Dashboard"""
        create_workflow_dashboard(self)

    def _show_recommendations(self):
        """Zeigt Empfehlungen an"""
        recommendations = self.generate_recommendations()
        if recommendations:
            rec_text = "\n\n".join([f"{rec.title}: {rec.description}" for rec in recommendations[:3]])
        else:
            rec_text = "Keine Empfehlungen verfügbar."
        messagebox.showinfo("Workflow-Empfehlungen", rec_text)

    def _track_context(self):
        """Verfolgt den Kontext im Hintergrund"""
        # Beispiel: Kontext alle 10 Sekunden aktualisieren
        self.after(10000, self._track_context)

        # Hier könnte man komplexe Logik einfügen, um den Kontext zu analysieren und zu aktualisieren
        self.context['duration'] += 10

    def learn_patterns(self):
        """Lernt Workflow-Muster aus Historie"""
        if len(self.action_history) < 50:
            return  # Zu wenig Daten

        # Sequenzielle Muster erkennen
        self._detect_sequential_patterns()

        # Zeitbasierte Muster erkennen
        self._detect_temporal_patterns()

        # Effizienz-Muster erkennen
        self._detect_efficiency_patterns()

        # ML-Modelle trainieren
        self._train_ml_models()

    def _detect_sequential_patterns(self):
        """Erkennt sequenzielle Aktionsmuster"""
        # N-Gramm-Analyse für Aktionssequenzen
        sequences = []
        window_size = 5

        actions = list(self.action_history)
        for i in range(len(actions) - window_size):
            sequence = [a.action_type for a in actions[i:i + window_size]]
            sequences.append(sequence)

        # Häufige Sequenzen finden
        sequence_counts = defaultdict(int)
        for seq in sequences:
            seq_key = tuple(seq)
            sequence_counts[seq_key] += 1

        # Patterns erstellen
        for seq, count in sequence_counts.items():
            if count >= 3:  # Mindestens 3x aufgetreten
                pattern_id = hashlib.md5(str(seq).encode()).hexdigest()[:8]

                # Durchschnittliche Dauer berechnen
                durations = []
                success_count = 0

                for i in range(len(actions) - len(seq)):
                    action_seq = actions[i:i + len(seq)]
                    seq_types = [a.action_type for a in action_seq]

                    if tuple(seq_types) == seq:
                        total_duration = sum(a.duration for a in action_seq)
                        durations.append(total_duration)
                        if all(a.success for a in action_seq):
                            success_count += 1

                avg_duration = np.mean(durations) if durations else 0
                success_rate = success_count / count if count > 0 else 0

                pattern = WorkflowPattern(
                    pattern_id=pattern_id,
                    name=f"Sequenz: {' → '.join(seq[:3])}...",
                    actions=list(seq),
                    frequency=count,
                    avg_duration=avg_duration,
                    success_rate=success_rate,
                    optimization_potential=self._calculate_optimization_potential(seq, durations)
                )

                self.workflow_patterns[pattern_id] = pattern
                self._save_pattern_to_db(pattern)

    def _detect_temporal_patterns(self):
        """Erkennt zeitbasierte Muster"""
        # Aktivität nach Tageszeit
        hourly_activity = defaultdict(list)

        for action in self.action_history:
            hour = action.timestamp.hour
            hourly_activity[hour].append(action)

        # Peak-Zeiten identifizieren
        peak_hours = []
        for hour, actions in hourly_activity.items():
            if len(actions) > np.mean([len(acts) for acts in hourly_activity.values()]) * 1.5:
                peak_hours.append(hour)

        if peak_hours:
            pattern_id = f"temporal_peak_{'-'.join(map(str, peak_hours))}"
            pattern = WorkflowPattern(
                pattern_id=pattern_id,
                name=f"Peak-Aktivität: {peak_hours[0]}-{peak_hours[-1]} Uhr",
                actions=["temporal_pattern"],
                frequency=len(peak_hours),
                avg_duration=0,
                success_rate=1.0,
                optimization_potential=0.3
            )
            self.workflow_patterns[pattern_id] = pattern

    def _calculate_optimization_potential(self, sequence, durations):
        """Berechnet Optimierungspotential"""
        if not durations:
            return 0.0

        # Varianz der Dauern (hohe Varianz = hohes Optimierungspotential)
        variance = np.var(durations)
        normalized_variance = min(1.0, variance / np.mean(durations) if np.mean(durations) > 0 else 0)

        # Sequenzlänge (längere Sequenzen = höheres Potential)
        length_factor = min(1.0, len(sequence) / 10.0)

        # Häufigkeit (häufigere Patterns = höheres Potential)
        frequency_factor = min(1.0, len(durations) / 100.0)

        return (normalized_variance + length_factor + frequency_factor) / 3.0

    def _train_ml_models(self):
        """Trainiert ML-Modelle"""
        if len(self.action_history) < 100:
            return

        # Feature-Engineering
        features, labels = self._prepare_ml_data()

        if len(features) == 0:
            return

        # Daten normalisieren
        features_scaled = self.scaler.fit_transform(features)

        # Anomalie-Detektor trainieren
        self.anomaly_detector.fit(features_scaled)

        # Effizienz-Prädiktor trainieren
        if len(set(labels)) > 1:  # Mindestens 2 verschiedene Labels
            self.efficiency_predictor.fit(features_scaled, labels)

    def _prepare_ml_data(self):
        """Bereitet Daten für ML vor"""
        features = []
        labels = []

        for action in self.action_history:
            if action.duration > 0:
                # Features extrahieren
                feature_vector = [
                    action.timestamp.hour,  # Stunde
                    action.timestamp.weekday(),  # Wochentag
                    action.duration,  # Dauer
                    len(action.context.get('file_path', '')),  # Dateipfad-Länge
                    action.context.get('file_size', 0),  # Dateigröße
                    1 if action.success else 0,  # Erfolg
                ]

                features.append(feature_vector)

                # Label: Effizienz (schnell/langsam basierend auf Dauer)
                avg_duration = self._get_average_duration(action.action_type)
                if avg_duration > 0:
                    efficiency = 1 if action.duration <= avg_duration else 0
                    labels.append(efficiency)
                else:
                    labels.append(1)  # Default: effizient

        return features, labels

    def generate_recommendations(self):
        """Generiert Workflow-Empfehlungen"""
        recommendations = []

        # Pattern-basierte Empfehlungen
        recommendations.extend(self._generate_pattern_recommendations())

        # Effizienz-Empfehlungen
        recommendations.extend(self._generate_efficiency_recommendations())

        # Anomalie-basierte Empfehlungen
        recommendations.extend(self._generate_anomaly_recommendations())

        # Kontext-basierte Empfehlungen
        recommendations.extend(self._generate_context_recommendations())

        # Nach Impact Score sortieren
        recommendations.sort(key=lambda x: x.impact_score, reverse=True)

        self.recommendations = recommendations[:10]  # Top 10

        # In Datenbank speichern
        for rec in self.recommendations:
            self._save_recommendation_to_db(rec)

        return self.recommendations

    def _generate_pattern_recommendations(self):
        """Generiert Empfehlungen basierend auf Patterns"""
        recommendations = []

        for pattern in self.workflow_patterns.values():
            if pattern.optimization_potential > 0.5:
                rec_id = f"pattern_{pattern.pattern_id}"

                # Automatisierungs-Empfehlung
                if pattern.frequency > 10 and pattern.success_rate > 0.8:
                    recommendations.append(WorkflowRecommendation(
                        recommendation_id=rec_id + "_automation",
                        title=f"Automatisierung für '{pattern.name}'",
                        description=f"Diese Sequenz tritt {pattern.frequency}x auf und könnte automatisiert werden.",
                        category="automation",
                        impact_score=pattern.optimization_potential * pattern.frequency / 10,
                        implementation_difficulty=3,
                        estimated_time_saving=pattern.avg_duration * pattern.frequency * 0.7,
                        actions_required=["create_macro", "test_automation", "deploy"]
                    ))

                # Shortcuts-Empfehlung
                if pattern.avg_duration > 30:  # Länger als 30 Sekunden
                    recommendations.append(WorkflowRecommendation(
                        recommendation_id=rec_id + "_shortcuts",
                        title=f"Shortcuts für '{pattern.name}'",
                        description=f"Tastenkombinationen könnten diese Sequenz beschleunigen.",
                        category="shortcuts",
                        impact_score=pattern.optimization_potential * 0.6,
                        implementation_difficulty=1,
                        estimated_time_saving=pattern.avg_duration * 0.3,
                        actions_required=["define_shortcuts", "learn_shortcuts"]
                    ))

        return recommendations

    def _generate_efficiency_recommendations(self):
        """Generiert Effizienz-Empfehlungen"""
        recommendations = []

        # Langsame Aktionen identifizieren
        action_times = defaultdict(list)
        for action in self.action_history:
            if action.duration > 0:
                action_times[action.action_type].append(action.duration)

        for action_type, durations in action_times.items():
            if len(durations) >= 5:
                avg_duration = np.mean(durations)
                max_duration = np.max(durations)

                if max_duration > avg_duration * 3:  # Große Varianz
                    rec_id = f"efficiency_{action_type}"
                    recommendations.append(WorkflowRecommendation(
                        recommendation_id=rec_id,
                        title=f"Optimierung für '{action_type}'",
                        description=f"Große Zeitunterschiede erkannt. Durchschnitt: {avg_duration:.1f}s, Maximum: {max_duration:.1f}s",
                        category="efficiency",
                        impact_score=0.7,
                        implementation_difficulty=2,
                        estimated_time_saving=(max_duration - avg_duration) * len(durations),
                        actions_required=["analyze_bottlenecks", "optimize_process"]
                    ))

        return recommendations

    def create_workflow_dashboard(self, parent):
        """Erstellt Workflow-Analytics Dashboard"""
        dashboard = ctk.CTkToplevel(parent)
        dashboard.title("Smart Workflow Analytics")
        dashboard.geometry("1400x900")
        dashboard.configure(fg_color=UITheme.APP_BG_COLOR)
        dashboard.transient(parent)
        dashboard.grab_set()

        # Notebook für verschiedene Ansichten
        style = UITheme.get_notebook_style()
        notebook = ctk.CTkNotebook(dashboard, **style)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Overview Tab
        overview_tab = notebook.add("📊 Übersicht")
        self._create_overview_tab(overview_tab)

        # Patterns Tab
        patterns_tab = notebook.add("🔄 Muster")
        self._create_patterns_tab(patterns_tab)

        # Recommendations Tab
        recommendations_tab = notebook.add("💡 Empfehlungen")
        self._create_recommendations_tab(recommendations_tab)

        # Learning Tab
        learning_tab = notebook.add("🤖 KI-Lernen")
        self._create_learning_tab(learning_tab)

        # Apply theme to all child widgets
        self._apply_theme_to_dashboard(overview_tab)
        self._apply_theme_to_dashboard(patterns_tab)
        self._apply_theme_to_dashboard(recommendations_tab)
        self._apply_theme_to_dashboard(learning_tab)

        return dashboard

    def _apply_theme_to_dashboard(self, parent):
        """Setzt das Theme für alle Widgets in einem Parent-Container."""
        parent.configure(fg_color=UITheme.APP_BG_COLOR)
        for widget in parent.winfo_children():
            widget_type = widget.winfo_class()
            if "Frame" in widget_type:
                widget.configure(fg_color=UITheme.CARD_COLOR, corner_radius=UITheme.CORNER_RADIUS)
            if "Label" in widget_type:
                # This is a bit tricky as we don't know the original font intent.
                # We will apply a default, but specific labels might need overrides.
                if hasattr(widget, "cget") and "bold" in widget.cget("font").actual("weight"):
                     widget.configure(font=UITheme.get_font("headline"), text_color=UITheme.TEXT_COLOR)
                else:
                     widget.configure(font=UITheme.get_font("default"), text_color=UITheme.TEXT_COLOR_SECONDARY)
            if "Button" in widget_type:
                 widget.configure(**UITheme.get_button_style())
            if isinstance(widget, ctk.CTkScrollableFrame):
                 widget.configure(fg_color=UITheme.APP_BG_COLOR)


    def _create_overview_tab(self, parent):
        """Erstellt Übersichts-Tab"""
        parent.configure(fg_color=UITheme.APP_BG_COLOR)
        # Stats Frame
        stats_frame = ctk.CTkFrame(parent, fg_color="transparent")
        stats_frame.pack(fill="x", padx=20, pady=20)

        # Statistiken
        total_actions = len(self.action_history)
        avg_duration = np.mean([a.duration for a in self.action_history if a.duration > 0]) if self.action_history else 0
        success_rate = np.mean([a.success for a in self.action_history]) if self.action_history else 0
        patterns_found = len(self.workflow_patterns)

        stats = [
            ("Aktionen gesamt", str(total_actions)),
            ("Ø Dauer", f"{avg_duration:.1f}s"),
            ("Erfolgsrate", f"{success_rate*100:.1f}%"),
            ("Erkannte Muster", str(patterns_found))
        ]

        for i, (label, value) in enumerate(stats):
            stat_frame = ctk.CTkFrame(stats_frame, fg_color=UITheme.CARD_COLOR, corner_radius=UITheme.CORNER_RADIUS)
            stat_frame.pack(side="left", fill="x", expand=True, padx=10, pady=10)
            ctk.CTkLabel(stat_frame, text=value, font=UITheme.get_font("large_bold"), text_color=UITheme.PRIMARY_COLOR).pack(pady=(10, 0))
            ctk.CTkLabel(stat_frame, text=label, font=UITheme.get_font("default"), text_color=UITheme.TEXT_COLOR_SECONDARY).pack(pady=(0, 10))

        # Chart Frame
        chart_frame = ctk.CTkFrame(parent, fg_color=UITheme.CARD_COLOR, corner_radius=UITheme.CORNER_RADIUS)
        chart_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self._create_activity_chart(chart_frame)

    def _create_activity_chart(self, parent):
        """Erstellt Aktivitäts-Chart mit modernem Theme"""
        plt.style.use('seaborn-v0_8-whitegrid') # A good base style
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        fig.patch.set_facecolor(UITheme.CARD_COLOR)

        text_color = UITheme.TEXT_COLOR
        primary_color = UITheme.PRIMARY_COLOR
        secondary_color = UITheme.SECONDARY_COLOR
        grid_color = UITheme.BORDER_COLOR

        # Aktivität nach Aktionstyp
        if self.action_history:
            action_types = [a.action_type for a in self.action_history]
            type_counts = defaultdict(int)
            for action_type in action_types:
                type_counts[action_type] += 1

            types = list(type_counts.keys())[:10]
            counts = [type_counts[t] for t in types]

            ax1.bar(range(len(types)), counts, color=primary_color)
            ax1.set_title('Top Aktionen', color=text_color, fontsize=14, weight='bold')
            ax1.set_xticks(range(len(types)))
            ax1.set_xticklabels(types, rotation=45, ha='right', color=text_color)
            ax1.tick_params(axis='y', colors=text_color)
            ax1.set_facecolor(UITheme.CARD_COLOR)
            ax1.grid(axis='y', color=grid_color, linestyle='--', alpha=0.7)


        # Aktivität nach Stunde
        if self.action_history:
            hourly_counts = [0] * 24
            for action in self.action_history:
                hour = action.timestamp.hour
                hourly_counts[hour] += 1

            ax2.plot(range(24), hourly_counts, marker='o', color=secondary_color, linestyle='-')
            ax2.set_title('Aktivität nach Tageszeit', color=text_color, fontsize=14, weight='bold')
            ax2.set_xlabel('Stunde', color=text_color)
            ax2.set_ylabel('Anzahl Aktionen', color=text_color)
            ax2.tick_params(axis='x', colors=text_color)
            ax2.tick_params(axis='y', colors=text_color)
            ax2.set_facecolor(UITheme.CARD_COLOR)
            ax2.grid(True, color=grid_color, linestyle='--', alpha=0.7)

        for spine in ax1.spines.values():
            spine.set_edgecolor(grid_color)
        for spine in ax2.spines.values():
            spine.set_edgecolor(grid_color)

        plt.tight_layout(pad=3.0)

        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def _create_recommendations_tab(self, parent):
        """Erstellt Empfehlungs-Tab"""
        parent.configure(fg_color=UITheme.APP_BG_COLOR)
        # Empfehlungen generieren falls noch nicht vorhanden
        if not self.recommendations:
            self.generate_recommendations()

        # Scrollable Frame für Empfehlungen
        scrollable_frame = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

        if not self.recommendations:
            ctk.CTkLabel(scrollable_frame,
                        text="Keine Empfehlungen verfügbar. Sammle mehr Daten.",
                        font=UITheme.get_font("large"), text_color=UITheme.TEXT_COLOR_SECONDARY).pack(pady=50, padx=20)
            return

        for rec in self.recommendations:
            rec_frame = ctk.CTkFrame(scrollable_frame, fg_color=UITheme.CARD_COLOR, corner_radius=UITheme.CORNER_RADIUS)
            rec_frame.pack(fill="x", pady=10, padx=10)

            # Header
            header_frame = ctk.CTkFrame(rec_frame, fg_color="transparent")
            header_frame.pack(fill="x", padx=15, pady=(15, 5))

            ctk.CTkLabel(header_frame, text=rec.title,
                        font=UITheme.get_font("headline"), text_color=UITheme.TEXT_COLOR).pack(anchor="w")

            details_text = (f"Impact: {rec.impact_score:.1f} | "
                            f"Schwierigkeit: {rec.implementation_difficulty}/5 | "
                            f"Zeitersparnis: {rec.estimated_time_saving:.1f}s")
            ctk.CTkLabel(header_frame, text=details_text,
                        font=UITheme.get_font("small"), text_color=UITheme.TEXT_COLOR_SECONDARY).pack(anchor="w")

            # Beschreibung
            ctk.CTkLabel(rec_frame, text=rec.description,
                        font=UITheme.get_font("default"), wraplength=800, justify="left").pack(anchor="w", padx=15, pady=5)

            # Aktionen
            actions_text = "Erforderliche Aktionen: " + ", ".join(rec.actions_required)
            ctk.CTkLabel(rec_frame, text=actions_text,
                        font=UITheme.get_font("small"), text_color=UITheme.TEXT_COLOR_SECONDARY).pack(anchor="w", padx=15, pady=(5,10))
              # Buttons
            button_frame = ctk.CTkFrame(rec_frame, fg_color="transparent")
            button_frame.pack(fill="x", padx=15, pady=10, anchor="e")

            ctk.CTkButton(button_frame, text="Details",
                         command=lambda r=rec: self._show_recommendation_details(r),
                         **UITheme.get_button_style("secondary")).pack(side="right", padx=(10,0))
            ctk.CTkButton(button_frame, text="Ablehnen",
                         command=lambda r=rec: self._reject_recommendation(r),
                         **UITheme.get_button_style("secondary")).pack(side="right", padx=10)
            ctk.CTkButton(button_frame, text="Akzeptieren",
                         command=lambda r=rec: self._accept_recommendation(r),
                         **UITheme.get_button_style()).pack(side="right")


    def _create_patterns_tab(self, parent):
        """Erstellt Muster-Tab"""
        parent.configure(fg_color=UITheme.APP_BG_COLOR)
        scrollable_frame = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

        if not self.workflow_patterns:
            ctk.CTkLabel(scrollable_frame,
                        text="Keine Muster gefunden. Sammle mehr Daten.",
                        font=UITheme.get_font("large"), text_color=UITheme.TEXT_COLOR_SECONDARY).pack(pady=50, padx=20)
            return

        # Sort patterns by optimization potential
        sorted_patterns = sorted(self.workflow_patterns.values(), key=lambda p: p.optimization_potential, reverse=True)

        for pattern in sorted_patterns:
            pattern_frame = ctk.CTkFrame(scrollable_frame, fg_color=UITheme.CARD_COLOR, corner_radius=UITheme.CORNER_RADIUS)
            pattern_frame.pack(fill="x", pady=10, padx=10)

            ctk.CTkLabel(pattern_frame, text=pattern.name,
                        font=UITheme.get_font("headline"), text_color=UITheme.TEXT_COLOR).pack(anchor="w", padx=15, pady=(15,5))

            details = (f"Häufigkeit: {pattern.frequency} | Ø Dauer: {pattern.avg_duration:.1f}s | "
                       f"Erfolgsrate: {pattern.success_rate*100:.1f}% | "
                       f"Optimierungspotential: {pattern.optimization_potential:.2f}")
            ctk.CTkLabel(pattern_frame, text=details,
                        font=UITheme.get_font("default"), text_color=UITheme.TEXT_COLOR_SECONDARY).pack(anchor="w", padx=15, pady=(0,15))

    def _create_learning_tab(self, parent):
        """Erstellt KI-Lernen-Tab"""
        parent.configure(fg_color=UITheme.APP_BG_COLOR)
        main_frame = ctk.CTkFrame(parent, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        card = ctk.CTkFrame(main_frame, fg_color=UITheme.CARD_COLOR, corner_radius=UITheme.CORNER_RADIUS)
        card.pack(pady=20, padx=20, fill="x")

        ctk.CTkLabel(card, text="KI-Modell Status",
                    font=UITheme.get_font("headline"), text_color=UITheme.TEXT_COLOR).pack(pady=20)

        status_text = f"""Aktionen in Historie: {len(self.action_history)}
Erkannte Muster: {len(self.workflow_patterns)}
ML-Modelle trainiert: {'Ja' if len(self.action_history) >= 100 else 'Nein (benötigt 100+ Aktionen)'}"""

        ctk.CTkLabel(card, text=status_text,
                    font=UITheme.get_font("default"), text_color=UITheme.TEXT_COLOR_SECONDARY, justify="left").pack(pady=20, padx=20)

        ctk.CTkButton(card, text="Patterns neu lernen",
                     command=self.learn_patterns, **UITheme.get_button_style()).pack(pady=20, padx=20)
    
    def _load_models(self):
        """Lädt gespeicherte ML-Modelle"""
        pass
    
    def _load_user_preferences(self):
        """Lädt Benutzereinstellungen"""
        pass
    
    def _save_pattern_to_db(self, pattern):
        """Speichert Pattern in Datenbank"""
        cursor = self.db_connection.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO workflow_patterns 
            (pattern_id, name, actions, frequency, avg_duration, success_rate, optimization_potential, created_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            pattern.pattern_id,
            pattern.name,
            json.dumps(pattern.actions),
            pattern.frequency,
            pattern.avg_duration,
            pattern.success_rate,
            pattern.optimization_potential,
            datetime.now()
        ))
        self.db_connection.commit()
    
    def _save_recommendation_to_db(self, rec):
        """Speichert Empfehlung in Datenbank"""
        cursor = self.db_connection.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO recommendations 
            (recommendation_id, title, description, category, impact_score, difficulty, time_saving, actions_required, created_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            rec.recommendation_id,
            rec.title,
            rec.description,
            rec.category,
            rec.impact_score,
            rec.implementation_difficulty,
            rec.estimated_time_saving,
            json.dumps(rec.actions_required),
            datetime.now()
        ))
        self.db_connection.commit()
    
    def _update_context(self, action):
        """Aktualisiert Kontext basierend auf Aktion"""
        self.current_context['time_of_day'] = action.timestamp.hour
        self.current_context['active_feature'] = action.action_type
    
    def _suggest_efficiency_improvement(self, action):
        """Schlägt Effizienzverbesserung vor"""
        pass
    
    def _suggest_troubleshooting(self):
        """Schlägt Fehlerbehebung vor"""
        pass
    
    def _suggest_focus_improvement(self):
        """Schlägt Fokusverbesserung vor"""
        pass
    
    def _detect_efficiency_patterns(self):
        """Erkennt Effizienz-Muster"""
        pass
    
    def _generate_anomaly_recommendations(self):
        """Generiert Anomalie-basierte Empfehlungen"""
        return []
    
    def _generate_context_recommendations(self):
        """Generiert Kontext-basierte Empfehlungen"""
        return []
    
    def _accept_recommendation(self, rec):
        """Akzeptiert Empfehlung"""
        messagebox.showinfo("Empfehlung", f"Empfehlung '{rec.title}' akzeptiert!")
    
    def _reject_recommendation(self, rec):
        """Lehnt Empfehlung ab"""
        messagebox.showinfo("Empfehlung", f"Empfehlung '{rec.title}' abgelehnt!")
    
    def _show_recommendation_details(self, rec):
        """Zeigt Empfehlungsdetails"""
        details = f"Titel: {rec.title}\n\nBeschreibung: {rec.description}\n\nKategorie: {rec.category}\n\nImpact Score: {rec.impact_score}\n\nSchwierigkeit: {rec.implementation_difficulty}/5\n\nZeitersparis: {rec.estimated_time_saving:.1f}s"
        messagebox.showinfo("Empfehlungsdetails", details)

    def create_assistant_panel(self, parent):
        """Erstellt das UI-Panel für den Assistenten."""

        self.panel = ctk.CTkFrame(parent, corner_radius=UITheme.CORNER_RADIUS, fg_color=UITheme.APP_BG_COLOR)
        self.panel.pack(fill="both", expand=True, padx=10, pady=10)

        # Main container
        self.container = ctk.CTkFrame(self.panel, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=10, pady=10)

        # Title
        ctk.CTkLabel(self.container, text="Smart Workflow Assistant",
                    font=UITheme.get_font("large_bold"), text_color=UITheme.TEXT_COLOR).pack(pady=(20, 10))

        # Description
        ctk.CTkLabel(self.container, text="Lernt aus Ihrem Verhalten und schlägt proaktiv Optimierungen vor.",
                    font=UITheme.get_font("default"), text_color=UITheme.TEXT_COLOR_SECONDARY).pack(pady=10)

        # Version
        ctk.CTkLabel(self.container, text="Version 1.0",
                    font=UITheme.get_font("small"), text_color=UITheme.TEXT_COLOR_SECONDARY).pack(pady=5)

        # Separator
        ctk.CTkFrame(self.container, height=1, fg_color=UITheme.BORDER_COLOR).pack(fill="x", pady=20, padx=50)

        # Buttons
        button_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        button_frame.pack(fill="x", pady=10)
        button_frame.grid_columnconfigure((0, 1, 2), weight=1)


        ctk.CTkButton(button_frame, text="📊 Dashboard",
                     command=lambda: self.create_workflow_dashboard(self.panel),
                     **UITheme.get_button_style()).pack(side="left", expand=True, padx=10)

        ctk.CTkButton(button_frame, text="💡 Empfehlungen",
                     command=self.generate_recommendations,
                     **UITheme.get_button_style("secondary")).pack(side="left", expand=True, padx=10)

        ctk.CTkButton(button_frame, text="🔄 Muster lernen",
                     command=self.learn_patterns,
                     **UITheme.get_button_style("secondary")).pack(side="left", expand=True, padx=10)

        # Footer
        ctk.CTkLabel(self.panel, text="© 2024 Checker-App",
                    font=UITheme.get_font("small"), text_color=UITheme.TEXT_COLOR_SECONDARY).pack(side="bottom", pady=10)

        # Bindings
        self.panel.bind("<Configure>", self.on_panel_configure)
        
    def on_panel_configure(self, event):
        """Wird aufgerufen, wenn das Panel konfiguriert wird."""
        width = self.panel.winfo_width()
        height = self.panel.winfo_height()
        
        # Minimum size
        if width < 800:
            width = 800
        if height < 600:
            height = 600
        
        self.panel.config(width=width, height=height)

def create_workflow_context_decorator(action_type: str):
    """Decorator für automatisches Action-Tracking"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                raise e
            finally:
                duration = time.time() - start_time
                workflow_assistant.track_action(action_type, duration, success)
                
        return wrapper
    return decorator

# Global instance
workflow_assistant = SmartWorkflowAssistant()

def track_workflow_action(action_type: str, duration: float = None, 
                         success: bool = True, context: Dict = None):
    """Hilfsfunktion für Action-Tracking"""
    workflow_assistant.track_action(action_type, duration, success, context)

def get_workflow_recommendations():
    """Gibt aktuelle Workflow-Empfehlungen zurück"""
    return workflow_assistant.generate_recommendations()

def create_workflow_dashboard(parent):
    """Erstellt Workflow-Dashboard"""
    return workflow_assistant.create_workflow_dashboard(parent)

if __name__ == "__main__":
    # Test des Smart Workflow Assistants
    import customtkinter as ctk
    ctk.set_appearance_mode(UITheme.APPEARANCE_MODE)
    ctk.set_default_color_theme(UITheme.COLOR_THEME)

    # Simuliere einige Workflow-Aktionen für Demo
    import random

    actions = ["open_file", "analyze_text", "ocr_process", "save_results", "export_data"]

    for i in range(100):
        action = random.choice(actions)
        duration = random.uniform(1, 30)
        success = random.random() > 0.1  # 90% Erfolgsrate

        workflow_assistant.track_action(action, duration, success)

    # Patterns lernen
    workflow_assistant.learn_patterns()

    # GUI
    root = ctk.CTk()
    root.title("Smart Workflow Assistant Test")
    root.geometry("1200x800")
    root.configure(fg_color=UITheme.APP_BG_COLOR)

    main_frame = ctk.CTkFrame(root, fg_color="transparent")
    main_frame.pack(pady=50, padx=50, fill="x")


    # Dashboard Button
    dashboard_btn = ctk.CTkButton(
        main_frame,
        text="📊 Workflow Dashboard öffnen",
        command=lambda: workflow_assistant.create_workflow_dashboard(root),
        **UITheme.get_button_style(image_path="assets/images/dashboard_icon.png")
    )
    dashboard_btn.pack(pady=20, padx=20, fill="x")

    # Empfehlungen Button
    def show_recommendations():
        recommendations = workflow_assistant.generate_recommendations()
        if recommendations:
            rec_text = "\n\n".join([f"{rec.title}: {rec.description}" for rec in recommendations[:3]])
        else:
            rec_text = "Keine Empfehlungen verfügbar."
        messagebox.showinfo("Workflow-Empfehlungen", rec_text)

    recommendations_btn = ctk.CTkButton(
        main_frame,
        text="💡 Empfehlungen anzeigen",
        command=show_recommendations,
        **UITheme.get_button_style(image_path="assets/images/idea_icon.png")
    )
    recommendations_btn.pack(pady=20, padx=20, fill="x")

    root.mainloop()
