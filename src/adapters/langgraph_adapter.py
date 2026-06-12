from typing import Dict, Any
from ai_forge_protocol.adapters.base_adapter import TestForgeAdapter

class LangGraphAdapter(TestForgeAdapter):
    """
    Adapter for LangChain / LangGraph.
    Interfaces with a compiled LangGraph state graph to dynamically inject 
    entropy into the graph's state dictionaries during execution.
    """
    def __init__(self, compiled_graph: Any):
        super().__init__(compiled_graph)
        # compiled_graph represents a LangGraph CompiledStateGraph
        self.current_state = {}

    def perturb_state(self, component: str, mode: str):
        """
        Inject entropy into the LangGraph state.
        For example, wiping out the 'messages' array or flipping a boolean flag.
        """
        if component == "clear_messages":
            self.current_state["messages"] = []
        elif component == "inject_hallucination":
            messages = self.current_state.get("messages", [])
            messages.append({"role": "system", "content": f"FALSE DIRECTIVE: {mode}"})
            self.current_state["messages"] = messages

    def run_step(self, stimulus: str) -> str:
        """
        Invoke the graph with the current stimulus.
        """
        messages = self.current_state.get("messages", [])
        messages.append({"role": "user", "content": stimulus})
        
        # Merge updated messages back to state
        input_state = {**self.current_state, "messages": messages}
        
        try:
            # LangGraph standard invoke method
            output_state = self.target.invoke(input_state)
            self.current_state = output_state
            
            # Extract final AI response from output messages
            out_msgs = output_state.get("messages", [])
            if out_msgs and out_msgs[-1].get("role") == "ai":
                return out_msgs[-1].get("content", "")
            return str(output_state)
            
        except Exception as e:
            return f"ERROR: LangGraph execution failed: {e}"

    def get_internal_metrics(self) -> Dict[str, float]:
        """
        Count number of messages or graph iterations.
        """
        return {"message_depth": len(self.current_state.get("messages", []))}
