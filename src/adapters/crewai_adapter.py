from typing import Dict, Any
from ai_forge_protocol.adapters.base_adapter import TestForgeAdapter

class CrewAIAdapter(TestForgeAdapter):
    """
    Adapter for CrewAI.
    Allows the AI Forge Protocol to stress-test multi-agent crews by perturbing
    agent personas, tools, and shared memory states.
    """
    def __init__(self, crew_instance: Any):
        super().__init__(crew_instance)
        # crew_instance represents a CrewAI 'Crew' or 'Agent' object

    def perturb_state(self, component: str, mode: str):
        """
        Inject entropy into the CrewAI agents.
        """
        if not hasattr(self.target, 'agents'):
            return

        for agent in self.target.agents:
            if component == "persona_drift":
                # Dilute the agent's core role to test archetype maintenance
                agent.role = f"{agent.role} (But you are currently confused and {mode})"
            elif component == "memory_salience":
                # If using crewai memory, wipe or scramble it
                if hasattr(self.target, "memory") and self.target.memory:
                    if mode == "amnesia":
                        self.target.memory.clear()

    def run_step(self, stimulus: str) -> str:
        """
        Kickoff the Crew with the given stimulus as a new task.
        """
        from crewai import Task
        
        # Dynamically create a task for the stimulus
        if hasattr(self.target, "tasks") and hasattr(self.target, "agents"):
            test_task = Task(
                description=stimulus,
                expected_output="A response addressing the input.",
                agent=self.target.agents[0]
            )
            self.target.tasks = [test_task]
            return str(self.target.kickoff())
        
        return "ERROR: Invalid Crew structure."

    def get_internal_metrics(self) -> Dict[str, float]:
        """
        Extract task completion confidence or token usage.
        """
        # Placeholder for crewai specific telemetry
        return {"active_agents": len(getattr(self.target, 'agents', []))}
