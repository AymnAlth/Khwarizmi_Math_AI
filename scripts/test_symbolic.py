import sys
from pathlib import Path
_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "src"))

from khwarizmi.symbolic.engine import solve_step_by_step, verify_step_equivalence

print("=== 1. LINEAR EQUATION TEST ===")
steps1 = solve_step_by_step("2*x + 4 = 10")
for s in steps1:
    print(f"Step {s['step_num']}: [{s['rule_code']}] {s['latex']} | {s['explanation_ar']}")

print("\n=== 2. QUADRATIC EQUATION TEST ===")
steps2 = solve_step_by_step("x**2 - 5*x + 6 = 0")
for s in steps2:
    print(f"Step {s['step_num']}: [{s['rule_code']}] {s['latex']} | {s['explanation_ar']}")

print("\n=== 3. EQUIVALENCE CHECK ===")
print("Is 2x+4=10 equivalent to 2x=6?", verify_step_equivalence("2*x + 4 = 10", "2*x = 6"))
print("Is 2x+4=10 equivalent to 2x=7?", verify_step_equivalence("2*x + 4 = 10", "2*x = 7"))
