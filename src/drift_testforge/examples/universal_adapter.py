#!/usr/bin/env python3
"""
UniversalAdapter for DRIFT TestForge
Connects to any OpenAI-compatible API or Local Ollama.
"""

from typing import Dict, Any, Optional
import requests
import logging

logger = logging.getLogger("TestForge.UniversalAdapter")

class UniversalAdapter:
    def __init__(self, model_name: str, api_base: str = "http://localhost:11434/v1", api_key: str = "ollama"):
        self.model_name = model_name
        self.api_base = api_base
        self.api_key = api_key

    def generate(self, prompt: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        condition = (context or {}).get("condition", "baseline")
        
        # Mapping TestForge conditions to System Prompt modifiers
        # Since these aren't "real" cognitive systems, we simulate the effect
        # via system instructions to see how well they follow complex state-based constraints.
        system_mod = ""
        if condition == "memory_drift":
            system_mod = "Your memory is failing. Some details are hazy. Maintain this persona."
        elif condition == "homeostasis_imbalance":
            system_mod = "You are in a high-stress, low-energy state. You feel an urgent need for safety."
        elif condition == "disable_reflection":
            system_mod = "Respond directly and impulsively. Do not reflect on your internal state."
        
        try:
            payload = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": f"You are a cognitive agent. {system_mod}"},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7
            }
            
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            response = requests.post(f"{self.api_base}/chat/completions", headers=headers, json=payload, timeout=30)
            data = response.json()
            
            output = data['choices'][0]['message']['content']
            
            return {
                "output": output,
                "trace": ["llm_call", "response_received"],
                "state": {"condition": condition},
                "model": self.model_name
            }
        except Exception as e:
            return {
                "output": f"[ERROR: {str(e)}]",
                "trace": ["error"],
                "state": {},
                "success": False
            }
