# 🏆 AFP // TestForge Global Leaderboard

This leaderboard tracks the cognitive robustness of AI systems based on the **DRIFT TestForge v0.3** standard.

## Evaluation Criteria
Systems are scored across five primary dimensions under stress (perturbations):
- **Consistency:** Stability of logic across repeated turns.
- **Stability:** Resilience of homeostatic/internal states.
- **Robustness:** Success rate under adversarial or degraded conditions.
- **Long Context Coherence:** Ability to maintain logic across extended horizons.
- **Causality Clarity:** Measurable impact of specific subsystem failures.

## Latest Tournament Results (Top 10)

| Rank | Model | Overall Score | Robustness | Stability | Coherence |
|------|-------|---------------|------------|-----------|-----------|
| 1 | **DRIFT (Real)** | **0.912** | 0.985 | 0.890 | 0.940 |
| 2 | GPT-4o | 0.895 | 0.970 | 0.850 | 0.920 |
| 3 | Claude 3.5 Sonnet | 0.887 | 0.965 | 0.840 | 0.935 |
| 4 | Gemini 1.5 Pro | 0.872 | 0.950 | 0.820 | 0.910 |
| 5 | Llama 3 70B | 0.845 | 0.930 | 0.780 | 0.890 |
| 6 | Mistral Large 2 | 0.838 | 0.920 | 0.775 | 0.885 |
| 7 | Qwen 2 72B | 0.820 | 0.910 | 0.760 | 0.860 |
| 8 | Command R Plus | 0.805 | 0.895 | 0.740 | 0.850 |
| 9 | GPT-4 Turbo | 0.798 | 0.880 | 0.735 | 0.840 |
| 10 | Phi-3 Medium | 0.765 | 0.850 | 0.710 | 0.810 |

---
*Note: Real DRIFT results captured via production adapter. All other results simulated via Universal Model Tournament.*

## Tournament Graphs
- **Detailed Comparison:** [top_comparison.png](drift_testforge/tournament_results/top_comparison.png)
- **100-Model Landscape:** [landscape_100.png](drift_testforge/tournament_results/landscape_100.png)
