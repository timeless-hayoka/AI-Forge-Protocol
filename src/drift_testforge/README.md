# DRIFT TestForge v0.3

**The emerging open standard for testing, validating, and shipping cognitive, persistent, interior-state AI systems.**

We don't just test outputs.  
We test how the *living system* holds together when memory drifts, homeostasis breaks, reflection is disabled, tools fail, or long context degrades.

This is the PyTest / OpenTelemetry / Docker equivalent for agentic cognitive architectures.

## Why This Matters

Most evals measure "does it answer correctly?"  
TestForge measures: **Does it break like a mind or like brittle code?**

- Semantic entropy (meaning diversity under stress)
- Behavioral consistency & action trace alignment
- Homeostatic / reflection depth proxies
- Causal impact ranking of subsystems (Shapley-style)
- Standardized, citable JSON scorecards

## Quick Start (Visible & Interactive)

```bash
cd /home/workdir/artifacts/drift_testforge

# 1. Run the real harness (Python, uses only numpy/scipy/pandas/matplotlib)
python run_testforge.py --repeats 6

# 2. Open the beautiful interactive dashboard (no server, works offline after load)
python run_ui.py
```

The dashboard is the **visible heart** of TestForge:
- Live animated scorecards & progress bars
- Radar chart + entropy bar visualization
- Causal impact ranking
- **Fully interactive**: edit model outputs in the browser → instantly recompute metrics
- Side-by-side model comparison
- One-click copy of the universal `TestForgeAdapter` contract
- Export production JSON scorecard for papers / CI / proof_of_work

## The Universal Contract (Priority #1 for adoption)

Any system implements this tiny interface:

```python
class TestForgeAdapter:
    def generate(self, prompt: str, context: dict = None) -> dict:
        return {
            "output": str,      # required
            "trace": list[str], # optional action trace
            "state": dict,      # optional internal state
            "metrics": dict     # optional
        }
```

DRIFT, LangGraph, CrewAI, raw OpenAI wrappers, Ollama — all plug in identically.

## Project Structure

```
drift_testforge/
├── metrics/
│   ├── semantic_entropy.py      # Lightweight n-gram embed + hierarchical clustering (no heavy deps)
│   └── additional_metrics.py    # Consistency, stability, reflection depth, causal impact
├── core/
│   └── harness.py               # The engine. Validation gates + parallel execution + reports
├── perturbations/
│   └── conditions.py            # Named reusable perturbations (memory_drift, homeostasis_imbalance, etc.)
├── utils/
│   └── validator.py             # Fail-fast interface + data checks (the boring consistency that wins)
├── examples/
│   └── dummy_adapter.py         # Reference implementation — swap for your real model
├── ui/
│   └── testforge_dashboard.html # The interactive visual standard (open this!)
├── visualization/
├── reports/                     # Generated JSONL + PNGs + scorecard.json
├── run_testforge.py
├── run_ui.py
└── README.md
```

## How to Plug Your Real System (DRIFT / INFJ-Bot)

1. Create `examples/drift_adapter.py`
2. Implement `generate()` by calling your `DriftBrain` / `CognitiveOrchestrator`
3. Replace `DummyAdapter` in `run_testforge.py`
4. Run. The `Validator` will catch any contract violations instantly.

## Becoming the Standard

TestForge wins by being:
- **Painfully simple** (one method to implement)
- **Shamelessly compatible** (works with anything)
- **Boringly consistent** (validation + seeds + JSONL export + reproducible reports)
- **Visually compelling** (the dashboard engineers actually screenshot and share)

This is how we move the field from "prompt engineering" to "cognitive systems engineering."

## Next (to lock leadership)

- Official DRIFT + LangGraph + Ollama reference adapters
- GitHub Action template (fail CI on stability regression)
- Public demo: "DRIFT vs LangGraph vs GPT-4o on same 5 prompts — side-by-side scorecard"

---

Built as part of the DRIFT / INFJ-Bot ecosystem by Julien James (@timelesshayoka).  
Local-first • Reproducible • Open source • Designed to become infrastructure.

Run the dashboard. See where your model actually stands. Then make it better. 🚀
