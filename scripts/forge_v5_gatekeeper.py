#!/usr/bin/env python3
"""CLI entry for the shared Forge V5 syntax gatekeeper."""
from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from forge_v5_gatekeeper import ForgeValidator  # noqa: E402

if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: forge_v5_gatekeeper.py <target_directory>")
        sys.exit(1)

    target = sys.argv[1]
    print(f"🔥 INITIALIZING FORGE V5 GATEKEEPER ON: {target}")

    validator = ForgeValidator(target)
    report = validator.run_validation()

    print("\n📊 PARTIAL PASS INTELLIGENCE REPORT:")
    print(json.dumps(report, indent=2))

    if report["failed"] > 0:
        sys.exit(1)
    sys.exit(0)
