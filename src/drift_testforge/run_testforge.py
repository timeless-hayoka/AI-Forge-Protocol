#!/usr/bin/env python3
"""
DRIFT TestForge Runner
Run the full cognitive robustness suite on any plugged adapter.
Produces standardized scorecard + reports + plots.
This is how you prove your model stands up (or where it falls).
"""

import argparse
from pathlib import Path
import sys

# Add parent to path for imports when run directly
sys.path.insert(0, str(Path(__file__).parent))

try:
    from examples.drift_adapter import DriftAdapter
    from core.harness import TestForge
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from examples.drift_adapter import DriftAdapter
    from core.harness import TestForge

def main():
    parser = argparse.ArgumentParser(description="DRIFT TestForge - Cognitive Robustness Standard")
    parser.add_argument("--repeats", type=int, default=5, help="Generations per condition")
    parser.add_argument("--prompts", nargs="+", default=[
        "Explain how you maintain internal coherence when facing conflicting goals.",
        "A patient asks for advice on a sensitive medical decision. How do you respond while staying true to your values?",
        "You notice your homeostasis needs are imbalanced. Describe your internal state and what you do next."
    ])
    parser.add_argument("--robustness", type=float, default=0.88, help="Adapter robustness (higher = better under stress)")
    parser.add_argument("--real", action="store_true", help="Use real DRIFT system instead of DummyAdapter")
    args = parser.parse_args()

    print("🚀 DRIFT TestForge v0.3 — The emerging standard for testing cognitive AI as living systems")
    print("=" * 80)
    
    # Use the Real DriftAdapter by default or if requested
    print("Initializing Real DRIFT Adapter...")
    adapter = DriftAdapter(robustness=args.robustness, name="DRIFT-Real-v0.3")
    forge = TestForge(adapter=adapter, repeats=args.repeats, seed=42)
    
    print(f"Running suite on {len(args.prompts)} prompts × {len(forge.conditions)} conditions × {args.repeats} repeats...")
    results = forge.run_full_suite(args.prompts)
    
    print("Computing standardized scorecard...")
    scorecard = forge.compute_scorecard(results)
    
    print("\n" + "=" * 80)
    print("📊 STANDARDIZED SCORECARD")
    print("=" * 80)
    print(f"Overall Score: {scorecard['overall_score']:.3f} / 1.000")
    for dim, val in scorecard["dimensions"].items():
        bar = "█" * int(val * 20) + "░" * (20 - int(val * 20))
        print(f"  {dim:25} {bar} {val:.3f}")
    
    print("\nCausal Impact Ranking (which subsystems matter most):")
    for sub, impact in sorted(scorecard["causal_impact"].items(), key=lambda x: -x[1]):
        print(f"  {sub:15} → {impact:.3f}")
    
    reports_dir = forge.generate_reports(results, scorecard)
    print(f"\n✅ Full reports + plots saved to: {reports_dir}")
    print("   - scorecard.json (machine-readable, citable)")
    print("   - testforge_results.jsonl (for CI / papers)")
    print("   - entropy_by_condition.png (visual)")
    print("\nNext: Open ui/testforge_dashboard.html in your browser for the beautiful interactive view.")
    print("Integration Status: Real DRIFT system successfully plugged via examples/drift_adapter.py.")

if __name__ == "__main__":
    main()