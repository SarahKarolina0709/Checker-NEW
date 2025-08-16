@echo off
echo 🔥 QUICK TEST - Fixed Version
echo ============================

echo Testing fixes...
python -c "
try:
    from user_friendly_welcome_screen import SimplifiedWelcomeScreen
    import customtkinter as ctk
    
    root = ctk.CTk()
    root.withdraw()
    
    class TestApp: pass
    test_app = TestApp()
    
    welcome = SimplifiedWelcomeScreen(root, test_app)
    print('✅ App created successfully - No critical errors!')
    root.destroy()
except Exception as e:
    print(f'❌ Error: {e}')
"

echo.
echo 🚀 Starting fixed app...
python user_friendly_welcome_screen.py

pause
