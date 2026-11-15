import urllib.request
import json

def test_equation(eq_str):
    print(f"\n==========================================")
    print(f"Testing Equation: {eq_str}")
    data = json.dumps({"equation_latex": eq_str}).encode("utf-8")
    req = urllib.request.Request(
        "http://127.0.0.1:8000/api/v1/solve",
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            print(f"Status: SUCCESS | Time: {res['computation_time_ms']} ms | Source: {res.get('engine_source')}")
            print(f"Final Answer: {res['final_answer']}")
            print(f"Total Steps: {res['total_steps']}")
            for s in res['steps']:
                print(f"  • Step {s['step_num']}: [{s['rule_name_ar']}] {s['latex']}")
                print(f"    الشرح: {s['explanation_ar']}")
    except Exception as exc:
        print(f"Error: {exc}")

if __name__ == "__main__":
    test_equation("6/8")
    test_equation("100 - 25 * 3 + 14")
    test_equation("8 * 9 / 7 + 5")
    test_equation("5x - 20 = 0")
    test_equation("x^2 - 7x + 12 = 0")
