#!/usr/bin/env python3
"""
Slice 6 Test Runner

This script runs all Slice 6 tests according to the test plan.
Usage:
    python run_slice6_tests.py [--unit] [--integration] [--e2e] [--frontend] [--all]
"""

import subprocess
import sys
import argparse
import time
from pathlib import Path


def run_command(cmd, description):
    """Run a command and return success status."""
    print(f"\n🧪 {description}")
    print(f"Running: {' '.join(cmd)}")
    print("-" * 60)
    
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    end_time = time.time()
    
    duration = end_time - start_time
    
    if result.returncode == 0:
        print(f"✅ {description} - PASSED ({duration:.2f}s)")
        if result.stdout:
            print("Output:", result.stdout[-500:])  # Last 500 chars
        return True
    else:
        print(f"❌ {description} - FAILED ({duration:.2f}s)")
        if result.stderr:
            print("Error:", result.stderr[-500:])  # Last 500 chars
        if result.stdout:
            print("Output:", result.stdout[-500:])  # Last 500 chars
        return False


def run_unit_tests():
    """Run unit tests."""
    tests = [
        "tests/test_slice6_download.py",
        "tests/test_slice6_storage.py", 
        "tests/test_slice6_worker.py",
        "tests/test_slice6_email.py"
    ]
    
    cmd = ["python", "-m", "pytest", "-v", "--tb=short", "-m", "unit"] + tests
    return run_command(cmd, "Unit Tests")


def run_integration_tests():
    """Run integration tests."""
    cmd = ["python", "-m", "pytest", "-v", "--tb=short", "-m", "integration", "tests/test_slice6_e2e.py"]
    return run_command(cmd, "Integration Tests")


def run_e2e_tests():
    """Run end-to-end tests."""
    cmd = ["python", "-m", "pytest", "-v", "--tb=short", "-m", "e2e", "tests/test_slice6_e2e.py"]
    return run_command(cmd, "End-to-End Tests")


def run_frontend_tests():
    """Run frontend tests."""
    cmd = ["python", "-m", "pytest", "-v", "--tb=short", "-m", "frontend", "tests/test_slice6_frontend.py"]
    return run_command(cmd, "Frontend Tests")


def run_performance_tests():
    """Run performance tests."""
    cmd = ["python", "-m", "pytest", "-v", "--tb=short", "-m", "slow", "tests/"]
    return run_command(cmd, "Performance Tests")


def run_security_tests():
    """Run security tests."""
    cmd = ["python", "-m", "pytest", "-v", "--tb=short", "-k", "security", "tests/"]
    return run_command(cmd, "Security Tests")


def check_test_environment():
    """Check if test environment is properly set up."""
    print("🔍 Checking test environment...")
    
    # Check if pytest is installed
    try:
        subprocess.run(["python", "-m", "pytest", "--version"], 
                      capture_output=True, check=True)
        print("✅ pytest is installed")
    except subprocess.CalledProcessError:
        print("❌ pytest is not installed. Install with: pip install pytest")
        return False
    
    # Check if test files exist
    test_files = [
        "tests/test_slice6_download.py",
        "tests/test_slice6_storage.py",
        "tests/test_slice6_worker.py", 
        "tests/test_slice6_email.py",
        "tests/test_slice6_e2e.py",
        "tests/test_slice6_frontend.py"
    ]
    
    missing_files = []
    for test_file in test_files:
        if not Path(test_file).exists():
            missing_files.append(test_file)
    
    if missing_files:
        print(f"❌ Missing test files: {missing_files}")
        return False
    
    print("✅ All test files present")
    return True


def generate_test_report(results):
    """Generate a test report."""
    print("\n" + "="*60)
    print("📊 SLICE 6 TEST REPORT")
    print("="*60)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    failed_tests = total_tests - passed_tests
    
    print(f"Total Test Suites: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print("\nDetailed Results:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    if failed_tests == 0:
        print("\n🎉 ALL TESTS PASSED! Slice 6 is ready for production.")
        return True
    else:
        print(f"\n⚠️  {failed_tests} test suite(s) failed. Please review and fix.")
        return False


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description="Slice 6 Test Runner")
    parser.add_argument("--unit", action="store_true", help="Run unit tests")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--e2e", action="store_true", help="Run end-to-end tests")
    parser.add_argument("--frontend", action="store_true", help="Run frontend tests")
    parser.add_argument("--performance", action="store_true", help="Run performance tests")
    parser.add_argument("--security", action="store_true", help="Run security tests")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    
    args = parser.parse_args()
    
    # Check environment
    if not check_test_environment():
        sys.exit(1)
    
    # Determine which tests to run
    if args.all:
        test_types = ["unit", "integration", "e2e", "frontend", "performance", "security"]
    else:
        test_types = []
        if args.unit:
            test_types.append("unit")
        if args.integration:
            test_types.append("integration")
        if args.e2e:
            test_types.append("e2e")
        if args.frontend:
            test_types.append("frontend")
        if args.performance:
            test_types.append("performance")
        if args.security:
            test_types.append("security")
    
    if not test_types:
        print("No test types specified. Use --help for options or --all for all tests.")
        sys.exit(1)
    
    # Run tests
    results = {}
    
    if "unit" in test_types:
        results["Unit Tests"] = run_unit_tests()
    
    if "integration" in test_types:
        results["Integration Tests"] = run_integration_tests()
    
    if "e2e" in test_types:
        results["E2E Tests"] = run_e2e_tests()
    
    if "frontend" in test_types:
        results["Frontend Tests"] = run_frontend_tests()
    
    if "performance" in test_types:
        results["Performance Tests"] = run_performance_tests()
    
    if "security" in test_types:
        results["Security Tests"] = run_security_tests()
    
    # Generate report
    success = generate_test_report(results)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
