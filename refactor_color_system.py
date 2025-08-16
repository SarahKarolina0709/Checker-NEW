#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎨 AUTOMATIC COLOR SYSTEM REFACTOR
==================================

Automatically refactors welcome_screen.py to use centralized get_color() calls
instead of hardcoded hex values and design_system['colors'] calls.

Usage:
    python refactor_color_system.py
"""

from datetime import datetime
import os
import re

COLOR_MAPPING = {
    # Primary colors
    '#1F4E79': 'primary',
    '#1A3F65': 'primary_hover',
    '#F0F7FF': 'primary_light',

    # Secondary colors
    '#6C757D': 'secondary',
    '#5A6268': 'secondary_hover',

    # Success colors
    '#2E8B57': 'success',
    '#256B43': 'success_hover',
    '#ECFDF5': 'success_light',
    '#10B981': 'success',
    '#059669': 'success',

    # Warning colors
    '#F2994A': 'warning',
    '#E08B3E': 'warning_hover',
    '#FEF3C7': 'warning_light',
    '#F59E0B': 'warning',

    # Error colors
    '#DC2626': 'error',
    '#B91C1C': 'error_hover',
    '#FEF2F2': 'error_light',
    '#EF4444': 'error',

    # Info colors
    '#2563EB': 'info',
    '#1D4ED8': 'info_hover',
    '#EFF6FF': 'info_light',
    '#3B82F6': 'info',

    # Surface colors
    '#FFFFFF': 'white',
    '#F8FAFC': 'background',
    '#F1F5F9': 'surface_secondary',
    '#F8F9FA': 'surface_secondary',

    # Border colors
    '#E5E7EB': 'border',
    '#D1D5DB': 'input_border',
    '#E0E0E0': 'border',

    # Text colors
    '#374151': 'text_primary',
    '#6B7280': 'text_secondary',
    '#9CA3AF': 'text_muted',

    # Anthracite theme
    '#4B5563': 'anthracite_600',
    '#1F2937': 'anthracite_800',
    '#2C3E50': 'anthracite_700',
    '#34495E': 'anthracite_600',

    # Grays
    '#111827': 'gray_900',
    '#475569': 'gray_600',

    # Special cases
    '#FAFBFC': 'surface',
    '#CBD5E1': 'border',
}

def backup_file(file_path):
    """Create backup of the file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{file_path}.backup_{timestamp}"

    with open(file_path, 'r', encoding='utf-8') as original:
        with open(backup_path, 'w', encoding='utf-8') as backup:
            backup.write(original.read())

    print(f"✅ Backup created: {backup_path}")
    return backup_path

def refactor_hex_colors(content):
    """Replace hex colors with get_color() calls"""

    replacements_made = 0

    for hex_color, color_name in COLOR_MAPPING.items():
        # Pattern for different contexts where colors appear
        patterns = [
            # fg_color="#1F4E79" -> fg_color=self.get_color('primary')
            (rf'fg_color="{re.escape(hex_color)}"', f'fg_color=self.get_color(\'{color_name}\')'),

            # text_color="#374151" -> text_color=self.get_color('text_primary')
            (rf'text_color="{re.escape(hex_color)}"', f'text_color=self.get_color(\'{color_name}\')'),

            # hover_color="#1A3F65" -> hover_color=self.get_color('primary_hover')
            (rf'hover_color="{re.escape(hex_color)}"', f'hover_color=self.get_color(\'{color_name}\')'),

            # border_color="#E5E7EB" -> border_color=self.get_color('border')
            (rf'border_color="{re.escape(hex_color)}"', f'border_color=self.get_color(\'{color_name}\')'),

            # progress_color="#1F4E79" -> progress_color=self.get_color('primary')
            (rf'progress_color="{re.escape(hex_color)}"', f'progress_color=self.get_color(\'{color_name}\')'),

            # Generic color= patterns
            (rf'color="{re.escape(hex_color)}"', f'color=self.get_color(\'{color_name}\')'),
        ]

        for pattern, replacement in patterns:
            before_count = len(re.findall(pattern, content))
            content = re.sub(pattern, replacement, content)
            after_count = len(re.findall(pattern, content))
            made = before_count - after_count
            replacements_made += made

            if made > 0:
                print(f"  {hex_color} -> get_color('{color_name}'): {made}x")

    return content, replacements_made

def refactor_design_system_calls(content):
    """Replace self.design_system['colors'] calls with get_color()"""

    replacements_made = 0

    # Pattern: self.design_system['colors']['color_name']
    pattern = r"self\.design_system\['colors'\]\['(\w+)'\]"

    def replace_match(match):
        nonlocal replacements_made
        color_name = match.group(1)
        replacements_made += 1
        return f"self.get_color('{color_name}')"

    content = re.sub(pattern, replace_match, content)

    if replacements_made > 0:
        print(f"  design_system['colors'] -> get_color(): {replacements_made}x")

    return content, replacements_made

def refactor_color_system():
    """Main refactoring function"""

    file_path = "welcome_screen.py"

    if not os.path.exists(file_path):
        print("❌ welcome_screen.py not found")
        return False

    print("🎨 STARTING AUTOMATIC COLOR SYSTEM REFACTOR")
    print("=" * 55)

    # Create backup
    backup_path = backup_file(file_path)

    # Read original file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    total_replacements = 0

    # Refactor hex colors
    print("\n🔧 REFACTORING HEX COLORS:")
    content, hex_replacements = refactor_hex_colors(content)
    total_replacements += hex_replacements

    # Refactor design system calls
    print("\n🔧 REFACTORING DESIGN_SYSTEM CALLS:")
    content, ds_replacements = refactor_design_system_calls(content)
    total_replacements += ds_replacements

    # Write refactored file
    if total_replacements > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"\n✅ REFACTORING COMPLETE!")
        print(f"📊 Total replacements: {total_replacements}")
        print(f"📁 Backup saved as: {backup_path}")
        print(f"📄 Refactored file: {file_path}")

        # Run color system test
        print(f"\n🧪 RUNNING POST-REFACTOR ANALYSIS...")
        os.system("python test_color_system.py")

        return True
    else:
        print("ℹ️ No replacements needed - color system already centralized!")
        return False

if __name__ == "__main__":
    print("🚀 Starting automatic color system refactor...")
    success = refactor_color_system()

    if success:
        print("\n🎉 Refactoring completed successfully!")
        print("💡 Next steps:")
        print("1. Test the application to ensure UI looks correct")
        print("2. Add any missing colors to get_color() fallback system")
        print("3. Remove backup file when satisfied with results")
    else:
        print("\n⚠️ Refactoring was not needed or failed.")