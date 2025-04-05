#!/usr/bin/env python3
"""
Test runner script for the Rotterdam Time Machine project.
Runs all tests and generates a coverage report.
"""

import unittest
import coverage
import sys
from pathlib import Path

def run_tests():
    """Run all tests and generate coverage report."""
    # Start coverage measurement
    cov = coverage.Coverage(
        source=['src'],
        omit=['*/__init__.py', '*/tests/*']
    )
    cov.start()

    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = str(Path(__file__).parent / 'tests')
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Stop coverage measurement and generate report
    cov.stop()
    cov.save()
    
    print('\nCoverage Summary:')
    cov.report()
    
    # Generate HTML report
    cov.html_report(directory='coverage_html')
    print('\nDetailed HTML coverage report generated in coverage_html/index.html')

    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1) 