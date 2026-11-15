from __future__ import annotations
import json
import re
from typing import List, Dict, Any, Tuple
from pathlib import Path
from ..symbolic.engine import verify_step_equivalence
from ..vision.syntax_guard import is_valid_latex_syntax
from ..reasoning.prompt_schema import parse_structured_output

class SFTAcceptanceGateEvaluator:
    """Evaluates fine-tuned reasoning model against Phase 3 Acceptance Criteria:

    1. Structured Schema Compliance Rate >= 99%
    2. Step-by-Step Mathematical Correctness >= 85%
    3. Pedagogical Explanation Presence & Quality
    """

    def __init__(self):
        pass

    def evaluate_response(self, initial_equation: str, output_text: str) -> Dict[str, Any]:
        """Evaluates a single model output."""
        # 1. Structural Schema Check
        has_step_tags = bool(re.search(r'<step>.*?</step>', output_text, re.DOTALL))
        steps = parse_structured_output(output_text)
        
        schema_compliant = False
        if has_step_tags and len(steps) > 0:
            all_fields_present = all(
                s.get("rule_code") and s.get("latex") and s.get("explanation_ar")
                for s in steps
            )
            schema_compliant = all_fields_present

        # 2. Mathematical Step-by-step Correctness
        math_correct = True
        step_evaluations = []
        prev_eq = initial_equation

        for s in steps:
            curr_latex = s.get("latex", "")
            syntax_ok = is_valid_latex_syntax(curr_latex)
            math_equiv = False

            if syntax_ok:
                math_equiv = verify_step_equivalence(prev_eq, curr_latex)
                if math_equiv:
                    prev_eq = curr_latex

            if not (syntax_ok and math_equiv):
                math_correct = False

            step_evaluations.append({
                "step_num": s["step_num"],
                "syntax_valid": syntax_ok,
                "mathematically_equivalent": math_equiv
            })

        return {
            "schema_compliant": schema_compliant,
            "math_correct": math_correct,
            "total_steps": len(steps),
            "step_evaluations": step_evaluations
        }

    def evaluate_test_set(self, test_records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluates batch of predictions."""
        total = len(test_records)
        if total == 0:
            return {"total": 0, "schema_rate": 0.0, "math_acc": 0.0, "passed": False}

        schema_passes = 0
        math_passes = 0

        for r in test_records:
            eq = r["equation"]
            pred_text = r["predicted_text"]
            res = self.evaluate_response(eq, pred_text)
            if res["schema_compliant"]:
                schema_passes += 1
            if res["math_correct"]:
                math_passes += 1

        schema_rate = (schema_passes / total) * 100
        math_acc = (math_passes / total) * 100
        passed_gate = (schema_rate >= 99.0) and (math_acc >= 85.0)

        return {
            "total_evaluated": total,
            "schema_compliance_rate": round(schema_rate, 2),
            "mathematical_accuracy": round(math_acc, 2),
            "gate_criteria": {
                "schema_threshold": 99.0,
                "math_threshold": 85.0
            },
            "passed_acceptance_gate": passed_gate
        }
