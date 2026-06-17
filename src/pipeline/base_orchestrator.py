import traceback
from typing import List, Dict, Callable


def run_steps(steps: List[Dict]) -> None:
    """
    Standard step runner shared by all pipeline orchestrators.
    Each step: {"name": str, "func": Callable}
    Raises RuntimeError on first failure.
    """
    for idx, step in enumerate(steps, 1):
        print(f"\n--- STEP {idx}/{len(steps)}: {step['name']} ---")
        try:
            step["func"]()
            print(f"[OK] {step['name']}")
        except Exception as e:
            print(f"\n[FAIL] Step failed: {e}")
            traceback.print_exc()
            raise RuntimeError(f"Pipeline failed at step: {step['name']}") from e
