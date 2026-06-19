# AI Forge Protocol

Most AI code assistants can draft something that looks right.
The Forge is built for the part where that code has to survive contact with reality.

AI Forge Protocol is a validation and patch-gating workflow for AI-assisted code changes. It wraps generated output in a reproducible harness, runs checks, and separates "looks plausible" from "actually safe to ship."

## What it does

- validates generated code before it gets executed
- runs a harness that compares behavior across perturbations
- keeps documentation grounded with placeholder checks
- stores investigation output so results can be reviewed later

## How to run it

```bash
source venv/bin/activate
python forge_harness.py
```

## Supporting scripts

- `scripts/run.sh` runs the main harness
- `scripts/verification_check.sh` checks docs for empty placeholders before release

## Related docs

- `docs/ENGINEERING_AUDIT.md`
- `docs/INTEGRATION_TARGETS.md`
- `docs/LEADERBOARD.md`

The goal is simple: keep the style, keep the edge, and make the result measurable.
