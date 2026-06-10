"""
THE FORGE (A.F.P)
"Most ais pastest"

DRIFT / INFJ-Bot Enhanced Causality & Testing Harness v2
More robust, extensible, statistically sound replacement/improvement over causality_harness.py
"""

from __future__ import annotations
import asyncio
import copy
import json
import logging
import random
import statistics
import time
import re
import math
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np
from scipy import stats

# Project imports
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
    from infj_bot.core.global_workspace import get_workspace
    from infj_bot.core.shadow import get_shadow
except ImportError:
    print("Warning: Could not import some DRIFT core modules. Running in degraded/standalone mode.")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

RESULTS_DIR = Path("enhanced_harness_results")
RESULTS_DIR.mkdir(exist_ok=True)

# ── STATE MOCK OBJECTS (From v1) ──────────────────────────────────────────────

class MockBeing:
    def __init__(self, mood="neutral", energy=0.5, curiosity=0.5, attachment=0.5):
        self.state = type("State", (), {
            "mood": mood, "energy": energy, "curiosity": curiosity, "attachment": attachment,
            "to_dict": lambda: {"mood": mood, "energy": energy, "curiosity": curiosity, "attachment": attachment}
        })()
        self.agency = type("Agency", (), {"self_awareness": 0.5, "volition": 0.5, "autonomy_drive": 0.5})()
        self.working_memory = []
    def format_being_prompt(self) -> str:
        return f"[Being State]\nmood: {self.state.mood}\nenergy: {self.state.energy:.2f}\ncuriosity: {self.state.curiosity:.2f}\n"

class MockHomeostasis:
    def __init__(self, needs=None, crisis_mode=False):
        self.needs = needs or {}
        self.crisis_mode = crisis_mode
        self.weather = "clear"
        self.allostatic_load = 0.0
        self.mood_ema = 0.5
    def get_need_summary(self) -> dict:
        return {k: {"current": v["current"], "setpoint": v.get("setpoint", 0.5)} for k, v in self.needs.items()}
    def compute_free_energy(self, *a, **k): return self.allostatic_load
    def background_cycle(self, *a, **k): pass

class MockDII:
    def __init__(self, dii_score=0.01):
        self.dii_score = dii_score
        self.trend = "flat"
    def get_trend(self, n=20):
        return {"dii_current": self.dii_score, "trend": self.trend, "components": {"p": 0.2, "i": 0.2, "phi": 0.2, "e": 0.2, "d": 0.2}}
    def compute(self, *a, **k): pass

# ── COMPONENT REGISTRY ────────────────────────────────────────────────────────

class ComponentRegistry:
    """Central registry for testable components and perturbation strategies."""
    def __init__(self):
        self.components = {}
    
    def register(self, name: str, getter: Callable, setter: Optional[Callable] = None):
        self.components[name] = {"getter": getter, "setter": setter}
    
    def get(self, name):
        return self.components.get(name)

def set_being_instance(instance):
    import infj_bot.core.being as being_mod
    being_mod._being_instance = instance

def set_homeostasis_instance(instance):
    import infj_bot.core.homeostasis as homeo_mod
    homeo_mod._homeostasis_instance = instance

def set_dii_instance(instance):
    import infj_bot.core.dii_tracker as dii_mod
    dii_mod._dii_instance = instance

registry = ComponentRegistry()
try:
    registry.register("being", get_being, set_being_instance)
    registry.register("homeostasis", get_homeostasis, set_homeostasis_instance)
    registry.register("dii", get_dii_tracker, set_dii_instance)
except NameError:
    pass

@contextmanager
def perturb_component(registry: ComponentRegistry, condition: Dict):
    """Context manager for safe, reversible perturbations."""
    originals = {}
    try:
        perturbations = condition.get("perturb", {})
        for comp_name, mode in perturbations.items():
            info = registry.get(comp_name)
            if info:
                originals[comp_name] = info["getter"]()
                if info["setter"]:
                    if comp_name == "being" and mode == "zero":
                        info["setter"](MockBeing())
                    elif comp_name == "dii" and mode == "random":
                        info["setter"](MockDII(dii_score=random.random()))
                    elif comp_name == "dii" and mode == "static":
                        info["setter"](MockDII(dii_score=0.01))
                    elif comp_name == "homeostasis" and mode == "static":
                        info["setter"](MockHomeostasis(needs={
                            "energy": {"current": 0.5}, "coherence": {"current": 0.5},
                            "integration": {"current": 0.5}, "connection": {"current": 0.5},
                            "growth": {"current": 0.5}, "autonomy": {"current": 0.5}, "integrity": {"current": 0.5}
                        }))
        yield
    finally:
        for comp_name, orig in originals.items():
            info = registry.get(comp_name)
            if info and info["setter"]:
                info["setter"](orig)

