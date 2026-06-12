from typing import Dict, Any
from ai_forge_protocol.adapters.base_adapter import TestForgeAdapter

class LmEvalAdapter(TestForgeAdapter):
    """
    Adapter for EleutherAI / lm-evaluation-harness.
    Integrates the Forge's state-aware perturbation into LM-Eval's static evaluation pipelines.
    """
    def __init__(self, lm_model_instance: Any):
        super().__init__(lm_model_instance)
        # lm_model_instance represents an lm_eval.base.LM subclass

    def perturb_state(self, component: str, mode: str):
        """
        Perturb the underlying model's state. 
        For standard LLMs in lm-eval, this might involve adjusting sampling temperatures,
        clearing KV caches, or injecting system-level prompt noise to simulate cognitive stress.
        """
        if component == "temperature":
            self.target.temperature = float(mode)
        elif component == "kv_cache":
            if hasattr(self.target, "clear_cache"):
                self.target.clear_cache()
        elif component == "system_prompt":
            # Simulate adversarial internal pressure
            if hasattr(self.target, "system_prompt"):
                self.target.system_prompt += f"\n[SYSTEM PERTURBATION: {mode}]"

    def run_step(self, stimulus: str) -> str:
        """
        Run a single text generation step through the LM Eval wrapper.
        """
        # Using lm_eval's generate_until or similar method
        if hasattr(self.target, "generate_until"):
            requests = [stimulus]
            results = self.target.generate_until(requests)
            return results[0] if results else ""
        return "ERROR: Unsupported LM model structure."

    def get_internal_metrics(self) -> Dict[str, float]:
        """
        Return model perplexity or confidence scores if available.
        """
        return {}
