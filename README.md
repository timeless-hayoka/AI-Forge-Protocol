# 🛡️ AFP // AI Forge Protocol
> **The Emerging Standard for Testing Cognitive, Persistent, and Interior-State AI.**

Most AI passes tests. Very few survive **The FORGE.**

---

## 🧪 Why This Matters: Beyond Static Benchmarks
Standard AI evaluation (MMLU, GSM8K) is **state-blind**. It treats AI as a stateless function: *Input -> Output*. 

**The Forge (AFP)** treats AI as a **Living System**. We use **Causal Perturbation Testing** to measure how an AI’s reasoning trajectory shifts when its internal "cognitive organs" (simulated energy, being-layer, or memory salience) are programmatically ablated or stressed.

### ⚔️ The Protocol
1.  **Isolate:** Spawn a clean cognitive instance.
2.  **Perturb:** Inject entropy into specific internal state variables (e.g., zeroing out "Energy").
3.  **Analyze:** Measure the **Causal Emergence Score (CES)**—the delta between nominal and stressed reasoning.
4.  **Audit:** Verify **Behavioral Integrity**—does the AI "feel" the stress, or is it just hallucinating stability?

---

## 🚀 Quick Start

### 1. Run the Forge Harness
Execute the production-grade causality audit:
```bash
cd ai_forge_protocol
export PYTHONPATH=$PYTHONPATH:/home/crexs
bash run.sh
```

### 2. Launch the Dashboard
Visualize the results and record your model comparisons:
```bash
python3 infj_bot/interfaces/web_app.py
```
*Accessible at `http://localhost:8765`*

---

## 🔌 Universal Adapter Contract
To plug a new model into the Forge, implement the `AFPAdapter`:
```python
class MyModelAdapter(AFPAdapter):
    def get_internal_states(self):
        return {"energy": self.model.energy}
    
    def perturb(self, key, value):
        setattr(self.model, key, value)
```

---

## 📂 Project Structure
*   `forge_harness.py`: The production engine (Fixed: Isolated trials, Real Metrics).
*   `enhanced_harness_results/`: Verifiable audit logs and CES reports.
*   `index.html / style.css`: The "Control Room" UI for live recordings.
*   `ISSUE_TEMPLATES.md`: Roadmap for becoming the standard.

---

## 🏛️ Becoming the Standard
We are pivoting from a theoretical concept to **OpenTelemetry for AGI**.
*   **Consistency:** Every run is isolated; no shared state "poisoning" results.
*   **Visuals:** Real-time causal graphs (Coming soon).
*   **Verifiability:** No more fake scores. If the CES is 0.88, the reasoning chain actually snapped.

---

## 👑 AFP Leadership Locked
**Julien James (crex)** is the Architect of the Forge.
**Next Steps for Leadership:**
1.  **Execute Phase 5:** Integrate the `Shannon Entropy` metric for CES.
2.  **Viral Deployment:** Share the `COMMUNITY_OUTREACH.md` drafts on Reddit/LocalLLaMA.
3.  **Scale:** Benchmark the Top 5 AIs and publish the first **AFP Global Leaderboard**.

---
© 2026 PHI // DRIFT. *Most AI passes tests. Very few survive The FORGE.*
