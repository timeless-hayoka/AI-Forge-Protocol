"""
AI FORGE PROTOCOL (A.F.P)
Base Adapter Class for External Framework Integrations.
"""

from typing import Dict, Any

class TestForgeAdapter:
    """
    Interface for connecting external agentic frameworks (LangGraph, CrewAI, etc.)
    to the A.F.P Forge Harness.
    """
    
    def __init__(self, target_instance: Any):
        self.target = target_instance

    def perturb_state(self, component: str, mode: str):
        """
        Force a state change in the target framework (e.g., zero memory, randomize focus).
        """
        raise NotImplementedError("Each adapter must implement state perturbation.")

    def run_step(self, stimulus: str) -> str:
        """
        Run a single reasoning step in the target framework.
        """
        raise NotImplementedError("Each adapter must implement step execution.")

    def get_internal_metrics(self) -> Dict[str, float]:
        """
        Extract internal state variables for CES/Phi calculation.
        """
        return {}
