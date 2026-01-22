#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 Design-System Self-Test
==========================

Prüft alle Tokens im Checker Design System:
- Farben validieren
- Spacings und Typografie prüfen
- CTkFont-Erstellung testen (fällt bei Headless automatisch auf Tuple zurück)
- CSS-Export ausgeben
- Kontrastverhältnisse checken

Ausführung:
    python design_system_self_test.py
"""
from __future__ import annotations

from design_system import DesignSystem


def run_self_test() -> None:
    print("🧪 DESIGN SYSTEM SELF-TEST\n" + "=" * 40)

    # 🎨 Farben prüfen
    print("\n🎨 Farben:")
    colors = DesignSystem.get_colors()
    invalid_colors = 0
    for name, hexval in colors.items():
        try:
            if hexval != "transparent" and not hexval.startswith("rgba("):
                assert hexval.startswith("#") and len(hexval) == 7, f"❌ Ungültige Farbe: {name}={hexval}"
            print(f"✅ {name:<20} {hexval}")
        except AssertionError as e:
            invalid_colors += 1
            print(str(e))
    if invalid_colors:
        print(f"⚠️  {invalid_colors} Farbtokens mit Problemen")

    # 📐 Abstände prüfen
    print("\n📐 Abstände:")
    spacings = DesignSystem.get_spacing()
    for name, px in spacings.items():
        assert isinstance(px, int), f"❌ Spacing {name} ist kein int"
        print(f"✅ {name:<5} = {px}px")

    # 📝 Typografie prüfen
    print("\n📝 Typografie:")
    fonts = DesignSystem.get_typography()
    for name, (family, size, weight) in fonts.items():
        print(f"✅ {name:<12} {family}, {size}px, {weight}")
        # CTkFont Test (kann in Headless auf Tuple-Fallback gehen)
        fobj = DesignSystem.get_font_object(name)
        print(f"   → CTkFont OK: {fobj}")

    # 🌐 CSS-Export
    print("\n🌐 CSS Export (gekürzt):")
    css = DesignSystem.to_css_variables()
    css_lines = css.splitlines()
    preview_lines = css_lines[: min(15, len(css_lines))]
    for line in preview_lines:
        print(line)
    if len(css_lines) > len(preview_lines):
        print("...")

    # ♿ Kontrastprüfung (wichtigste Text-auf-Hintergrund Kombinationen)
    print("\n♿ Kontrast-Check (WCAG >= 4.5 für normalen Text):")
    pairs = [
        ("text_primary", "background"),
        ("text_secondary", "background"),
        ("button_primary_text", "button_primary"),
        ("button_secondary_text", "button_secondary"),
        ("button_warning_text", "button_warning"),
        ("button_danger_text", "button_danger"),
    ]
    for fg_token, bg_token in pairs:
        fg = DesignSystem.get_color(fg_token)
        bg = DesignSystem.get_color(bg_token)
        ratio = DesignSystem.contrast_ratio(fg, bg)
        status = "OK" if ratio >= 4.5 else "WARN"
        print(f"{fg_token:<22} auf {bg_token:<22} → {ratio:5.2f} ({status})")

    print("\n✅ Self-Test abgeschlossen")


if __name__ == "__main__":
    run_self_test()
