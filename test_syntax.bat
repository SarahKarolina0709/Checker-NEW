@echo off
echo Testing Quality GUI...
python -c "import py_compile; py_compile.compile('modern_translation_quality_gui.py', doraise=True); print('✅ Syntax OK')" 2>&1
if errorlevel 1 (
    echo ❌ Syntax Error found
) else (
    echo ✅ No syntax errors
)
pause
