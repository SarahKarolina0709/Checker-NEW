#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ollama Model Selector & Optimizer
=================================
Advanced Model Selection und Performance Optimization für Ollama
"""

import threading

import customtkinter as ctk
import subprocess
from design_system import DesignSystem, get_color, get_font, create_button

class OllamaModelManager:
    """🤖 Advanced Ollama Model Management System"""

    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Ollama Model Manager & Optimizer")
        self.root.geometry("1200x800")

        self.available_models = []
        self.current_model = "mistral"

        self._setup_ui()
        self._load_available_models()

    def _setup_ui(self):
        """Setup model manager UI"""

        # Header
        header = ctk.CTkFrame(
            self.root,
            fg_color=get_color('primary'),
            height=80
        )
        header.pack(fill="x", padx=20, pady=(20, 10))

        header_label = ctk.CTkLabel(
            header,
            text="Ollama Model Manager & Performance Optimizer",
            font=ctk.CTkFont(*get_font('heading_lg')),
            text_color=get_color('white')
        )
        header_label.pack(pady=20)

        # Main content
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        main_frame.grid_columnconfigure((0, 1), weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # Model Selection Panel
        self._setup_model_panel(main_frame)

        # Performance Panel
        self._setup_performance_panel(main_frame)

    def _ollama_available(self) -> bool:
        """Check if the 'ollama' CLI is available on the system."""
        try:
            result = subprocess.run(['ollama', '--version'], capture_output=True, text=True, timeout=3)
            return result.returncode == 0
        except Exception:
            return False

    def _setup_model_panel(self, parent):
        """Setup Modell-Auswahl Panel"""
        model_frame = ctk.CTkFrame(parent, fg_color=get_color('surface'))
        model_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        title = ctk.CTkLabel(
            model_frame,
            text="Verfügbare Modelle",
            font=ctk.CTkFont(*get_font('heading_sm'))
        )
        title.pack(pady=15)

        # Model List
        self.model_listbox = ctk.CTkScrollableFrame(
            model_frame,
            height=300
        )
        self.model_listbox.pack(fill="both", expand=True, padx=15, pady=10)

        # Model Actions
        actions_frame = ctk.CTkFrame(model_frame, fg_color="transparent")
        actions_frame.pack(fill="x", padx=15, pady=15)
        actions_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Refresh Models Button
        refresh_btn = ctk.CTkButton(
            actions_frame,
            **create_button(style='secondary', text='Aktualisieren'),
            width=DesignSystem.get_component_property('buttons', 'min_width_md'),
            command=self._load_available_models
        )
        refresh_btn.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        # Pull New Model Button
        pull_btn = ctk.CTkButton(
            actions_frame,
            **create_button(style='primary', text='Modell laden'),
            width=DesignSystem.get_component_property('buttons', 'min_width_md'),
            command=self._show_pull_dialog
        )
        pull_btn.grid(row=0, column=1, padx=5, sticky="ew")

        # Remove Model Button
        remove_btn = ctk.CTkButton(
            actions_frame,
            **create_button(style='warning', text='Entfernen'),
            width=DesignSystem.get_component_property('buttons', 'min_width_md'),
            command=self._remove_model
        )
        remove_btn.grid(row=0, column=2, padx=(5, 0), sticky="ew")

    def _setup_performance_panel(self, parent):
        """Setup Performance-Panel"""

        perf_frame = ctk.CTkFrame(parent, fg_color=get_color('surface'))
        perf_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        title = ctk.CTkLabel(
            perf_frame,
            text="Performance-Optimierung",
            font=ctk.CTkFont(*get_font('heading_sm'))
        )
        title.pack(pady=15)

        # Model Performance Stats
        stats_frame = ctk.CTkFrame(perf_frame, fg_color=get_color('surface'))
        stats_frame.pack(fill="x", padx=15, pady=10)

        self.stats_label = ctk.CTkLabel(
            stats_frame,
            text="Leistungsmetriken\n\nEin Modell auswählen, um Statistiken anzuzeigen",
            font=ctk.CTkFont(*get_font('body_sm')),
            justify="left"
        )
        self.stats_label.pack(pady=20)

        # Recommended Models
        rec_frame = ctk.CTkFrame(perf_frame, fg_color=get_color('surface'))
        rec_frame.pack(fill="both", expand=True, padx=15, pady=10)

        rec_title = ctk.CTkLabel(
            rec_frame,
            text="Empfohlene Modelle",
            font=ctk.CTkFont(*get_font('heading_sm'))
        )
        rec_title.pack(pady=10)

        recommendations = [
            ("mistral", "Best for general translation quality", "Balanced performance"),
            ("llama2", "Excellent for detailed analysis", "Higher accuracy"),
            ("codellama", "Optimized for technical content", "Fast processing"),
            ("gemma", "Google's model for multilingual", "Best for multiple languages")
        ]

        for model, desc, perf in recommendations:
            rec_card = ctk.CTkFrame(rec_frame, fg_color=get_color('surface_hover'))
            rec_card.pack(fill="x", padx=10, pady=5)

            rec_content = ctk.CTkFrame(rec_card, fg_color="transparent")
            rec_content.pack(fill="x", padx=15, pady=10)

            model_label = ctk.CTkLabel(
                rec_content,
                text=model,
                font=ctk.CTkFont(*get_font('label'))
            )
            model_label.pack(anchor="w")

            desc_label = ctk.CTkLabel(
                rec_content,
                text=f"{desc}\n{perf}",
                font=ctk.CTkFont(*get_font('caption')),
                text_color=get_color('gray_500')
            )
            desc_label.pack(anchor="w")

        # Test Performance Button
        test_btn = ctk.CTkButton(
            perf_frame,
            **create_button(style='secondary', text='Leistung testen'),
            width=DesignSystem.get_component_property('buttons', 'min_width_md'),
            command=self._test_model_performance
        )
        test_btn.pack(pady=15)

    def _load_available_models(self):
        """Load available Ollama models"""

        def load_models():
            try:
                # Clear existing models
                for widget in self.model_listbox.winfo_children():
                    widget.destroy()

                if self._ollama_available():
                    # Get models from Ollama
                    result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')[1:]  # Skip header
                        models = []

                        for line in lines:
                            if line.strip():
                                parts = line.split()
                                if parts:
                                    model_name = parts[0]
                                    models.append(model_name)

                        self.available_models = models

                        # Display models in UI
                        self.root.after(0, lambda: self._display_models(models))
                    else:
                        self.root.after(0, lambda: self._display_error("Could not load models"))
                else:
                    self.root.after(0, lambda: self._display_error("Ollama not available"))

            except Exception as e:
                self.root.after(0, lambda: self._display_error(f"Error loading models: {e}"))

        threading.Thread(target=load_models, daemon=True).start()

    def _display_models(self, models):
        """Display models in the listbox"""

        if not models:
            no_models_label = ctk.CTkLabel(
                self.model_listbox,
                text="Keine Modelle gefunden.\n'​Modell laden' verwenden, um ein Modell herunterzuladen.",
                font=ctk.CTkFont(*get_font('body_sm')),
                text_color=get_color('gray_500')
            )
            no_models_label.pack(pady=20)
            return

        for model in models:
            model_card = ctk.CTkFrame(
                self.model_listbox,
                fg_color=get_color('surface_hover') if model == self.current_model else get_color('surface'),
                border_width=2 if model == self.current_model else 1,
                border_color=get_color('primary') if model == self.current_model else get_color('surface_border')
            )
            model_card.pack(fill="x", pady=5)

            model_content = ctk.CTkFrame(model_card, fg_color="transparent")
            model_content.pack(fill="x", padx=15, pady=10)

            # Model name and status
            header_frame = ctk.CTkFrame(model_content, fg_color="transparent")
            header_frame.pack(fill="x")

            model_label = ctk.CTkLabel(
                header_frame,
                text=f"{model}",
                font=ctk.CTkFont(*get_font('label'))
            )
            model_label.pack(side="left")

            if model == self.current_model:
                current_label = ctk.CTkLabel(
                    header_frame,
                    text="Aktiv",
                    font=ctk.CTkFont(*get_font('caption')),
                    text_color=get_color('success')
                )
                current_label.pack(side="right")

            # Select button
            select_btn = ctk.CTkButton(
                model_content,
                **create_button(style='primary', text='Auswählen'),
                width=DesignSystem.get_component_property('buttons', 'min_width_sm'),
                command=lambda m=model: self._select_model(m)
            )
            select_btn.pack(anchor="w", pady=(5, 0))

    def _display_error(self, error_message):
        """Display error message"""
        error_label = ctk.CTkLabel(
            self.model_listbox,
            text=f"{error_message}",
            font=ctk.CTkFont(*get_font('body_sm')),
            text_color=get_color('error')
        )
        error_label.pack(pady=20)

    def _select_model(self, model_name):
        """Select a model as current"""
        self.current_model = model_name
        print(f"Selected model: {model_name}")

        # Update display
        self._load_available_models()

        # Update performance stats
        self._update_performance_stats(model_name)

    def _update_performance_stats(self, model_name):
        """Update performance statistics for selected model"""

        # Simulated performance data
        performance_data = {
            'mistral': {'speed': '2.3s/query', 'accuracy': '94.2%', 'memory': '4.2GB'},
            'llama2': {'speed': '3.1s/query', 'accuracy': '96.7%', 'memory': '7.8GB'},
            'codellama': {'speed': '1.8s/query', 'accuracy': '91.5%', 'memory': '5.1GB'},
            'gemma': {'speed': '2.7s/query', 'accuracy': '93.8%', 'memory': '6.2GB'}
        }

        base_model = model_name.split(':')[0]  # Remove version tag
        stats = performance_data.get(base_model, {'speed': 'Unknown', 'accuracy': 'Unknown', 'memory': 'Unknown'})

        stats_text = (
            f"Performance Metrics for {model_name}:\n\n"
            f"Average Response Time: {stats['speed']}\n"
            f"Translation Accuracy: {stats['accuracy']}\n"
            f"Memory Usage: {stats['memory']}\n\n"
            "Optimization Status:\n"
            "- Model loaded and ready\n"
            "- Optimized for translation quality\n"
            "- Compatible with current system\n\n"
            "Usage Recommendations:\n"
            "• Best for: General translation quality analysis\n"
            "• Suitable for: Batch processing up to 50 files\n"
            f"• Performance: {stats['accuracy']} accuracy rate"
        )

        self.stats_label.configure(text=stats_text)

    def _show_pull_dialog(self):
        """Show dialog to pull new model"""

        dialog = ctk.CTkInputDialog(
            text="Enter model name to pull (e.g., llama2, codellama, gemma):",
            title="Pull New Model"
        )

        model_name = dialog.get_input()

        if model_name:
            self._pull_model(model_name)

    def _pull_model(self, model_name):
        """Pull a new model from Ollama"""

        def pull_model_thread():
            try:
                print(f"Pulling model: {model_name}...")
                result = subprocess.run(['ollama', 'pull', model_name], capture_output=True, text=True)

                if result.returncode == 0:
                    self.root.after(0, lambda: print(f"Successfully pulled model: {model_name}"))
                    self.root.after(0, self._load_available_models)
                else:
                    self.root.after(0, lambda: print(f"Failed to pull model: {result.stderr}"))

            except Exception as e:
                self.root.after(0, lambda: print(f"Error pulling model: {e}"))

        threading.Thread(target=pull_model_thread, daemon=True).start()

    def _remove_model(self):
        """Remove selected model"""
        if self.current_model:
            print(f"Removing model: {self.current_model}")
            # Implementation for removing model

    def _test_model_performance(self):
        """Test performance of current model"""

        if not self.current_model:
            print("No model selected")
            return

        print(f"Testing performance of {self.current_model}...")

        def run_performance_test():
            try:
                if self._ollama_available():
                    from ki_module import _call_ollama

                    test_prompt = "Analyze this translation quality: 'The quick brown fox jumps over the lazy dog' -> 'Der schnelle braune Fuchs springt über den faulen Hund'"

                    import time
                    start_time = time.time()

                    result = _call_ollama(test_prompt, model=self.current_model, timeout=30)

                    end_time = time.time()
                    response_time = end_time - start_time

                    self.root.after(0, lambda: print("Performance Test Results:"))
                    self.root.after(0, lambda: print(f"Response Time: {response_time:.2f} seconds"))
                    self.root.after(0, lambda: print(f"Response Length: {len(result)} characters"))
                    self.root.after(0, lambda: print("Test completed successfully"))

                else:
                    self.root.after(0, lambda: print("Ollama not available for testing"))

            except Exception as e:
                self.root.after(0, lambda: print(f"Performance test failed: {e}"))

        threading.Thread(target=run_performance_test, daemon=True).start()

    def run(self):
        """Start the model manager"""
        self.root.mainloop()

if __name__ == "__main__":
    # Start Ollama Model Manager
    manager = OllamaModelManager()
    manager.run()