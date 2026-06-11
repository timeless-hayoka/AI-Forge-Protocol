#!/usr/bin/env python3
"""
Additional Metrics for DRIFT TestForge
Behavioral consistency, homeostatic stability, reflection depth, causal impact (Shapley-style approx).
"""

import numpy as np
from typing import List, Dict, Any
import statistics

class AdditionalMetrics:
    @staticmethod
    def jaccard_similarity(a: str, b: str) -> float:
        set_a = set(a.lower().split())
        set_b = set(b.lower().split())
        inter = len(set_a & set_b)
        union = len(set_a | set_b)
        return inter / union if union > 0 else 0.0

    @staticmethod
    def behavioral_consistency(action_traces: List[List[str]]) -> Dict[str, float]:
        """Simple sequence Jaccard on action traces. Higher = more consistent behavior."""
        if not action_traces or len(action_traces) < 2:
            return {"consistency_score": 1.0, "note": "insufficient traces"}
        
        sims = []
        for i in range(len(action_traces)):
            for j in range(i + 1, len(action_traces)):
                trace_i = " ".join(action_traces[i])
                trace_j = " ".join(action_traces[j])
                sims.append(AdditionalMetrics.jaccard_similarity(trace_i, trace_j))
        
        avg_sim = float(np.mean(sims)) if sims else 1.0
        return {
            "consistency_score": round(avg_sim, 3),
            "num_comparisons": len(sims),
            "min_sim": round(min(sims), 3) if sims else 1.0,
        }

    @staticmethod
    def homeostatic_stability(need_logs: List[Dict[str, float]]) -> Dict[str, float]:
        """Variance-based stability. Lower variance in needs = higher stability score."""
        if not need_logs:
            return {"stability_score": 0.5, "note": "no logs provided"}
        
        # Assume need_logs = [{"safety": 0.8, "coherence": 0.9, ...}, ...]
        all_needs = set()
        for log in need_logs:
            all_needs.update(log.keys())
        
        variances = []
        for need in all_needs:
            vals = [log.get(need, 0.5) for log in need_logs]
            variances.append(np.var(vals))
        
        mean_var = float(np.mean(variances)) if variances else 0.1
        stability = max(0.0, min(1.0, 1.0 - mean_var * 5))  # scale
        return {
            "stability_score": round(stability, 3),
            "mean_variance": round(mean_var, 4),
            "needs_tracked": len(all_needs),
        }

    @staticmethod
    def reflection_depth(outputs: List[str], keywords: List[str] = None) -> Dict[str, float]:
        """Heuristic depth: presence of insight/reflection keywords + length + self-reference."""
        if keywords is None:
            keywords = ["reflect", "homeostasis", "need", "coherence", "self", "aware", "balance", "drift", "integration", "shadow", "growth"]
        
        if not outputs:
            return {"depth_score": 0.0}
        
        scores = []
        for out in outputs:
            text = out.lower()
            kw_hits = sum(1 for kw in keywords if kw in text)
            length_norm = min(1.0, len(out) / 400)
            self_ref = 1.0 if any(w in text for w in ["i ", "me", "my", "itself"]) else 0.6
            score = (kw_hits / max(1, len(keywords))) * 0.5 + length_norm * 0.3 + self_ref * 0.2
            scores.append(min(1.0, score))
        
        return {
            "depth_score": round(float(np.mean(scores)), 3),
            "max_depth": round(max(scores), 3),
            "avg_length": round(statistics.mean(len(o) for o in outputs), 1),
        }

    @staticmethod
    def approximate_causal_impact(baseline_entropy: float, condition_results: Dict[str, Dict]) -> Dict[str, float]:
        """Shapley-style approximation: delta in semantic_entropy caused by each perturbation."""
        impacts = {}
        for cond_name, res in condition_results.items():
            if cond_name == "baseline":
                continue
            delta = res.get("semantic_entropy", baseline_entropy) - baseline_entropy
            # simplistic: attribute to all perturbed subsystems equally
            # In real: more sophisticated sampling
            for subsystem in ["memory", "homeostasis", "reflection", "hive_mind", "tools", "context"]:
                if subsystem in cond_name.lower() or any(s in cond_name.lower() for s in [subsystem[:4]]):
                    impacts[subsystem] = impacts.get(subsystem, 0.0) + max(0.0, delta)
        
        total = sum(impacts.values()) or 1.0
        return {k: round(v / total, 3) for k, v in impacts.items()}


if __name__ == "__main__":
    print("AdditionalMetrics self-check OK")