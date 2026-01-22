import types


class DummyBus:
    def __init__(self):
        self.handlers = {}

    def subscribe(self, name, fn):
        self.handlers.setdefault(name, []).append(fn)
        return (name, id(fn))

    def unsubscribe(self, name, sid):
        # no-op in tests
        return

    def emit(self, name, payload):
        for fn in self.handlers.get(name, []):
            fn(payload)


class DummyCard:
    def __init__(self):
        self.calls = []

    def update_metric(self, value_new=None, desc_new=None, progress_value=None):
        self.calls.append({'value_new': value_new, 'desc_new': desc_new, 'progress_value': progress_value})


class DummyApp:
    def __init__(self, with_trigger=True):
        self.root = types.SimpleNamespace(after=lambda ms, fn=None: (fn() if fn else None), after_cancel=lambda t: None)
        self.event_bus = DummyBus()
        self.output_frame = types.SimpleNamespace(winfo_children=lambda: [], destroy=lambda: None)
        self._dev_mode = True
        self.settings = {}
        self.design_system = {}
        self.uploaded_files = {'source': ['a'], 'translation': []}
        self._t = lambda s: s
        if with_trigger:
            self.trigger_analysis = lambda: None

    def get_color(self, name):
        # Provide minimal palette
        palette = {
            'primary': '#123456', 'primary_hover': '#234567', 'white': '#ffffff',
            'surface': '#ffffff', 'surface_border': '#dddddd', 'transparent': 'transparent',
            'text_muted': '#888888', 'text_secondary': '#666666', 'info': '#0050aa',
            'success': '#0a8a0a', 'warning': '#f08c00', 'error': '#cc0000'
        }
        return palette.get(name, '#000000')

    def get_spacing(self, token):
        return {'md': 16, 'lg': 24, 'xl': 32}.get(token, 16)

    def get_typography(self, token):
        return {'body': ('Segoe UI', 14, 'normal'), 'heading': ('Segoe UI', 18, 'bold'), 'title': ('Segoe UI', 22, 'bold'), 'caption': ('Segoe UI', 12, 'normal')}.get(token, ('Segoe UI', 14, 'normal'))


def test_build_dashboard_no_analysis(monkeypatch):
    import sys, types, importlib
    import customtkinter as ctk
    # Dummy CTk classes to avoid real Tk
    class F:
        def __init__(self, *a, **k): pass
        def pack(self, *a, **k): pass
        def grid(self, *a, **k): pass
        def pack_propagate(self, *a, **k): pass
        def grid_columnconfigure(self, *a, **k): pass
        def grid_rowconfigure(self, *a, **k): pass
        def bind(self, *a, **k): pass
        def winfo_children(self): return []
        def configure(self, **k): pass
        def cget(self, k): return None
        def winfo_rootx(self): return 0
        def winfo_rooty(self): return 0
        def winfo_height(self): return 0
    class L(F):
        def __init__(self, *a, **k): self._text = k.get('text')
    class T(F):
        def __init__(self, *a, **k): pass
        def overrideredirect(self, *a, **k): pass
        def geometry(self, *a, **k): pass
        def destroy(self): pass
    created = {'cta': False}
    class B(F):
        def __init__(self, *a, **k):
            if k.get('text') == 'Jetzt analysieren':
                created['cta'] = True
            self._cmd = k.get('command')
        def cget(self, key):
            return self._cmd if key == 'command' else None
    class Font:
        def __init__(self, *a, **k): pass
    monkeypatch.setattr(ctk, 'CTkFrame', F)
    monkeypatch.setattr(ctk, 'CTkLabel', L)
    monkeypatch.setattr(ctk, 'CTkButton', B)
    monkeypatch.setattr(ctk, 'CTkToplevel', T, raising=False)
    monkeypatch.setattr(ctk, 'CTkFont', Font)

    # Neutralize aggressive_anti_dark_mode side-effects for this test run
    dummy_aggressive = types.ModuleType('aggressive_anti_dark_mode')
    dummy_aggressive.apply_aggressive_light_mode_patches = lambda: True
    # Replace any existing module to avoid auto-exec side effects
    monkeypatch.setitem(sys.modules, 'aggressive_anti_dark_mode', dummy_aggressive)

    import quality_gui_components_analysis_dashboard as mod
    # Reload to ensure our CTk stubs and dummy aggressive module are used
    mod = importlib.reload(mod)
    app = DummyApp(with_trigger=True)
    mod.build_analysis_dashboard(app)
    assert created['cta'] is True


def test_progress_updates_quality(monkeypatch):
    import sys, types, importlib
    import customtkinter as ctk
    # Dummy CTk classes to avoid real Tk
    class F:
        def __init__(self, *a, **k): pass
        def pack(self, *a, **k): pass
        def grid(self, *a, **k): pass
        def pack_propagate(self, *a, **k): pass
        def grid_columnconfigure(self, *a, **k): pass
        def grid_rowconfigure(self, *a, **k): pass
        def bind(self, *a, **k): pass
        def winfo_children(self): return []
        def configure(self, **k): pass
        def cget(self, k): return None
        def winfo_rootx(self): return 0
        def winfo_rooty(self): return 0
        def winfo_height(self): return 0
    class L(F):
        def __init__(self, *a, **k): self._text = k.get('text')
    class B(F):
        def __init__(self, *a, **k): self._cmd = k.get('command')
        def cget(self, key):
            return self._cmd if key == 'command' else None
    class T(F):
        def overrideredirect(self, *a, **k): pass
        def geometry(self, *a, **k): pass
        def destroy(self): pass
    class Font:
        def __init__(self, *a, **k): pass
    monkeypatch.setattr(ctk, 'CTkFrame', F)
    monkeypatch.setattr(ctk, 'CTkLabel', L)
    monkeypatch.setattr(ctk, 'CTkButton', B)
    monkeypatch.setattr(ctk, 'CTkToplevel', T, raising=False)
    monkeypatch.setattr(ctk, 'CTkFont', Font)

    # Neutralize aggressive_anti_dark_mode side-effects and reload dashboard
    dummy_aggressive = types.ModuleType('aggressive_anti_dark_mode')
    dummy_aggressive.apply_aggressive_light_mode_patches = lambda: True
    monkeypatch.setitem(sys.modules, 'aggressive_anti_dark_mode', dummy_aggressive)

    import quality_gui_components_analysis_dashboard as mod
    mod = importlib.reload(mod)
    app = DummyApp(with_trigger=False)
    # Stub card creation to attach DummyCard for 'quality'
    cards = {}
    def fake_create_or_fallback(app_, parent, title, value, color, description, column, *, show_progress=False, value_max=100.0):
        card = DummyCard()
        idx = {0: 'quality', 1: 'issues', 2: 'files', 3: 'duration', 4: 'severity'}.get(column)
        if idx:
            cards[idx] = card
        return card
    monkeypatch.setattr(mod, 'create_or_fallback_metric_card', fake_create_or_fallback)
    mod.build_analysis_dashboard(app)
    # Emit progress with quality_score
    app.event_bus.emit('analysis.progress', {'quality_score': 0.73, 'phase': 'analyze'})
    # Expect a value ~ 73% applied via update_metric
    q = cards.get('quality')
    assert q is not None
    assert any(call.get('value_new') in ('73%', '73.0%') for call in q.calls)
