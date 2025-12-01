"""
Run Tests - Social Network Analysis
====================================
Convenient script to run test suite from project root.
"""

import sys
import os

# Add tests directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests'))
sys.path.insert(0, os.path.dirname(__file__))

if __name__ == "__main__":
    import test_suite
    test_suite.run_all_tests()
