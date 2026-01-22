from design_system import DesignSystem

DesignSystem.apply_to_ctk(high_contrast=True)
print('High Contrast active colors (buttons):')
for k in ['button_primary','button_primary_hover','button_secondary','button_secondary_hover','button_danger','button_danger_hover']:
    print(k, DesignSystem.get_color(k))
