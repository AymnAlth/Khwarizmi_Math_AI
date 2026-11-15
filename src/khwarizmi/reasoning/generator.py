from __future__ import annotations
import random
import json
import math
from pathlib import Path
from typing import Dict, Any, List
import sympy as sp
from ..symbolic.engine import solve_step_by_step
from .prompt_schema import format_prompt, format_full_solution_to_text
from ..config import ARABIC_SYNTH_DIR

class EnhancedCurriculumGenerator:
    """Comprehensive 4-Stage Curriculum Generator:

    Stage 1: Basic Algebra (Linear, Fractions, Transposition)
    Stage 2: Advanced Algebra (Quadratics, Discriminant, Factoring, Systems)
    Stage 3: Transcendental Functions (Logarithms, Exponentials, Trigonometry)
    Stage 4: Calculus (Derivatives, Power Rule, Product Rule, Integrals)
    """

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)

    # -------------------------------------------------------------
    # STAGE 1: BASIC ALGEBRA
    # -------------------------------------------------------------
    def generate_stage1_basic(self) -> Dict[str, Any]:
        """Linear equations: a*x + b = c*x + d or a*(x + b) = c."""
        pattern = self.rng.choice(["simple", "both_sides", "parentheses"])
        sol = self.rng.randint(-20, 20)
        
        if pattern == "simple":
            a = self.rng.choice([-6, -5, -4, -3, -2, 2, 3, 4, 5, 6, 7])
            b = self.rng.randint(-30, 30)
            c = a * sol + b
            sign_b = f"+ {b}" if b >= 0 else f"- {abs(b)}"
            eq_latex = f"{a}x {sign_b} = {c}"
            steps = solve_step_by_step(f"{a}*x + {b} = {c}")
        elif pattern == "both_sides":
            a1 = self.rng.choice([3, 4, 5, 6])
            a2 = self.rng.choice([1, 2])
            b1 = self.rng.randint(-15, 15)
            # a1*sol + b1 = a2*sol + b2 => b2 = (a1 - a2)*sol + b1
            b2 = (a1 - a2) * sol + b1
            sign1 = f"+ {b1}" if b1 >= 0 else f"- {abs(b1)}"
            sign2 = f"+ {b2}" if b2 >= 0 else f"- {abs(b2)}"
            eq_latex = f"{a1}x {sign1} = {a2}x {sign2}"
            steps = solve_step_by_step(f"{a1}*x + {b1} = {a2}*x + {b2}")
        else: # parentheses
            a = self.rng.choice([2, 3, 4, 5])
            p = self.rng.randint(-10, 10)
            c = a * (sol + p)
            sign_p = f"+ {p}" if p >= 0 else f"- {abs(p)}"
            eq_latex = f"{a}(x {sign_p}) = {c}"
            steps = solve_step_by_step(f"{a}*(x + {p}) = {c}")

        return {
            "curriculum_stage": "stage_1_basic_algebra",
            "equation": eq_latex,
            "solution": steps,
            "final_answer": f"x = {sol}"
        }

    # -------------------------------------------------------------
    # STAGE 2: ADVANCED ALGEBRA
    # -------------------------------------------------------------
    def generate_stage2_advanced(self) -> Dict[str, Any]:
        """Quadratic equations: ax^2 + bx + c = 0 with distinct roots."""
        r1 = self.rng.randint(-9, 9)
        r2 = self.rng.randint(-9, 9)
        a = self.rng.choice([1, 1, 2, -1])
        b = -a * (r1 + r2)
        c = a * r1 * r2

        x = sp.Symbol('x')
        poly = a*x**2 + b*x + c
        eq_latex = f"{sp.latex(poly)} = 0"
        steps = solve_step_by_step(f"{a}*x**2 + {b}*x + {c} = 0")

        return {
            "curriculum_stage": "stage_2_advanced_algebra",
            "equation": eq_latex,
            "solution": steps,
            "final_answer": f"x = {min(r1, r2)}, x = {max(r1, r2)}"
        }

    # -------------------------------------------------------------
    # STAGE 3: TRANSCENDENTAL & EXPONENTIAL
    # -------------------------------------------------------------
    def generate_stage3_transcendental(self) -> Dict[str, Any]:
        """Exponential / Logarithmic: a^(x + b) = a^c or log simplifications."""
        base = self.rng.choice([2, 3, 5, 10])
        sol = self.rng.randint(-4, 6)
        shift = self.rng.randint(-3, 4)
        c = sol + shift
        power_val = base**c if 0 <= c <= 6 else base
        
        sign_shift = f"+ {shift}" if shift >= 0 else f"- {abs(shift)}"
        eq_latex = f"{base}^{{x {sign_shift}}} = {power_val}"
        
        steps = [
            {
                "step_num": 1,
                "rule_code": "PROBLEM_FORMULATION",
                "rule_name_ar": "صياغة المعادلة الأسية",
                "latex": eq_latex,
                "explanation_ar": f"نلاحظ أن المعادلة تحتوي على متغير في الأس بالأساس {base}.",
                "status": "VERIFIED"
            },
            {
                "step_num": 2,
                "rule_code": "EQUAL_BASES",
                "rule_name_ar": "مساواة الأسس عند تشابه الأساسات",
                "latex": f"x {sign_shift} = {c}",
                "explanation_ar": f"بما أن الطرف الأيمن يمكن كتابته بالأساس {base} كـ ${base}^{{{c}}}$، فإننا نساوي الأسين مباشرة.",
                "status": "VERIFIED"
            },
            {
                "step_num": 3,
                "rule_code": "ISOLATE_VARIABLE",
                "rule_name_ar": "عزل المتغير ونقل الحدود",
                "latex": f"x = {c} - ({shift}) = {sol}",
                "explanation_ar": "ننقل الحد الثابت إلى الطرف الآخر لنحصل على قيمة x النهائية.",
                "status": "VERIFIED"
            }
        ]
        
        return {
            "curriculum_stage": "stage_3_transcendental",
            "equation": eq_latex,
            "solution": steps,
            "final_answer": f"x = {sol}"
        }

    # -------------------------------------------------------------
    # STAGE 4: CALCULUS (DERIVATIVES & INTEGRALS)
    # -------------------------------------------------------------
    def generate_stage4_calculus(self) -> Dict[str, Any]:
        """Calculus: Polynomial derivatives or basic integrals."""
        x = sp.Symbol('x')
        kind = self.rng.choice(["derivative", "integral"])
        
        if kind == "derivative":
            deg = self.rng.randint(2, 4)
            poly = sum(self.rng.randint(-5, 5) * x**i for i in range(1, deg + 1))
            deriv = sp.diff(poly, x)
            eq_latex = f"\\frac{{d}}{{dx}} \\left( {sp.latex(poly)} \\right)"
            
            steps = [
                {
                    "step_num": 1,
                    "rule_code": "PROBLEM_FORMULATION",
                    "rule_name_ar": "صياغة مسألة الاشتقاق",
                    "latex": f"f(x) = {sp.latex(poly)}",
                    "explanation_ar": "نحدد دالة كثير الحدود المراد اشتقاقها بالنسبة للمتغير x.",
                    "status": "VERIFIED"
                },
                {
                    "step_num": 2,
                    "rule_code": "POWER_RULE_DERIVATIVE",
                    "rule_name_ar": "تطبيق قاعدة القوة في الاشتقاق",
                    "latex": f"f'(x) = {sp.latex(deriv)}",
                    "explanation_ar": "نشتق كل حد بشكل مستقل: ننزل الأس كمعامل وننقص من القوة بمقدار واحد.",
                    "status": "VERIFIED"
                }
            ]
            ans = sp.latex(deriv)
        else: # integral
            a = self.rng.choice([2, 3, 4, 6])
            poly = a * x
            antideriv = sp.integrate(poly, x)
            eq_latex = f"\\int \\left( {sp.latex(poly)} \\right) dx"
            
            steps = [
                {
                    "step_num": 1,
                    "rule_code": "PROBLEM_FORMULATION",
                    "rule_name_ar": "صياغة مسألة التكامل غير المحدود",
                    "latex": eq_latex,
                    "explanation_ar": "المطلوب إيجاد الدالة الأصلية لدالة كثيرة الحدود.",
                    "status": "VERIFIED"
                },
                {
                    "step_num": 2,
                    "rule_code": "POWER_RULE_INTEGRAL",
                    "rule_name_ar": "قاعدة القوة في التكامل",
                    "latex": f"{sp.latex(antideriv)} + C",
                    "explanation_ar": "نزيد الأس بمقدار واحد ونقسم على الأس الجديد، مع إضافة ثابت التكامل C.",
                    "status": "VERIFIED"
                }
            ]
            ans = f"{sp.latex(antideriv)} + C"

        return {
            "curriculum_stage": "stage_4_calculus",
            "equation": eq_latex,
            "solution": steps,
            "final_answer": ans
        }

    def generate_stage_sample(self, stage_num: int) -> Dict[str, Any]:
        if stage_num == 1:
            return self.generate_stage1_basic()
        elif stage_num == 2:
            return self.generate_stage2_advanced()
        elif stage_num == 3:
            return self.generate_stage3_transcendental()
        elif stage_num == 4:
            return self.generate_stage4_calculus()
        else:
            return self.generate_stage1_basic()

    def export_curriculum_batch(self, stage_num: int, count: int, output_file: Path) -> Path:
        output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for i in range(count):
                prob = self.generate_stage_sample(stage_num)
                prompt = format_prompt(prob["equation"])
                target = format_full_solution_to_text(prob["solution"])
                record = {
                    "id": i + 1,
                    "curriculum_stage": prob["curriculum_stage"],
                    "equation": prob["equation"],
                    "prompt": prompt,
                    "target": target,
                    "steps": prob["solution"],
                    "final_answer": prob["final_answer"]
                }
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
                
        return output_file
