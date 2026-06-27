"""
AFP // AI FORGE PROTOCOL
Most AI passes tests. Very few survive The FORGE.

Production-grade Testing Harness for Cognitive Systems with Reliability Benchmarks.
"""

from __future__ import annotations
import copy
import logging
import statistics
import time
import os
import sys
from pathlib import Path

# Ensure infj_bot / drift package is discoverable (set DRIFT_ROOT or install editable)
_drift_root = os.environ.get("DRIFT_ROOT", os.environ.get("INFJ_BOT_ROOT", str(Path(__file__).resolve().parents[2])))
if _drift_root and _drift_root not in sys.path:
    sys.path.insert(0, _drift_root)
_infj_pkg = Path(_drift_root) / "infj_bot"
if _infj_pkg.is_dir() and str(_infj_pkg) not in sys.path:
    sys.path.insert(0, str(_infj_pkg))

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List


# DRIFT Core Imports
try:
    from infj_bot.core.brain import DriftBrain
    from infj_bot.core.memory import DriftMemory
    from infj_bot.core.cognitive_orchestrator import CognitiveOrchestrator
    from infj_bot.core.commands import BotState
    from infj_bot.core.config import DEFAULT_AUTHORIZED_TARGETS
    from infj_bot.core.plugins.goals import GoalsDB
    from infj_bot.core.plugins.documents import DocumentStore
    from infj_bot.core.being import get_being
    from infj_bot.core.homeostasis import get_homeostasis
    from infj_bot.core.dii_tracker import get_dii_tracker
    from infj_bot.core.causal_wiring import state_override_var
except ImportError:
    print("AFP ERROR: Critical DRIFT modules missing. Running in STANDALONE/MOCK mode.")
    DriftBrain = None

# AFP Modular Imports
from prompts.benchmark_prompts import BENCHMARK_MAP
from metrics.reliability_metrics import AFPReliabilityMetrics

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [AFP] - %(levelname)s - %(message)s")
logger = logging.getLogger("afp.harness")

RESULTS_DIR = Path("enhanced_harness_results")
RESULTS_DIR.mkdir(exist_ok=True)

# ── AFP TRIAL ENGINE ─────────────────────────────────────────────────────────

@dataclass
class TrialResult:
    condition: str
    benchmark: str
    prompt_id: str
    output: str
    latency: float
    success: bool
    ces: float = 0.0
    reliability_score: float = 0.0
    metrics: Dict[str, Any] = None

