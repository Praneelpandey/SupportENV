"""
server/app.py — OpenEnv-compatible server entry point.

Re-exports the Flask app from the root app module.
"""

import sys
import os

# Add parent directory to path so we can import from root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app


def main():
    """Entry point for the server script."""
    app.run(debug=False, host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()
