#!/usr/bin/env python3
"""
Standalone script to generate beautiful HTML test report
Run this after pytest to create a custom styled report
"""

import subprocess
import sys
import json
from pathlib import Path


def run_tests_and_generate_report():
    """Run pytest and generate custom HTML report"""

    print("🧪 Running tests...")
    print("-" * 60)

    # Run pytest with JSON output
    result = subprocess.run(
        ['pytest', 'tests/', '-v', '--tb=short'],
        capture_output=False,
        text=True
    )

    print("-" * 60)

    if result.returncode == 0:
        print("✅ All tests passed!")
    else:
        print(f"⚠️  Some tests failed (exit code: {result.returncode})")

    # Check if report was generated
    report_path = Path('reports/test_report.html')
    if report_path.exists():
        print(f"\n✨ Custom HTML report generated successfully!")
        print(f"📊 Report location: {report_path.absolute()}")
        print(f"\n🌐 Open in browser:")
        print(f"   file://{report_path.absolute()}")
    else:
        print("\n⚠️  Report was not generated. Check for errors above.")

    return result.returncode


if __name__ == "__main__":
    sys.exit(run_tests_and_generate_report())
