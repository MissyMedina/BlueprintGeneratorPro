#!/usr/bin/env python3
"""
Test runner for the Guidance Blueprint Kit Pro project
"""

import unittest
import sys
import os
from pathlib import Path

def discover_and_run_tests():
    """Discover and run all tests in the tests directory"""
    
    # Add project directories to path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root / 'web_app'))
    sys.path.insert(0, str(project_root / 'validation_service'))
    
    # Discover tests
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print(f"\nFAILURES ({len(result.failures)}):")
        for test, traceback in result.failures:
            print(f"- {test}")
    
    if result.errors:
        print(f"\nERRORS ({len(result.errors)}):")
        for test, traceback in result.errors:
            print(f"- {test}")
    
    # Return success/failure
    return len(result.failures) == 0 and len(result.errors) == 0

def run_specific_test(test_name):
    """Run a specific test module"""
    
    # Add project directories to path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root / 'web_app'))
    sys.path.insert(0, str(project_root / 'validation_service'))
    
    # Load and run specific test
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(test_name)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return len(result.failures) == 0 and len(result.errors) == 0

def main():
    """Main test runner function"""
    
    print("🧪 Guidance Blueprint Kit Pro - Test Runner")
    print("="*60)
    
    if len(sys.argv) > 1:
        # Run specific test
        test_name = sys.argv[1]
        print(f"Running specific test: {test_name}")
        success = run_specific_test(test_name)
    else:
        # Run all tests
        print("Running all tests...")
        success = discover_and_run_tests()
    
    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
