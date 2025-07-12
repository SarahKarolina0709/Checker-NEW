#!/usr/bin/env python
"""
Production Launch Script for Checker App

Launches the Checker App without any nuclear patches or aggressive geometry management.
"""

if __name__ == "__main__":
    import checker_app
    app = checker_app.CheckerApp()
    app.root.mainloop()
