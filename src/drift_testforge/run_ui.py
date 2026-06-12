#!/usr/bin/env python3
"""
Launch the beautiful interactive TestForge Dashboard.
Just open the generated HTML in your browser — fully self-contained, no server needed.
"""

from pathlib import Path
import webbrowser
import sys

def main():
    dashboard_path = Path(__file__).parent / "ui" / "testforge_dashboard.html"
    
    if not dashboard_path.exists():
        print("❌ Dashboard not found. Run from the drift_testforge directory.")
        sys.exit(1)
    
    abs_path = dashboard_path.resolve()
    print("🚀 DRIFT TestForge Dashboard")
    print("=" * 50)
    print(f"Opening: {abs_path}")
    print("\nThis is a fully interactive, self-contained HTML dashboard.")
    print("Testers can:")
    print("  • Switch between model profiles (DRIFT, Baseline LLM, Fragile)")
    print("  • Edit sample outputs and instantly recompute metrics")
    print("  • See live radar, entropy bars, causal impact, dimension scores")
    print("  • Export standardized JSON scorecard")
    print("  • Copy the universal adapter contract")
    print("\nThis is how you make the standard visible and usable.")
    
    try:
        webbrowser.open(f"file://{abs_path}")
        print("\n✅ Dashboard opened in your default browser.")
    except Exception:
        print(f"\nOpen manually in browser:\nfile://{abs_path}")

if __name__ == "__main__":
    main()