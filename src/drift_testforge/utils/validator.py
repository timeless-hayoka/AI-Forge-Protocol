#!/usr/bin/env python3
"""
TestForge Validator - Fail-fast verification layer for adapters and data flows.
Ensures every component meets the universal contract before expensive computation.
"""

import logging
from typing import Any, Dict

logger = logging.getLogger("TestForge-Validator")

class Validator:
    @staticmethod
    def verify_adapter(adapter: Any) -> bool:
        """Check that adapter implements the required TestForgeAdapter interface."""
        if not hasattr(adapter, "generate"):
            raise AttributeError("CRITICAL: Adapter must implement .generate(prompt: str, context: dict = None) -> dict")
        if not callable(getattr(adapter, "generate")):
            raise TypeError("CRITICAL: adapter.generate must be callable")
        logger.info("[Validator] ✅ Adapter interface verified successfully.")
        return True

    @staticmethod
    def verify_data_format(result: Dict[str, Any]) -> bool:
        """Ensure the output from generate() is usable by metrics pipeline."""
        if not isinstance(result, dict):
            raise ValueError("CRITICAL: Adapter.generate() must return a dict, not " + str(type(result)))
        if "output" not in result:
            raise ValueError("CRITICAL: Result dict must contain key 'output' (the generated text).")
        if not isinstance(result.get("output"), str):
            raise ValueError("CRITICAL: result['output'] must be a string.")
        logger.info("[Validator] ✅ Data format verified. Ready for metrics.")
        return True

    @staticmethod
    def verify_outputs_for_metrics(outputs: list) -> bool:
        if not outputs or len(outputs) < 2:
            logger.warning("[Validator] Only %d outputs provided. Semantic entropy and consistency will be limited.", len(outputs))
        return True