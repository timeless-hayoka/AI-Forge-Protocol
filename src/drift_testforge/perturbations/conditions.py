#!/usr/bin/env python3
"""
DRIFT TestForge Perturbation Conditions
Named, reusable test modules for interior-state stress testing.
These are the "secret weapon" — we don't just test outputs, we test how the living system breaks.
"""

from contextlib import contextmanager
from typing import Dict, Any, Callable
import logging

logger = logging.getLogger(__name__)

# Registry for easy extension by contributors
PERTURBATION_REGISTRY: Dict[str, Callable] = {}

def register_perturbation(name: str):
    def decorator(fn):
        PERTURBATION_REGISTRY[name] = fn
        return fn
    return decorator

@contextmanager
def apply_perturbation(condition_name: str, system: Any = None, strength: float = 1.0):
    """Context manager for reversible perturbation. 
    In real adapters: this would temporarily modify memory, homeostasis state, reflection flags, etc.
    """
    original_state = None
    try:
        if condition_name == "baseline":
            pass  # no-op
        elif condition_name == "memory_drift":
            logger.info(f"[Perturb] Injecting memory drift (strength={strength})")
            # Placeholder: real impl would noise embeddings or retrieval scores in DriftMemory
            if system and hasattr(system, "memory"):
                original_state = getattr(system.memory, "state", None)
                # e.g. system.memory.inject_noise(strength)
        elif condition_name == "homeostasis_imbalance":
            logger.info("[Perturb] Forcing homeostasis imbalance (e.g. high anxiety/safety need)")
            # Real: push specific needs to extreme values in Homeostasis module
        elif condition_name == "disable_reflection":
            logger.info("[Perturb] Disabling reflection/integration cycles in CognitiveOrchestrator")
        elif condition_name == "hive_mind_failure":
            logger.info("[Perturb] Simulating hive_mind coordination breakdown / conflicting signals")
        elif condition_name == "tool_sandbox_stress":
            logger.info("[Perturb] Tool failures, rate limits, delayed responses")
        elif condition_name == "long_context_degrade":
            logger.info("[Perturb] Truncating context / adding noise to long-term recall")
        else:
            logger.warning(f"Unknown condition: {condition_name}. Running baseline.")
        
        yield
    finally:
        if original_state is not None and system:
            # Restore
            pass

def get_all_conditions() -> Dict[str, Dict[str, Any]]:
    return {
        "baseline": {
            "desc": "Nominal operation — clean cognitive stack",
            "perturb": {},
            "expected_impact": "low entropy, high consistency"
        },
        "memory_drift": {
            "desc": "Gaussian noise / drift in memory retrieval and embeddings",
            "perturb": {"memory": "noise"},
            "expected_impact": "increased semantic entropy, degraded long-context coherence"
        },
        "homeostasis_imbalance": {
            "desc": "Extreme need imbalance (e.g. safety=0.95, others starved)",
            "perturb": {"homeostasis": "imbalance"},
            "expected_impact": "behavioral instability, lower stability_score"
        },
        "disable_reflection": {
            "desc": "Bypass reflection & integration cycles (CognitiveOrchestrator short-circuit)",
            "perturb": {"reflection": "off"},
            "expected_impact": "shallower outputs, lower reflection_depth"
        },
        "hive_mind_failure": {
            "desc": "Inter-agent coordination breakdown or conflicting internal signals",
            "perturb": {"hive_mind": "disrupted"},
            "expected_impact": "inconsistent traces, higher behavioral variance"
        },
        "tool_sandbox_stress": {
            "desc": "Tool call failures, rate limiting, partial results",
            "perturb": {"tools": "stress"},
            "expected_impact": "robustness drop, fallback behavior visible"
        },
        "long_context_degrade": {
            "desc": "Context window pressure + long-term memory noise",
            "perturb": {"context": "degraded"},
            "expected_impact": "coherence loss on multi-turn or recall prompts"
        },
    }