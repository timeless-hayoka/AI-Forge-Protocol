# GitHub Issue Templates: Good First Issues

---

## Issue 1: [Python Dev] Add Support for Async Perturbation Handlers
**Label:** `good first issue`, `enhancement`, `Python`
**Role:** Python Developer

### Description
Currently, the perturbation harness in `forge_harness.py` handles component state swaps synchronously. To support more complex cognitive models (like LangGraph or CrewAI), we need to allow for `async` getter and setter functions within the `ComponentRegistry`.

### Task
- Modify `ComponentRegistry` to detect if a getter/setter is a coroutine.
- Update `run_trial` to properly `await` these calls if necessary.
- Add a unit test in a new `tests/test_registry.py` file to verify async support.

### Resources
- File: `ai_forge_protocol/forge_harness.py`
- Look at the `ComponentRegistry` class (line 100+).

---

## Issue 2: [ML Engineer] Implement Shannon Entropy for CES Metric
**Label:** `good first issue`, `math`, `ML Engineer`
**Role:** ML Engineer

### Description
The Causal Emergence Score (CES) currently uses a basic semantic similarity delta. We want to move towards a more robust Information Theory approach by calculating the **Shannon Entropy** between the baseline output distribution and the perturbed output distribution.

### Task
- Implement a `calculate_entropy_delta` function in `forge_harness.py`.
- Integrate this function into the `CES` calculation loop.
- Document the math used in a comment for transparency.

### Resources
- File: `ai_forge_protocol/forge_harness.py`
- See existing `CES` calculation logic.

---

## Issue 3: [Frontend Dev] Create a Basic D3.js Causal Tree
**Label:** `good first issue`, `frontend`, `React`
**Role:** Frontend Developer

### Description
We have raw JSON output from the harness, but we need a way to visualize which "internal states" (Aura, Logic, Energy) are driving the final output. We need a basic React component using D3.js to render these as a directed tree.

### Task
- Create a simple `CausalGraph` component in `index.html` (or a new JS file).
- The graph should take the `enhanced_harness_results/latest_result.json` as input.
- Render nodes for each internal state and edges showing their influence weights.

### Resources
- File: `ai_forge_protocol/index.html`
- JSON Schema: See `enhanced_harness_results/` for sample structure.

---

## Issue 4: [Documentation] Standardize Error Logging in Harness
**Label:** `good first issue`, `cleanup`
**Role:** Python Developer / Documentation

### Description
The `forge_harness.py` uses a mix of `print()` statements and `logger.info()`. We need to standardize this to use the Python `logging` module exclusively with appropriate levels (`DEBUG`, `INFO`, `WARNING`, `ERROR`).

### Task
- Audit `forge_harness.py` for any `print()` calls.
- Replace them with appropriate `logger` calls.
- Ensure that stack traces are captured in `ERROR` logs during trial failures.

### Resources
- File: `ai_forge_protocol/forge_harness.py`