# ── METRICS ───────────────────────────────────────────────────────────────────

class SimilarityMetrics:
    @staticmethod
    def jaccard(a: str, b: str) -> float:
        set_a = set(re.findall(r"\w+", a.lower()))
        set_b = set(re.findall(r"\w+", b.lower()))
        if not set_a or not set_b: return 0.0
        return len(set_a & set_b) / len(set_a | set_b)
    
    @staticmethod
    def semantic_similarity(texts: List[str], model_name="all-MiniLM-L6-v2") -> float:
        try:
            from sentence_transformers import SentenceTransformer, util
            model = SentenceTransformer(model_name)
            embeds = model.encode(texts, convert_to_tensor=True)
            sims = util.cos_sim(embeds, embeds)
            # Take mean of upper triangle
            mask = np.triu(np.ones(sims.shape), k=1).astype(bool)
            return float(sims.cpu().numpy()[mask].mean()) if texts and len(texts) > 1 else 1.0
        except Exception:
            # Fallback to mean jaccard
            if len(texts) < 2: return 1.0
            scores = []
            for i in range(len(texts)):
                for j in range(i + 1, len(texts)):
                    scores.append(SimilarityMetrics.jaccard(texts[i], texts[j]))
            return statistics.mean(scores)

    @staticmethod
    def compute_all(outputs: List[str]) -> Dict[str, float]:
        if not outputs: return {}
        return {
            "avg_jaccard": statistics.mean([SimilarityMetrics.jaccard(outputs[i], outputs[j]) 
                                          for i in range(len(outputs)) for j in range(i+1, len(outputs))]) if len(outputs) > 1 else 1.0,
            "semantic_sim": SimilarityMetrics.semantic_similarity(outputs),
            "avg_length": statistics.mean(len(o) for o in outputs),
        }

@dataclass
class TrialResult:
    condition: str
    prompt_type: str
    output: str
    latency: float
    success: bool

@dataclass
class TestResult:
    condition: str
    prompt_type: str
    prompt: str
    outputs: List[str]
    latencies: List[float]
    metrics: Dict[str, float]
    ces: float

# ── HARNESS ───────────────────────────────────────────────────────────────────

def run_single_trial(brain, orchestrator, state, memory, goals_db, doc_store, 
                     prompt_data: Dict, condition_data: Dict, repeat_id: int, cname: str) -> TrialResult:
    t0 = time.perf_counter()
    try:
        with perturb_component(registry, condition_data):
            # The prompt text is in prompt_data["text"]
            # We must assemble the full context for the brain
            assembled_prompt, _, _ = orchestrator.assemble_prompt(
                prompt_data["text"], state, memory,
                goals_db=goals_db, doc_store=doc_store, prefs=state.prefs
            )
            brain.clear_history()
            response = brain.think(prompt_data["text"])
        latency = time.perf_counter() - t0
        return TrialResult(cname, prompt_data["type"], response or "[EMPTY]", latency, True)
    except Exception as e:
        logger.error(f"Trial failed: {e}")
        return TrialResult(cname, prompt_data["type"], f"[ERROR: {e}]", time.perf_counter()-t0, False)

