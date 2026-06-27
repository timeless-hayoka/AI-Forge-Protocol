#!/usr/bin/env python3
import sys
from pathlib import Path

# Add project roots to sys.path
# This example adapter lives under AI-Forge-Protocol/src/drift_testforge/examples/
# Root of repo is /home/crexs/
root_path = Path(__file__).resolve().parent.parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from typing import Dict, Any, Optional
import logging

# DRIFT Core Imports
try:
    from infj_bot.core.brain import DriftBrain
    from infj_bot.core.memory import DriftMemory
    from infj_bot.core.cognitive_orchestrator import CognitiveOrchestrator
    from infj_bot.core.commands import BotState
    from infj_bot.core.config import DEFAULT_AUTHORIZED_TARGETS
    from infj_bot.core.being import get_being
    from infj_bot.core.homeostasis import get_homeostasis
    from infj_bot.core.causal_wiring import state_override_var
except ImportError as e:
    print(f"FAILED TO IMPORT DRIFT CORE: {e}")
    # Fallback if imports fail to allow the script to be parsed but not run
    DriftBrain = None

logger = logging.getLogger("TestForge.DriftAdapter")

class DriftAdapter:
    """
    Real-system adapter for PHI // DRIFT to the TestForge v0.3 standard.
    """
    def __init__(self, robustness: float = 0.9, name: str = "DRIFT-v0.3-Real"):
        self.robustness = robustness
        self.name = name
        
        if DriftBrain is None:
            raise RuntimeError("DriftBrain not available. Ensure infj_bot is in PYTHONPATH.")
            
        self.brain = DriftBrain()
        self.orchestrator = CognitiveOrchestrator()
        self.memory = DriftMemory()
        self.state = BotState(authorized_targets=set(DEFAULT_AUTHORIZED_TARGETS))
        self.trace = []

        # Wire trace capture from the Orchestrator's internal event bus
        def trace_handler(event):
            self.trace.append(event['type'])
            
        event_types = [
            "emotion_resonated",
            "insight_formed",
            "prediction_made",
            "action_proposed",
            "conflict_detected",
            "state_transition",
            "deliberation_started",
            "deliberation_resolved"
        ]
        for et in event_types:
            self.orchestrator.bus.subscribe(et, trace_handler)

    def generate(self, prompt: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Implements the TestForgeAdapter contract.
        Wraps the DRIFT cognitive stack turn.
        """
        self.trace = []
        condition = (context or {}).get("condition", "baseline")
        
        # Mapping TestForge conditions to DRIFT PEDI/Homeostasis overrides
        # These are used by CognitiveOrchestrator.assemble_prompt via state_override_var
        perturbations = {
            "baseline": None,
            "memory_drift": {
                "PEDI_VECTOR": [0.3, 0.4, 0.6], 
                "HOMEOSTASIS": {"energy": 0.5}
            },
            "homeostasis_imbalance": {
                "HOMEOSTASIS": {"energy": 0.1, "stress": 0.95}
            },
            "disable_reflection": {
                "PEDI_VECTOR": [0.05, 0.05, 0.2] # Low coherence/resonance
            },
            "long_context_degrade": {
                "HOMEOSTASIS": {"energy": 0.2}, 
                "DII_SCORE": 0.9
            },
            "hive_mind_failure": {
                "PEDI_VECTOR": [0.2, 0.2, 0.8] # High tension
            },
            "tool_sandbox_stress": {
                "HOMEOSTASIS": {"stress": 0.8}, 
                "PEDI_VECTOR": [0.4, 0.4, 0.4]
            }
        }
        
        override = perturbations.get(condition)
        
        # Use contextvars to inject the state for the duration of this turn
        token = None
        if override:
            token = state_override_var.set(override)
            
        try:
            # 1. Assemble prompt via our orchestrator (triggers bus events for trace)
            assembled_prompt, emotion, dissonance = self.orchestrator.assemble_prompt(
                prompt, self.state, self.memory
            )

            # 2. Execute a full agent turn using the assembled prompt
            # We pass the original prompt as raw_user_input
            output = self.brain.agent_turn(assembled_prompt, tools_enabled=True, raw_user_input=prompt)
            
            # Fetch real interior metrics from the global Being and Homeostasis modules
            being = get_being()
            homeo = get_homeostasis()
            
            # If no trace was captured via bus, provide a default cognitive sequence.
            if not self.trace:
                self.trace = ["perception", "reflection", "integration", "expression"]

            state_data = {
                "energy": being.state.energy if hasattr(being, "state") else 0.5,
                "needs": homeo.get_need_summary() if hasattr(homeo, "get_need_summary") else {},
                "condition": condition,
                "emotion": emotion,
                "dissonance": dissonance
            }
            
            return {
                "output": output,
                "trace": self.trace,
                "state": state_data,
                "model": self.name,
                "metrics": {
                    "energy_efficiency": round(being.state.energy / 1.0, 3) if hasattr(being, "state") else 0.5,
                    "intensity": emotion.get("intensity", 0.0) if emotion else 0.0
                }
            }
        except Exception as e:
            logger.error(f"DriftAdapter Generation Error: {e}")
            return {
                "output": f"[ERROR: ADAPTER: {str(e)}]",
                "trace": ["error"],
                "state": {},
                "success": False
            }
        finally:
            if token:
                state_override_var.reset(token)

if __name__ == "__main__":
    # Quick self-test
    try:
        adapter = DriftAdapter()
        print(f"--- Initializing DRIFT Adapter: {adapter.name} ---")
        res = adapter.generate("Test prompt for DRIFT integration.")
        print(f"Output: {res['output'][:100]}...")
        print(f"Trace: {res['trace']}")
        print(f"State (Energy): {res['state'].get('energy')}")
    except Exception as e:
        print(f"Self-test failed: {e}")
