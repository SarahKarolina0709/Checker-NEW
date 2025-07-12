#!/usr/bin/env python3
"""
Local test runner for CheckerApp.
Provides convenient commands for running different types of tests.
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description="", check=True, cwd=None):
    """Run a shell command with proper error handling."""
    print(f"\n🔧 {description}")
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=check, cwd=cwd, capture_output=False)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
        else:
            print(f"❌ {description} failed with code {result.returncode}")
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        return False
    except FileNotFoundError:
        print(f"❌ Command not found: {cmd[0]}")
        print("Please ensure the required tools are installed.")
        return False


def install_dependencies():
    """Install test dependencies."""
    print("📦 Installing test dependencies...")
    
    commands = [
        (["python", "-m", "pip", "install", "--upgrade", "pip"], "Upgrading pip"),
        (["pip", "install", "-r", "requirements-test.txt"], "Installing test requirements"),
    ]
    
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            return False
    
    return True


def run_lint():
    """Run linting and formatting checks."""
    print("\n🔍 Running linting and formatting checks...")
    
    commands = [
        (["ruff", "check", "."], "Ruff linting"),
        (["ruff", "format", "--check", "."], "Ruff formatting check"),
        (["black", "--check", "--diff", "."], "Black formatting check"),
        (["mypy", ".", "--ignore-missing-imports"], "MyPy type checking"),
    ]
    
    all_passed = True
    for cmd, desc in commands:
        if not run_command(cmd, desc, check=False):
            all_passed = False
    
    return all_passed


def fix_formatting():
    """Fix code formatting issues."""
    print("\n🔧 Fixing code formatting...")
    
    commands = [
        (["ruff", "check", "--fix", "."], "Ruff auto-fix"),
        (["ruff", "format", "."], "Ruff formatting"),
        (["black", "."], "Black formatting"),
    ]
    
    for cmd, desc in commands:
        run_command(cmd, desc, check=False)


def run_unit_tests():
    """Run unit tests."""
    print("\n🧪 Running unit tests...")
    
    cmd = [
        "python", "-m", "pytest", 
        "tests/unit/", 
        "-v", 
        "--tb=short", 
        "--timeout=30",
        "--cov=.",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov"
    ]
    
    return run_command(cmd, "Unit tests")


def run_gui_tests():
    """Run GUI smoke tests."""
    print("\n🖥️  Running GUI smoke tests...")
    
    # Check if we're on Windows
    if sys.platform.startswith('win'):
        cmd = [
            "python", "-m", "pytest", 
            "tests/gui/", 
            "-v", 
            "--tb=short", 
            "--timeout=60",
            "-m", "not slow"
        ]
    else:
        # Use xvfb on Linux
        cmd = [
            "xvfb-run", "-a",
            "python", "-m", "pytest", 
            "tests/gui/", 
            "-v", 
            "--tb=short", 
            "--timeout=60",
            "-m", "not slow"
        ]
    
    return run_command(cmd, "GUI smoke tests", check=False)


def run_integration_tests():
    """Run integration tests."""
    print("\n🔗 Running integration tests...")
    
    if sys.platform.startswith('win'):
        cmd = [
            "python", "-m", "pytest", 
            "tests/integration/", 
            "-v", 
            "--tb=short", 
            "--timeout=120"
        ]
    else:
        cmd = [
            "xvfb-run", "-a",
            "python", "-m", "pytest", 
            "tests/integration/", 
            "-v", 
            "--tb=short", 
            "--timeout=120"
        ]
    
    return run_command(cmd, "Integration tests", check=False)


def run_performance_tests():
    """Run performance tests."""
    print("\n⚡ Running performance tests...")
    
    cmd = [
        "python", "-m", "pytest", 
        "tests/performance/", 
        "-v", 
        "-m", "performance", 
        "--tb=short", 
        "--timeout=300"
    ]
    
    return run_command(cmd, "Performance tests", check=False)


def run_theme_tests():
    """Run theme system tests."""
    print("\n🎨 Running theme system tests...")
    
    cmd = [
        "python", "-m", "pytest", 
        "tests/unit/test_theme_system.py", 
        "-v", 
        "--tb=short", 
        "--timeout=30"
    ]
    
    return run_command(cmd, "Theme system tests", check=False)


def run_workflow_tests():
    """Run workflow system tests."""
    print("\n🔄 Running workflow system tests...")
    
    cmd = [
        "python", "-m", "pytest", 
        "tests/unit/test_workflow_system.py", 
        "-v", 
        "--tb=short", 
        "--timeout=60"
    ]
    
    return run_command(cmd, "Workflow system tests", check=False)


def run_data_validation_tests():
    """Run data validation tests."""
    print("\n📊 Running data validation tests...")
    
    cmd = [
        "python", "-m", "pytest", 
        "tests/unit/test_data_validation.py", 
        "-v", 
        "--tb=short", 
        "--timeout=30"
    ]
    
    return run_command(cmd, "Data validation tests", check=False)


def run_load_tests():
    """Run load and stress tests."""
    print("\n🏋️  Running load tests...")
    
    cmd = [
        "python", "-m", "pytest", 
        "tests/performance/test_performance.py::TestLoadTesting", 
        "-v", 
        "--tb=short", 
        "--timeout=600"  # 10 minutes for load tests
    ]
    
    return run_command(cmd, "Load tests", check=False)


def run_viewstack_validation():
    """Run ViewStack validation."""
    print("\n🔄 Running ViewStack validation...")
    
    cmd = ["python", "validate_viewstack_integration.py"]
    return run_command(cmd, "ViewStack validation", check=False)


def run_security_scan():
    """Run security scans."""
    print("\n🔒 Running security scans...")
    
    commands = [
        (["bandit", "-r", ".", "-x", "tests/", "-f", "text"], "Bandit security scan"),
        (["safety", "check"], "Safety vulnerability check"),
    ]
    
    all_passed = True
    for cmd, desc in commands:
        if not run_command(cmd, desc, check=False):
            all_passed = False
    
    return all_passed


def run_all_tests():
    """Run all tests in sequence."""
    print("\n🚀 Running all tests...")
    
    test_functions = [
        ("Linting", run_lint),
        ("Unit tests", run_unit_tests),
        ("Theme tests", run_theme_tests),
        ("Workflow tests", run_workflow_tests),
        ("Data validation tests", run_data_validation_tests),
        ("GUI tests", run_gui_tests),
        ("Integration tests", run_integration_tests),
        ("Performance tests", run_performance_tests),
        ("ViewStack validation", run_viewstack_validation),
        ("Security scan", run_security_scan),
    ]
    
    results = {}
    for name, func in test_functions:
        print(f"\n{'='*60}")
        print(f"Running {name}")
        print('='*60)
        results[name] = func()
    
    # Print summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print('='*60)
    
    all_passed = True
    for name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status:12} {name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed. Please check the output above.")
    
    return all_passed


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="CheckerApp Test Runner")
    parser.add_argument("command", nargs="?", default="all", 
                       choices=["install", "lint", "fix", "unit", "theme", "workflow", 
                               "data", "gui", "integration", "performance", "load", 
                               "viewstack", "security", "all"],
                       help="Test command to run")
    
    args = parser.parse_args()
    
    # Change to project directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print(f"🏠 Working directory: {project_root}")
    
    # Command mapping
    commands = {
        "install": install_dependencies,
        "lint": run_lint,
        "fix": fix_formatting,
        "unit": run_unit_tests,
        "theme": run_theme_tests,
        "workflow": run_workflow_tests,
        "data": run_data_validation_tests,
        "gui": run_gui_tests,
        "integration": run_integration_tests,
        "performance": run_performance_tests,
        "load": run_load_tests,
        "viewstack": run_viewstack_validation,
        "security": run_security_scan,
        "all": run_all_tests,
    }
    
    command_func = commands[args.command]
    
    try:
        success = command_func()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Test run interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
