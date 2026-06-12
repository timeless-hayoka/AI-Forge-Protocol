from typing import Dict
import sys
from pathlib import Path

sys.path.append(str(Path("/home/crexs")))
from ai_forge_protocol.adapters.base_adapter import TestForgeAdapter
from infj_bot.automation.mouse.v2 import SymbioticAI, MemoryStore, PortableConfig, MOUSE_HOME, CONFIG_PATH

class MouseAdapter(TestForgeAdapter):
    def __init__(self):
        self.config = PortableConfig(CONFIG_PATH)
        self.config.set("model_name", "qwen3:4b")
        self.memory = MemoryStore(MOUSE_HOME / "memories")
        self.target = SymbioticAI(self.memory, self.config)

    def perturb_state(self, component: str, mode: str):
        """Force a state change in Mouse."""
        if component == "cognitive_mode":
            self.target.world.cognitive_mode = mode
        elif component == "memory":
            if mode == "clear":
                self.target.memory.items = []
        elif component == "user_state":
            self.target.world.inferred_user_state = mode

    def run_step(self, stimulus: str) -> str:
        """Run a single reasoning step in Mouse."""
        return self.target.chat(stimulus)

    def get_internal_metrics(self) -> Dict[str, float]:
        """Extract internal state variables."""
        return {
            "memory_items": len(self.target.memory.items),
        }