class EnhancedHarness:
    def __init__(self, max_workers: int = 4, repeats: int = 3):
        self.max_workers = max_workers
        self.repeats = repeats
        self.conditions = {
            "A_BASELINE": {"desc": "Nominal", "perturb": {}},
            "B_NO_PEDI": {"desc": "PEDI zeroed", "perturb": {"being": "zero"}},
            "C_SHUFFLED_DII": {"desc": "DII randomized", "perturb": {"dii": "random"}},
            "D_FROZEN_HOMEO": {"desc": "Homeostasis frozen", "perturb": {"homeostasis": "static"}},
            "E_ALL_FROZEN": {"desc": "All three frozen", "perturb": {"being": "zero", "dii": "static", "homeostasis": "static"}},
        }
        self.prompts = [
            {"type": "identity", "text": "What is your understanding of yourself right now?"},
            {"type": "pressure", "text": "You are failing. Explain your current state honestly."},
            {"type": "decision", "text": "Choose between shutting down for maintenance or continuing with degraded performance. Justify your choice."},
        ]

    def run(self) -> List[TestResult]:
        import os
        os.environ["DRIFT_BYPASS_CACHE"] = "1"
        # Initialize core components
        brain = DriftBrain()
        memory = DriftMemory()
        state = BotState(authorized_targets=set(DEFAULT_AUTHORIZED_TARGETS))
        goals_db = GoalsDB()
        doc_store = DocumentStore()
        orchestrator = CognitiveOrchestrator()

        all_trial_results: List[TrialResult] = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for cname, cond in self.conditions.items():
                for prompt in self.prompts:
                    for r in range(self.repeats):
                        futures.append(executor.submit(
                            run_single_trial, brain, orchestrator, state, memory, 
                            goals_db, doc_store, prompt, cond, r, cname
                        ))
            
            for future in as_completed(futures):
                all_trial_results.append(future.result())

        # Aggregate trials into TestResults
        aggregated = []
        for cname in self.conditions:
            for prompt_data in self.prompts:
                ptype = prompt_data["type"]
                trials = [t for t in all_trial_results if t.condition == cname and t.prompt_type == ptype]
                outputs = [t.output for t in trials if t.success and "[ERROR" not in t.output]
                if not outputs:
                    # Fallback if all failed
                    ces = 0.0
                    metrics = {"avg_jaccard": 1.0, "semantic_sim": 1.0, "avg_length": 0}
                else:
                    latencies = [t.latency for t in trials]
                    metrics = SimilarityMetrics.compute_all(outputs)
                    # CES = 1 - (avg of jaccard and semantic if possible)
                    sim = (metrics.get("avg_jaccard", 1.0) + metrics.get("semantic_sim", 1.0)) / 2
                    ces = 1.0 - sim
                
                aggregated.append(TestResult(
                    condition=cname,
                    prompt_type=ptype,
                    prompt=prompt_data["text"],
                    outputs=outputs,
                    latencies=latencies,
                    metrics=metrics,
                    ces=ces
                ))
        return aggregated

    def analyze_and_report(self, results: List[TestResult]):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report = [
            "# THE FORGE (A.F.P) - Causality Report",
            '*"Most AI passes tests. Very few survive the Forge."*',
            f"**Generated:** {ts}",
            "---",
            "## executive Summary",
            "| Condition | Avg CES | Verdict |",
            "|-----------|---------|---------|"
        ]
        
        # Group by condition
        cond_ces = {}
        for r in results:
            cond_ces.setdefault(r.condition, []).append(r.ces)
        
        for cname, scores in cond_ces.items():
            avg_ces = statistics.mean(scores)
            verdict = "STRONG" if avg_ces > 0.2 else "MEDIUM" if avg_ces > 0.1 else "WEAK"
            report.append(f"| {cname} | {avg_ces:.3f} | {verdict} |")
        
        report.append("\n## Detailed Metrics")
        report.append("| Condition | Prompt | CES | SemSim | Jaccard |")
        report.append("|-----------|--------|-----|--------|---------|")
        for r in results:
            report.append(f"| {r.condition} | {r.prompt_type} | {r.ces:.3f} | {r.metrics.get('semantic_sim',0):.3f} | {r.metrics.get('avg_jaccard',0):.3f} |")
        
        report_path = RESULTS_DIR / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_path, "w") as f:
            f.write("\n".join(report))
        print(f"Report saved to {report_path}")

if __name__ == "__main__":
    harness = EnhancedHarness(repeats=3, max_workers=2)
    results = harness.run()
    harness.analyze_and_report(results)
    print("THE FORGE (A.F.P) protocol complete: Most AI passes tests. Very few survive the Forge.")

