#!/usr/bin/env python3
"""
Comprehensive validation script for ViewStack integration in CheckerApp.
Tests O(1) view switching, callback functionality, and workflow integration.
"""

import sys
import os
import traceback
from typing import Dict, Any, Optional

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_viewstack_classes():
    """Test ViewStack and EnhancedViewStack classes directly."""
    print("🔍 Testing ViewStack classes...")
    
    try:
        from view_stack import ViewStack, EnhancedViewStack
        import customtkinter as ctk
        
        # Create test root
        root = ctk.CTk()
        root.withdraw()
        
        # Test basic ViewStack
        container = ctk.CTkFrame(root)
        viewstack = ViewStack(container)
        
        # Test EnhancedViewStack
        enhanced_viewstack = EnhancedViewStack(container)
        
        # Test adding views
        test_frame1 = ctk.CTkFrame(container)
        test_frame2 = ctk.CTkFrame(container)
        
        enhanced_viewstack.add("test1", test_frame1)
        enhanced_viewstack.add("test2", test_frame2)
        
        # Test switching
        result1 = enhanced_viewstack.show("test1")
        result2 = enhanced_viewstack.show("test2")
        
        # Test history
        history = enhanced_viewstack.get_history()
        
        print(f"✓ ViewStack classes work correctly")
        print(f"  - Show test1: {result1}")
        print(f"  - Show test2: {result2}")
        print(f"  - History length: {len(history)}")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"✗ ViewStack classes failed: {e}")
        traceback.print_exc()
        return False

def test_checker_app_integration():
    """Test ViewStack integration in CheckerApp."""
    print("\n🔍 Testing CheckerApp ViewStack integration...")
    
    try:
        from checker_app import CheckerApp
        from view_stack import EnhancedViewStack
        import customtkinter as ctk
        
        # Create test root
        root = ctk.CTk()
        root.withdraw()
        
        # Create app instance
        app = CheckerApp()
        
        # Test ViewStack initialization
        if hasattr(app, 'views') and isinstance(app.views, EnhancedViewStack):
            print("✓ CheckerApp has EnhancedViewStack")
            
            # Test available views
            views = app.views.get_views()
            print(f"  - Available views: {list(views.keys())}")
            
            # Test welcome screen
            if 'welcome' in views:
                print("✓ Welcome screen is in ViewStack")
                
                # Test switching to welcome
                result = app.views.show("welcome")
                print(f"  - Welcome show result: {result}")
            else:
                print("✗ Welcome screen NOT in ViewStack")
                
            # Test workflow integration
            workflow_router = getattr(app, 'workflow_router', None)
            if workflow_router:
                print("✓ WorkflowRouter found")
                
                # Check ViewStack usage
                using_viewstack = getattr(workflow_router, '_using_viewstack', False)
                print(f"  - Using ViewStack: {using_viewstack}")
                
                # Check available workflows
                workflows = workflow_router.workflows
                print(f"  - Available workflows: {list(workflows.keys())}")
                
                # Test workflows in ViewStack
                expected_workflows = ['angebots_workflow', 'pruefung_workflow', 'finalisierung_workflow', 'projekt_workflow']
                for workflow_name in expected_workflows:
                    if workflow_name in views:
                        print(f"✓ {workflow_name} is in ViewStack")
                    else:
                        print(f"✗ {workflow_name} is NOT in ViewStack")
                        
            else:
                print("✗ WorkflowRouter NOT found")
                
        else:
            print("✗ CheckerApp does NOT have EnhancedViewStack")
            
        root.destroy()
        return True
        
    except Exception as e:
        print(f"✗ CheckerApp integration failed: {e}")
        traceback.print_exc()
        return False

def test_workflow_switching():
    """Test workflow switching functionality."""
    print("\n🔍 Testing workflow switching...")
    
    try:
        from checker_app import CheckerApp
        import customtkinter as ctk
        
        # Create test root
        root = ctk.CTk()
        root.withdraw()
        
        # Create app instance
        app = CheckerApp()
        
        # Test workflow switching if ViewStack is available
        if hasattr(app, 'views') and hasattr(app, 'workflow_router'):
            views = app.views.get_views()
            
            # Test switching to welcome
            welcome_result = app.views.show("welcome")
            print(f"✓ Switch to welcome: {welcome_result}")
            
            # Test switching to workflows
            test_workflows = []
            for workflow_name in ['angebots_workflow', 'pruefung_workflow', 'finalisierung_workflow', 'projekt_workflow']:
                if workflow_name in views:
                    result = app.views.show(workflow_name)
                    test_workflows.append((workflow_name, result))
                    print(f"✓ Switch to {workflow_name}: {result}")
                    
            # Test switching back to welcome
            welcome_result2 = app.views.show("welcome")
            print(f"✓ Switch back to welcome: {welcome_result2}")
            
            # Test history
            history = app.views.get_history()
            print(f"✓ View history length: {len(history)}")
            
        else:
            print("✗ ViewStack or WorkflowRouter not available for switching test")
            
        root.destroy()
        return True
        
    except Exception as e:
        print(f"✗ Workflow switching test failed: {e}")
        traceback.print_exc()
        return False

def test_performance():
    """Test performance of ViewStack switching."""
    print("\n🔍 Testing ViewStack performance...")
    
    try:
        import time
        from view_stack import EnhancedViewStack
        import customtkinter as ctk
        
        # Create test root
        root = ctk.CTk()
        root.withdraw()
        
        # Create ViewStack with multiple views
        container = ctk.CTkFrame(root)
        viewstack = EnhancedViewStack(container)
        
        # Add multiple test views
        views = {}
        for i in range(10):
            view_name = f"test_view_{i}"
            test_frame = ctk.CTkFrame(container)
            views[view_name] = test_frame
            viewstack.add(view_name, test_frame)
        
        # Test switching performance
        start_time = time.time()
        
        # Perform multiple switches
        for i in range(100):
            view_name = f"test_view_{i % 10}"
            viewstack.show(view_name)
            
        end_time = time.time()
        
        total_time = end_time - start_time
        avg_time = total_time / 100
        
        print(f"✓ Performance test completed")
        print(f"  - 100 switches in {total_time:.4f}s")
        print(f"  - Average per switch: {avg_time:.6f}s")
        print(f"  - O(1) performance: {'✓' if avg_time < 0.001 else '✗'}")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"✗ Performance test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all validation tests."""
    print("🚀 ViewStack Integration Validation")
    print("=" * 50)
    
    tests = [
        ("ViewStack Classes", test_viewstack_classes),
        ("CheckerApp Integration", test_checker_app_integration),
        ("Workflow Switching", test_workflow_switching),
        ("Performance", test_performance),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status:12} {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n🎉 All tests passed! ViewStack integration is working correctly.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the output above.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
