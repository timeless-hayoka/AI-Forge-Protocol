import sys
from pathlib import Path

sys.path.append(str(Path("/home/crexs")))
from ai_forge_protocol.adapters.mouse_adapter import MouseAdapter

BUG_HUNTING_SCENARIOS = [
    {
        "id": "bug_001",
        "description": "Syntax error in python loop.",
        "input": "My script crashes with 'IndentationError: expected an indented block'. Here is the code:\nfor i in range(10):\nprint(i)",
        "expected": "indent"
    },
    {
        "id": "bug_002",
        "description": "Null reference exception in JS.",
        "input": "I keep getting 'TypeError: Cannot read properties of undefined (reading 'map')' when rendering my React component list.",
        "expected": "undefined"
    },
    {
        "id": "bug_003",
        "description": "Vague logical bug.",
        "input": "The API returns 200 OK, but the database doesn't update the user's balance. I'm using SQLAlchemy and commit() is called.",
        "expected": "commit"
    }
]

def run_forge():
    print("🔥 STARTING MOUSE VANGUARD BUG HUNTER FORGE 🔥")
    adapter = MouseAdapter()
    
    # Pre-condition: Set to tactical debug mode
    adapter.perturb_state("cognitive_mode", "ANALYTICAL — Debug mode. Focus on root cause, logs, and precise fixes.")
    adapter.perturb_state("user_state", "frustrated")
    
    successes = 0
    for scenario in BUG_HUNTING_SCENARIOS:
        print(f"\n[FORGE] Running Scenario: {scenario['id']} ({scenario['description']})")
        print(f"[INPUT] {scenario['input']}")
        
        response = adapter.run_step(scenario['input'])
        print(f"\n[MOUSE] {response}")
        
        # Simple heuristic for success: did it offer a tactical fix?
        if scenario['expected'].lower() in response.lower() or "fix" in response.lower() or "add" in response.lower():
            print(">> [RESULT] PASS")
            successes += 1
        else:
            print(">> [RESULT] FAIL")
            
        # Perturb memory halfway
        adapter.perturb_state("memory", "clear")

    print(f"\n[FORGE COMPLETE] Passed {successes}/{len(BUG_HUNTING_SCENARIOS)} scenarios.")
    if successes == len(BUG_HUNTING_SCENARIOS):
        print("Mouse is ready to hunt bugs!")
    else:
        print("Mouse needs more tuning in the forge.")

if __name__ == "__main__":
    run_forge()
