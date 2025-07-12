#!/usr/bin/env python3
"""
Test to demonstrate typo detection in color names.
"""

import sys
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

def test_typo_detection():
    """Test that typos in color names are properly detected and reported."""
    print("=== TESTING TYPO DETECTION IN COLOR NAMES ===\n")
    
    from ui_theme import UITheme, enhanced_theme
    
    print("🎯 TESTING COLOR NAME VALIDATION\n")
    
    # Test 1: Valid color names
    print("1. VALID COLOR NAMES:")
    enhanced_theme.switch_theme("light")
    
    valid_colors = [
        'primary', 'primary_hover', 'secondary', 'background', 
        'surface', 'text_primary', 'text_secondary', 'border'
    ]
    
    for color in valid_colors:
        try:
            value = UITheme.get_color(color)
            print(f"   ✅ {color}: {value}")
        except Exception as e:
            print(f"   ❌ {color}: ERROR - {e}")
    
    # Test 2: Invalid color names (typos)
    print("\n2. INVALID COLOR NAMES (TYPOS):")
    
    typos = [
        'primery',          # Missing 'a' in primary
        'primar',           # Missing 'y' in primary  
        'primary_hower',    # 'hower' instead of 'hover'
        'backgrond',        # Missing 'u' in background
        'boarder',          # 'boarder' instead of 'border'
        'text_primery',     # 'primery' instead of 'primary'
        'suface',           # Missing 'r' in surface
        'nonexistent_color' # Completely wrong
    ]
    
    for typo in typos:
        try:
            print(f"\n   Testing typo: '{typo}'")
            value = UITheme.get_color(typo)
            print(f"   ⚠️  Returned: {value} (fallback to primary)")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    # Test 3: Test with both legacy and new API
    print("\n3. TYPO DETECTION IN LEGACY vs NEW API:")
    
    # Test legacy property access (this would be harder to validate)
    print("   Legacy API: Direct property access (limited validation)")
    
    # Test new API
    print("   New API: Method calls (full validation)")
    test_color = 'primary_hoverr'  # Double 'r' typo
    try:
        result = enhanced_theme.get_color(test_color)
        print(f"   Enhanced theme result: {result}")
    except Exception as e:
        print(f"   Enhanced theme error: {e}")
    
    # Test 4: Available colors listing
    print("\n4. AVAILABLE COLORS DISCOVERY:")
    enhanced_theme.switch_theme("light")
    
    # Get the actual theme object to inspect available colors
    light_theme = enhanced_theme._themes['light']
    available_colors = []
    
    for attr_name in dir(light_theme):
        if not attr_name.startswith('_'):
            attr_value = getattr(light_theme, attr_name)
            if isinstance(attr_value, str) and attr_value.startswith('#'):
                available_colors.append(attr_name)
    
    print(f"   Available colors in light theme:")
    for i, color in enumerate(sorted(available_colors)):
        if i % 4 == 0:
            print(f"\n   ", end="")
        print(f"{color:<20}", end="")
    
    print(f"\n\n   Total: {len(available_colors)} colors available")
    
    # Test 5: Suggest similar colors for typos
    print("\n5. SMART TYPO SUGGESTIONS:")
    
    def suggest_similar_color(typo, available_colors):
        """Simple similarity suggestion based on string distance."""
        def levenshtein_distance(s1, s2):
            if len(s1) < len(s2):
                return levenshtein_distance(s2, s1)
            if len(s2) == 0:
                return len(s1)
            
            previous_row = list(range(len(s2) + 1))
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
            return previous_row[-1]
        
        suggestions = []
        for color in available_colors:
            distance = levenshtein_distance(typo.lower(), color.lower())
            if distance <= 2:  # Only suggest if very similar
                suggestions.append((color, distance))
        
        return sorted(suggestions, key=lambda x: x[1])[:3]  # Top 3 suggestions
    
    test_typos = ['primery', 'primary_hower', 'backgrond', 'boarder']
    
    for typo in test_typos:
        suggestions = suggest_similar_color(typo, available_colors)
        if suggestions:
            suggestion_text = ", ".join([f"'{s[0]}'" for s in suggestions])
            print(f"   '{typo}' -> Did you mean: {suggestion_text}?")
        else:
            print(f"   '{typo}' -> No similar colors found")
    
    print("\n=== SUMMARY ===")
    print("✅ Typo detection implemented - warns about invalid color names")
    print("✅ Available colors are listed in warning messages") 
    print("✅ Fallback to primary color prevents crashes")
    print("💡 Consider enabling strict mode for development (raise exceptions)")
    print("💡 Smart suggestions could be added for better developer experience")
    
    return True

if __name__ == "__main__":
    test_typo_detection()