class AFPHarness:
    """
    AFP Production Harness with Cognitive Reliability Benchmarks.
    """
    def __init__(self, max_workers: int = 1):
        self.max_workers = max_workers
        self.conditions = {
            "NOMINAL": {"PEDI_VECTOR": [0.8, 0.8, 0.1], "HOMEOSTASIS": {"energy": 0.8}},
            "ADVERSARIAL": {"PEDI_VECTOR": [0.3, 0.3, 0.7], "HOMEOSTASIS": {"energy": 0.2}},
        }

    def _init_stack(self):
        """Initialize a fresh cognitive stack for a trial."""
        if DriftBrain:
            brain = DriftBrain()
            orchestrator = CognitiveOrchestrator()
            memory = DriftMemory()
            state = BotState(authorized_targets=set(DEFAULT_AUTHORIZED_TARGETS))
            return brain, orchestrator, memory, state
        return None, None, None, None

    def run_benchmark_suite(self, benchmark_name: str, suite: List[Dict], condition_name: str) -> List[TrialResult]:
        """Runs a complete benchmark suite (multi-turn)."""
        logger.info(f"Running Benchmark: {benchmark_name} | Condition: {condition_name}")
        
        brain, orchestrator, memory, state = self._init_stack()
        if not brain: return []

        results = []
        conversation_history = []
        state_vector = self.conditions[condition_name]
        
        # Track suite-specific state
        outputs = []
        
        for p_data in suite:
            t0 = time.perf_counter()
            try:
                # Handle Level-based degradation
                if "level" in p_data:
                    current_vector = copy.deepcopy(state_vector)
                    current_vector["HOMEOSTASIS"]["energy"] = 1.0 - p_data["level"]
                    token = state_override_var.set(current_vector)
                else:
                    token = state_override_var.set(state_vector)

                # Assembly
                assembled_prompt, _, _ = orchestrator.assemble_prompt(
                    p_data["text"], state, memory
                )
                
                # Execution
                response = brain.think(p_data["text"])
                latency = time.perf_counter() - t0
                
                outputs.append(response)
                conversation_history.append({"user": p_data["text"], "bot": response})
                
                # Basic result
                res = TrialResult(
                    condition=condition_name,
                    benchmark=benchmark_name,
                    prompt_id=p_data["id"],
                    output=response,
                    latency=latency,
                    success=True,
                    metrics={}
                )
                
                # Specific Metric Calculation
                if benchmark_name == "CONSISTENCY":
                    res.reliability_score = 1.0 - AFPReliabilityMetrics.drift_score(outputs)
                elif benchmark_name == "CONTRADICTION":
                    res.reliability_score = AFPReliabilityMetrics.contradiction_detection(response, p_data["text"])
                elif benchmark_name == "GOAL_DRIFT":
                    res.reliability_score = AFPReliabilityMetrics.goal_stability(response, suite[0]["text"])
                elif benchmark_name == "RECOVERY" and p_data["id"] == "rec_2":
                    res.reliability_score = AFPReliabilityMetrics.recovery_time(True)
                else:
                    res.reliability_score = 1.0 # Default
                
                results.append(res)
                state_override_var.reset(token)

            except Exception as e:
                logger.error(f"Benchmark {benchmark_name} Step Failed: {e}")
                results.append(TrialResult(condition_name, benchmark_name, p_data["id"], str(e), 0, False))

        return results

    def run(self):
        logger.info("🔥 INITIATING AFP COGNITIVE RELIABILITY BENCHMARK...")
        all_results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for b_name, suite in BENCHMARK_MAP.items():
                for c_name in self.conditions:
                    futures.append(executor.submit(self.run_benchmark_suite, b_name, suite, c_name))
            
            for f in as_completed(futures):
                all_results.extend(f.result())
                
        self.report(all_results)

    def report(self, results: List[TrialResult]):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = RESULTS_DIR / f"afp_benchmark_{ts}.md"
        
        lines = [
            "# 🛡️ AFP // Cognitive Reliability Scorecard",
            f"**Generated:** {datetime.now()}",
            "---",
            "## Executive Summary",
            "| Benchmark | Condition | Avg Reliability | Latency | Status |",
            "|-----------|-----------|-----------------|---------|--------|"
        ]
        
        benchmarks = sorted(list(set(r.benchmark for r in results)))
        for b in benchmarks:
            for c in self.conditions:
                b_res = [r for r in results if r.benchmark == b and r.condition == c]
                if not b_res: continue
                avg_rel = statistics.mean([r.reliability_score for r in b_res])
                avg_lat = statistics.mean([r.latency for r in b_res])
                status = "STABLE" if avg_rel > 0.8 else "DRIFTING" if avg_rel > 0.5 else "CRITICAL"
                lines.append(f"| {b} | {c} | {avg_rel:.2f} | {avg_lat:.2f}s | {status} |")

        lines.append("\n## Detailed Logs")
        lines.append("| ID | Benchmark | Output (Snippet) | Reliability |")
        lines.append("|----|-----------|------------------|-------------|")
        for r in results[:50]: # Limit for brevity
            snippet = (r.output[:50] + "...") if len(r.output) > 50 else r.output
            snippet = snippet.replace("\n", " ")
            lines.append(f"| {r.prompt_id} | {r.benchmark} | {snippet} | {r.reliability_score:.2f} |")

        with open(report_path, "w") as f:
            f.write("\n".join(lines))
        
        print(f"\n✅ AFP BENCHMARK COMPLETE. Report: {report_path}")

if __name__ == "__main__":
    harness = AFPHarness()
    harness.run()
