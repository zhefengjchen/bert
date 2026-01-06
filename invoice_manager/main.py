#!/usr/bin/env python3
"""
Invoice Management System
A local Windows desktop application for managing Excel-based invoice data
from multiple testing labs (BV, ITS, TUV, SGS).

Author: Invoice Manager Team
Version: 1.0.0
"""

import sys
import os

# Add the package directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import InvoiceManagerApp


def main():
    """Main entry point for the Invoice Management System."""
    print("Starting Invoice Management System...")

    try:
        app = InvoiceManagerApp()
        app.mainloop()
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
