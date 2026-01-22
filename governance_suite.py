"""Governance Suite Runner

Führt in definierter Reihenfolge aus:
1. Konsistenz / Namespace Policy Check
2. Pytest Smoke-Test für _handle_error Kontexte

Exit Codes:
 0 = Alles OK
 3 = Konsistenz / Logger Fehler (durchgereicht)
 4 = Namespace Policy Verstoß (durchgereicht)
 >=5 = Testfehler oder unerwarteter Fehler

Nutzung:
  python governance_suite.py
"""
from __future__ import annotations
import subprocess, sys, shutil


def run(cmd: list[str], desc: str) -> int:
    print(f"\n=== {desc} ===")
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True)
        print(proc.stdout)
        if proc.stderr:
            print(proc.stderr, file=sys.stderr)
        return proc.returncode
    except FileNotFoundError:
        print(f"Werkzeug nicht gefunden: {' '.join(cmd)}", file=sys.stderr)
        return 127


def main() -> int:
    # 1) Konsistenz
    code_consistency = run([sys.executable, "check_error_handling_consistency.py"], "Konsistenz / Namespace Policy")
    if code_consistency in (3, 4):
        print("Abbruch wegen Policy-Verstoß.")
        return code_consistency

    # 2) Tests
    if shutil.which("pytest"):
        code_tests = run([sys.executable, "-m", "pytest", "-q", "test_error_contexts.py"], "Smoke-Test _handle_error")
        if code_tests != 0:
            return 5
    else:
        print("Pytest nicht installiert – überspringe Testphase.")

    return code_consistency if code_consistency != 0 else 0


if __name__ == "__main__":
    sys.exit(main())
