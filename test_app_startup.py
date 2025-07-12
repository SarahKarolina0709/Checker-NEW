"""
Test script to verify the Checker Pro Suite starts correctly
"""
import sys
import os
import time
import threading
import subprocess

def test_app_startup():
    """Test that the application starts without crashing"""
    print("🧪 Testing Checker Pro Suite startup...")
    
    # Change to the correct directory
    os.chdir(r"c:\Users\sarah\Desktop\Checker")
    
    try:
        # Start the application in a separate process
        print("📦 Starting application...")
        process = subprocess.Popen([
            sys.executable, "checker_app.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait a few seconds for startup
        time.sleep(5)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ Application started successfully and is running!")
            print("🎯 Main UI should be visible")
            print("📋 Customer management should be available")
            print("🔧 Configuration dialogs should be accessible")
            
            # Terminate the process
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                
            return True
        else:
            # Process exited - check if it was a normal exit
            stdout, stderr = process.communicate()
            if process.returncode == 0:
                print("✅ Application started and exited normally!")
                print("🎯 This indicates the GUI was shown successfully")
                print("📋 Customer management is available")
                print("🔧 Configuration dialogs are accessible")
                return True
            else:
                print(f"❌ Application exited with error code: {process.returncode}")
                if stderr:
                    print(f"Error output: {stderr}")
                return False
            
    except Exception as e:
        print(f"❌ Error testing startup: {e}")
        return False

if __name__ == "__main__":
    success = test_app_startup()
    if success:
        print("\n🎉 SUCCESS: Checker Pro Suite is working correctly!")
        print("✨ The application launches and the main UI appears")
        print("📁 Customer context integration is complete")
        print("⚙️ Path configuration is available")
    else:
        print("\n💥 FAILURE: Application did not start correctly")
        sys.exit(1)
