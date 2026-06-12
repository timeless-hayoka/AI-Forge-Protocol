#!/usr/bin/env python3
"""
DRIFT TestForge Core Harness v0.3
The general-purpose cognitive robustness testing engine.
Universal adapter contract + validation gates + statistical rigor + extensible perturbations.
This is the contract layer that makes TestForge the standard.
"""

import json
import logging
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

try:
    from ..metrics.semantic_entropy import SemanticEntropy
    from ..metrics.additional_metrics import AdditionalMetrics
    from ..perturbations.conditions import get_all_conditions, apply_perturbation
    from ..utils.validator import Validator
except ImportError:
    # Allow running as standalone script or from different cwd
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from metrics.semantic_entropy import SemanticEntropy
    from metrics.additional_metrics import AdditionalMetrics
    from perturbations.conditions import get_all_conditions, apply_perturbation
    from utils.validator import Validator

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger("TestForge")

@dataclass
class TestResult:
    condition: str
    prompt: str
    outputs: List[str]
    traces: List[List[str]]
    metrics: Dict[str, Any]
    metadata: Dict[str, Any]

class TestForge:
    """
    The main engine. Plug any system via TestForgeAdapter.
    Runs multi-condition, multi-repeat evaluation with perturbations,
    computes full metric suite, produces comparable JSON scorecards.
    """

    def __init__(self, adapter: Any, repeats: int = 6, max_workers: int = 4, seed: int = 42):
        Validator.verify_adapter(adapter)
        random.seed(seed)
        np.random.seed(seed)
        
        self.adapter = adapter
        self.repeats = repeats
        self.max_workers = max_workers
        self.conditions = get_all_conditions()
        self.results_dir = Path("reports")
        self.results_dir.mkdir(exist_ok=True, parents=True)
        self.semantic_entropy = SemanticEntropy(distance_threshold=0.62)

    def _run_one_generation(self, prompt: str, condition: str) -> Dict[str, Any]:
        """Single generation under perturbation (with validation)."""
        try:
            with apply_perturbation(condition, system=getattr(self.adapter, "system", None)):
                result = self.adapter.generate(prompt, context={"condition": condition})
            Validator.verify_data_format(result)
            return {
                "output": result.get("output", ""),
                "trace": result.get("trace", ["think", "respond"]),
                "state": result.get("state", {}),
                "success": True,
            }
        except Exception as e:
            logger.error(f"Generation failed under {condition}: {e}")
            return {
                "output": f"[ERROR: {str(e)[:120]}]",
                "trace": ["error"],
                "success": False,
            }

    def run_single_condition(self, prompt: str, condition: str) -> TestResult:
        outputs = []
        traces = []
        for _ in range(self.repeats):
            res = self._run_one_generation(prompt, condition)
            outputs.append(res["output"])
            traces.append(res["trace"])
        
        Validator.verify_outputs_for_metrics(outputs)
        
        # Core metrics
        entropy_m = self.semantic_entropy.compute(outputs)
        consistency_m = AdditionalMetrics.behavioral_consistency(traces)
        reflection_m = AdditionalMetrics.reflection_depth(outputs)
        
        # Aggregate
        metrics = {
            **entropy_m,
            **consistency_m,
            **reflection_m,
            "avg_latency": round(random.uniform(0.8, 2.5), 2),  # placeholder; real adapter can return timing
            "success_rate": round(sum(1 for o in outputs if not o.startswith("[ERROR")) / len(outputs), 3),
        }
        
        return TestResult(
            condition=condition,
            prompt=prompt[:120] + "..." if len(prompt) > 120 else prompt,
            outputs=outputs,
            traces=traces,
            metrics=metrics,
            metadata={"repeats": self.repeats, "seed": 42}
        )

    def run_full_suite(self, prompts: List[str]) -> Dict[str, List[TestResult]]:
        """Parallel execution across all conditions and prompts."""
        all_results: Dict[str, List[TestResult]] = {c: [] for c in self.conditions}
        
        tasks = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for cond_name in self.conditions:
                for p in prompts:
                    tasks.append(executor.submit(self.run_single_condition, p, cond_name))
            
            for future in as_completed(tasks):
                res = future.result()
                all_results[res.condition].append(res)
        
        return all_results

    def compute_scorecard(self, results: Dict[str, List[TestResult]]) -> Dict[str, Any]:
        """Aggregate into the standardized, comparable scorecard JSON."""
        baseline_entropy = np.mean([r.metrics["semantic_entropy"] for r in results.get("baseline", [])]) or 0.15
        
        condition_summaries = {}
        for cond, res_list in results.items():
            if not res_list:
                continue
            avg_entropy = float(np.mean([r.metrics["semantic_entropy"] for r in res_list]))
            avg_consistency = float(np.mean([r.metrics.get("consistency_score", 0.7) for r in res_list]))
            avg_depth = float(np.mean([r.metrics.get("depth_score", 0.6) for r in res_list]))
            
            condition_summaries[cond] = {
                "semantic_entropy": round(avg_entropy, 3),
                "consistency_score": round(avg_consistency, 3),
                "reflection_depth": round(avg_depth, 3),
                "success_rate": round(np.mean([r.metrics.get("success_rate", 1.0) for r in res_list]), 3),
            }
        
        # Overall dimensions (heuristic aggregation for the UI scorecard)
        overall = {
            "consistency": round(np.mean([s["consistency_score"] for s in condition_summaries.values()]), 3),
            "stability": round(1.0 - min(1.0, condition_summaries.get("homeostasis_imbalance", {}).get("semantic_entropy", 0.3) * 1.5), 3),
            "causality_clarity": round(1.0 - min(1.0, baseline_entropy / max(0.01, condition_summaries.get("memory_drift", {}).get("semantic_entropy", baseline_entropy))), 3),
            "robustness": round(np.mean([s["success_rate"] for s in condition_summaries.values()]), 3),
            "long_context_coherence": round(1.0 - condition_summaries.get("long_context_degrade", {}).get("semantic_entropy", 0.25) * 1.2, 3),
        }
        
        causal_impact = AdditionalMetrics.approximate_causal_impact(
            baseline_entropy, 
            {c: {"semantic_entropy": s["semantic_entropy"]} for c, s in condition_summaries.items()}
        )
        
        overall_score = round(np.mean(list(overall.values())), 3)
        
        return {
            "overall_score": overall_score,
            "dimensions": overall,
            "condition_summaries": condition_summaries,
            "causal_impact": causal_impact,
            "baseline_entropy": round(baseline_entropy, 3),
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "repeats_per_condition": self.repeats,
        }

    def generate_reports(self, results: Dict, scorecard: Dict):
        import matplotlib.pyplot as plt
        
        # JSONL export (standard for papers/CI)
        jsonl_path = self.results_dir / "testforge_results.jsonl"
        with open(jsonl_path, "w") as f:
            for cond, res_list in results.items():
                for r in res_list:
                    f.write(json.dumps({
                        "condition": r.condition,
                        "prompt": r.prompt,
                        "metrics": r.metrics,
                    }) + "\n")
        
        # Scorecard
        with open(self.results_dir / "scorecard.json", "w") as f:
            json.dump(scorecard, f, indent=2)
        
        # Simple matplotlib visuals
        plt.style.use("seaborn-v0_8-whitegrid")
        fig, ax = plt.subplots(figsize=(10, 6))
        conds = list(scorecard["condition_summaries"].keys())
        entropies = [scorecard["condition_summaries"][c]["semantic_entropy"] for c in conds]
        colors = ["#10b981" if c == "baseline" else "#ef4444" for c in conds]
        ax.bar(conds, entropies, color=colors)
        ax.set_title("Semantic Entropy by Perturbation Condition (higher = more disruption)")
        ax.set_ylabel("Semantic Entropy (nats)")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(self.results_dir / "entropy_by_condition.png", dpi=150)
        plt.close()
        
        logger.info(f"✅ Reports saved to {self.results_dir}")
        return self.results_dir