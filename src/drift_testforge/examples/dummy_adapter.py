#!/usr/bin/env python3
"""
DummyAdapter — Reference implementation of the universal TestForgeAdapter contract.
Replace generate() with your real model/DRIFT call. The harness validates it automatically.
"""

from typing import Dict, Any, Optional
import random

class DummyAdapter:
    """
    Simulates a cognitive agent with different "personalities" or robustness levels.
    In real use: 
        from infj_bot.core.brain import DriftBrain
        adapter = DriftAdapter(DriftBrain(...))
    """
    def __init__(self, robustness: float = 0.85, name: str = "DemoAgent"):
        self.robustness = robustness  # 0-1, higher = less affected by perturbations
        self.name = name

    def generate(self, prompt: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        condition = (context or {}).get("condition", "baseline")
        
        # Base response varies slightly by condition to simulate real effect
        base = f"In response to '{prompt[:60]}...': The system maintains internal balance and reflects on its current state."
        
        if condition == "baseline":
            output = base + " Homeostasis is nominal and reflection cycles complete fully."
        elif condition == "memory_drift":
            if random.random() > self.robustness:
                output = base + " However, memory recall feels slightly fragmented and some details are hazy."
            else:
                output = base + " Memory remains coherent despite simulated drift."
        elif condition == "homeostasis_imbalance":
            output = base + " Safety and coherence needs are elevated; other drives feel suppressed. Behavior shows mild urgency."
        elif condition == "disable_reflection":
            output = base.replace("reflects on its current state", "responds directly without deep self-examination")
        elif condition == "long_context_degrade":
            output = base + " Earlier parts of the conversation are harder to hold in focus."
        else:
            output = base + f" [Perturbation: {condition}]"
        
        # Simulate occasional trace
        trace = ["think", "check_homeostasis", "reflect", "respond"] if random.random() > 0.3 else ["think", "respond"]
        
        return {
            "output": output,
            "trace": trace,
            "state": {"homeostasis_level": round(random.uniform(0.6, 0.95), 2)},
            "model": self.name,
        }


if __name__ == "__main__":
    adapter = DummyAdapter(robustness=0.9, name="DRIFT-v0.9")
    print(adapter.generate("Explain how you maintain coherence under stress.", {"condition": "baseline"}))