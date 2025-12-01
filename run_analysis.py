"""
Main Entry Point - Social Network Analysis
===========================================
Convenient script to run the main analysis from project root.
"""

import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))
sys.path.insert(0, os.path.dirname(__file__))

if __name__ == "__main__":
    import main
    main.main()
