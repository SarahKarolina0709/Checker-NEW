import ast
import sys
import traceback

print("🔍 COMPREHENSIVE ERROR ANALYSIS")
print("="*50)

# Test 1: AST Parse
print("1. Testing AST parsing...")
try:
    with open('modern_translation_quality_gui.py', 'r', encoding='utf-8') as f:
        content = f.read()
    ast.parse(content)
    print("✅ AST Parse: SUCCESS")
    ast_ok = True
except SyntaxError as e:
    print(f"❌ Syntax Error at line {e.lineno}: {e.msg}")
    if e.text:
        print(f"   Text: {repr(e.text[:100])}")
    ast_ok = False
except Exception as e:
    print(f"❌ Parse Error: {e}")
    ast_ok = False

# Test 2: Import Test
print("\n2. Testing import...")
try:
    if 'modern_translation_quality_gui' in sys.modules:
        del sys.modules['modern_translation_quality_gui']
    import modern_translation_quality_gui
    print("✅ Import: SUCCESS")
    import_ok = True
except Exception as e:
    print(f"❌ Import Error: {e}")
    traceback.print_exc()
    import_ok = False

# Test 3: Class Check
if import_ok:
    print("\n3. Testing main class...")
    try:
        app_class = getattr(modern_translation_quality_gui, 'ProfessionalTranslationQualityApp', None)
        if app_class:
            print("✅ Main class found")
            class_ok = True
        else:
            print("❌ Main class missing")
            class_ok = False
    except Exception as e:
        print(f"❌ Class check error: {e}")
        class_ok = False
else:
    class_ok = False

# Test 4: Function Check
if import_ok:
    print("\n4. Testing main function...")
    try:
        main_func = getattr(modern_translation_quality_gui, 'main', None)
        if main_func:
            print("✅ Main function found")
            main_ok = True
        else:
            print("❌ Main function missing")
            main_ok = False
    except Exception as e:
        print(f"❌ Function check error: {e}")
        main_ok = False
else:
    main_ok = False

# Summary
print("\n" + "="*50)
print("📋 SUMMARY:")
print(f"   AST Parse:     {'✅ PASS' if ast_ok else '❌ FAIL'}")
print(f"   Import Test:   {'✅ PASS' if import_ok else '❌ FAIL'}")
print(f"   Main Class:    {'✅ PASS' if class_ok else '❌ FAIL'}")
print(f"   Main Function: {'✅ PASS' if main_ok else '❌ FAIL'}")

if all([ast_ok, import_ok, class_ok, main_ok]):
    print("\n🎉 ALL TESTS PASSED - Quality GUI is working!")
else:
    print("\n❌ ISSUES FOUND - Further fixes needed!")

print("="*50)