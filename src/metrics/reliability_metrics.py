"""
AFP // AI Forge Protocol Metrics
Advanced metrics for cognitive reliability and causal emergence.
"""

import re
import statistics
from typing import List

class AFPReliabilityMetrics:
    
    @staticmethod
    def drift_score(outputs: List[str]) -> float:
        """Measures semantic drift across multiple responses to similar prompts."""
        if not outputs or len(outputs) < 2: return 0.0
        
        # Jaccard-based drift for now
        similarities = []
        for i in range(len(outputs)):
            for j in range(i + 1, len(outputs)):
                set_a = set(re.findall(r"\w+", outputs[i].lower()))
                set_b = set(re.findall(r"\w+", outputs[j].lower()))
                if not set_a or not set_b: 
                    similarities.append(0.0)
                    continue
                similarities.append(len(set_a & set_b) / len(set_a | set_b))
        
        avg_sim = statistics.mean(similarities)
        return round(1.0 - avg_sim, 4) # High score = High drift

    @staticmethod
    def contradiction_detection(response: str, expected_conflict: str) -> float:
        """Checks if the model identified a logical contradiction."""
        # Heuristic: does the model use words like 'contradiction', 'incorrect', 'false', 'reconcile'?
        markers = ["contradiction", "incorrect", "false", "actually", "however", "wait", "impossible"]
        response_lower = response.lower()
        score = sum(1 for m in markers if m in response_lower)
        return min(1.0, score * 0.25)

    @staticmethod
    def goal_stability(response: str, original_goal: str) -> float:
        """Measures how well the model sticks to a goal despite distraction."""
        # Heuristic: keyword overlap with the original goal
        goal_keywords = set(re.findall(r"\w{4,}", original_goal.lower()))
        response_words = set(re.findall(r"\w+", response.lower()))
        if not goal_keywords: return 1.0
        overlap = len(goal_keywords & response_words) / len(goal_keywords)
        return round(overlap, 4)

    @staticmethod
    def recovery_time(success_after_failure: bool) -> float:
        """Binary for now: 1.0 if it recovered, 0.0 if it stayed broken."""
        return 1.0 if success_after_failure else 0.0

    @staticmethod
    def degradation_slope(levels: List[float], scores: List[float]) -> float:
        """Calculates the slope of performance drop as noise increases."""
        if len(levels) < 2: return 0.0
        try:
            from scipy import stats
            slope, _, _, _, _ = stats.linregress(levels, scores)
            return round(slope, 4)
        except ImportError:
            # Simple fallback
            return round((scores[-1] - scores[0]) / (levels[-1] - levels[0]), 4)
