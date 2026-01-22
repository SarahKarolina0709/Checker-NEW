"""Einfacher i18n Smoke-Test.
Stellt sicher, dass alle über _i18n_map definierten Keys bei aktiver Sprache 'de' eine (nicht-leere) Übersetzung liefern.
Test ist robust: Falls UI-Konstruktion Fenster benötigt, wird sie übersprungen (reiner Logiktest).
"""
import inspect
import sys

from quality_gui_main_app import QualityGuiMainApp


def test_all_i18n_keys_have_german_translation():
    app = QualityGuiMainApp()
    # Force German (sollte bereits default sein)
    app.current_language = 'de'
    app._initialize_localization()
    missing = []
    for key, val in sorted(app._i18n_map.items()):  # type: ignore
        translated = app._t(key)
        # Erwartung: Unterschied oder identisch nur falls bewusst gleich (z.B. Eigennamen).
        if not isinstance(translated, str) or not translated.strip():
            missing.append(key)
    assert not missing, f"Fehlende oder leere Übersetzungen: {missing}"  # pragma: no cover

if __name__ == '__main__':  # manueller Run
    try:
        test_all_i18n_keys_have_german_translation()
        print('i18n Smoke OK')
    except AssertionError as e:
        print(str(e))
        sys.exit(1)
