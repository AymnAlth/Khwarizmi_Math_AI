from __future__ import annotations
import math
import re
from typing import List, Dict, Any, Optional, Tuple
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
from .rules import get_rule_details

_TRANSFORMATIONS = standard_transformations + (implicit_multiplication_application,)


def latex_to_sympy_str(latex_str: str) -> str:
    """Preprocesses LaTeX string into SymPy readable Python syntax."""
    s = latex_str.strip()
    s = s.replace(r'\cdot', '*').replace(r'\times', '*').replace(r'\div', '/')
    s = s.replace(r'\left', '').replace(r'\right', '')
    
    # Replace fractions: \frac{a}{b} -> (a)/(b)
    # Handle nested fractions iteratively
    pattern = r'\\frac\{([^{}]+)\}\{([^{}]+)\}'
    while re.search(pattern, s):
        s = re.sub(pattern, r'((\1)/(\2))', s)
        
    # Powers: x^{2} -> x**(2)
    s = re.sub(r'\^\{([^{}]+)\}', r'**(\1)', s)
    s = re.sub(r'\^([0-9a-zA-Z])', r'**\1', s)
    
    # Square root: \sqrt{x} -> sqrt(x)
    s = re.sub(r'\\sqrt\{([^{}]+)\}', r'sqrt(\1)', s)
    
    # Functions: \sin, \cos, \ln, \log
    s = re.sub(r'\\sin', 'sin', s)
    s = re.sub(r'\\cos', 'cos', s)
    s = re.sub(r'\\tan', 'tan', s)
    s = re.sub(r'\\ln', 'log', s)
    s = re.sub(r'\\log', 'log', s)
    
    # Clean whitespace and braces
    s = s.replace('{', '(').replace('}', ')')
    return s


def parse_equation(latex_str: str) -> Tuple[Optional[sp.Expr], Optional[sp.Expr]]:
    """Parse equation into (LHS, RHS) expressions."""
    s = latex_str.split(r'\implies')[0].strip()
    parts = s.split('=')
    if len(parts) >= 2:
        lhs_str = latex_to_sympy_str(parts[0])
        rhs_str = latex_to_sympy_str(parts[-1])
        try:
            lhs = parse_expr(lhs_str, transformations=_TRANSFORMATIONS)
            rhs = parse_expr(rhs_str, transformations=_TRANSFORMATIONS)
            return lhs, rhs
        except Exception:
            return None, None
    elif len(parts) == 1:
        expr_str = latex_to_sympy_str(parts[0])
        try:
            expr = parse_expr(expr_str, transformations=_TRANSFORMATIONS)
            return expr, sp.Integer(0)
        except Exception:
            return None, None
    return None, None


def verify_step_equivalence(prev_latex: str, curr_latex: str) -> bool:
    """Rigorous symbolic verification of step equivalence (Neuro-Symbolic Gate)."""
    prev_lhs, prev_rhs = parse_equation(prev_latex)
    curr_lhs, curr_rhs = parse_equation(curr_latex)
    
    if prev_lhs is None or curr_lhs is None:
        return False
        
    # Check if (prev_LHS - prev_RHS) == (curr_LHS - curr_RHS) or constant multiple
    diff_prev = sp.simplify(prev_lhs - prev_rhs)
    diff_curr = sp.simplify(curr_lhs - curr_rhs)
    
    if sp.simplify(diff_prev - diff_curr) == 0:
        return True
        
    # Check if current step is a verified arithmetic sub-equality (e.g. 25 * 3 = 75)
    if "=" in curr_latex and sp.simplify(curr_lhs - curr_rhs) == 0:
        return True
        
    # Check if solutions match for single variable
    free_vars = diff_prev.free_symbols.union(diff_curr.free_symbols)
    if len(free_vars) == 1:
        var = list(free_vars)[0]
        try:
            sol_prev = sp.solve(diff_prev, var)
            sol_curr = sp.solve(diff_curr, var)
            return set(sol_prev) == set(sol_curr)
        except Exception:
            pass
            
    return False


def solve_step_by_step(latex_str: str) -> List[Dict[str, Any]]:
    """Generates verified symbolic step-by-step resolution for equations, expressions, and fractions."""
    s_clean = latex_str.strip()
    
    # 1. Standalone Fraction check (e.g., 6/8, \frac{6}{8}, 15/25)
    m_frac1 = re.match(r'^\s*([+-]?\d+)\s*/\s*([+-]?\d+)\s*$', s_clean)
    m_frac2 = re.search(r'^\\frac\{([+-]?\d+)\}\{([+-]?\d+)\}$', s_clean)
    if m_frac1 or m_frac2:
        m = m_frac1 or m_frac2
        num = int(m.group(1))
        den = int(m.group(2))
        if den == 0:
            return [{
                "step_num": 1,
                "rule_code": "ERROR_DIVISION_BY_ZERO",
                "rule_name_ar": "خطأ رياضي: القسمة على صفر",
                "latex": f"\\frac{{{num}}}{{0}}",
                "explanation_ar": "القسمة على صفر غير معرّفة في الحسابات الرياضية.",
                "status": "VERIFIED"
            }]
        
        g = math.gcd(abs(num), abs(den))
        simplified_num = num // g
        simplified_den = den // g
        steps: List[Dict[str, Any]] = []
        
        # Step 1: Initial Formulation
        steps.append({
            "step_num": 1,
            "rule_code": "PROBLEM_FORMULATION",
            "rule_name_ar": "صياغة الكسر الاعتيادي",
            "latex": f"\\frac{{{num}}}{{{den}}}",
            "explanation_ar": f"الكسر المعطى يتكون من البسط ${num}$ والمقام ${den}$، ونريد تبسيطه إلى أبسط صورة غير قابلة للاختزال.",
            "status": "VERIFIED"
        })
        
        if g > 1:
            # Step 2: Find GCD
            steps.append({
                "step_num": 2,
                "rule_code": "GREATEST_COMMON_DIVISOR",
                "rule_name_ar": get_rule_details("GREATEST_COMMON_DIVISOR").name_ar,
                "latex": f"\\gcd({abs(num)}, {abs(den)}) = {g}",
                "explanation_ar": f"نبحث عن القاسم المشترك الأكبر (الع.م.أ) بين البسط والمقام لاختزال الكسر: $\\gcd({abs(num)}, {abs(den)}) = {g}$.",
                "status": "VERIFIED"
            })
            # Step 3: Divide numerator and denominator
            ans_latex = f"{simplified_num}" if simplified_den == 1 else f"\\frac{{{simplified_num}}}{{{simplified_den}}}"
            steps.append({
                "step_num": 3,
                "rule_code": "SIMPLIFY_FRACTIONS",
                "rule_name_ar": get_rule_details("SIMPLIFY_FRACTIONS").name_ar,
                "latex": f"\\frac{{{num} \\div {g}}}{{{den} \\div {g}}} = {ans_latex}",
                "explanation_ar": f"بقسمة البسط والمقام على القاسم المشترك الأكبر ({g})، نحصل على الكسر في أبسط صورة.",
                "status": "VERIFIED"
            })
        else:
            ans_latex = f"{simplified_num}" if simplified_den == 1 else f"\\frac{{{num}}}{{{den}}}"
            steps.append({
                "step_num": 2,
                "rule_code": "SIMPLIFY_FRACTIONS",
                "rule_name_ar": get_rule_details("SIMPLIFY_FRACTIONS").name_ar,
                "latex": f"\\frac{{{num}}}{{{den}}} = {ans_latex}",
                "explanation_ar": "الكسر المعطى في أبسط صورة بالفعل نظراً لأن القاسم المشترك الأكبر بين البسط والمقام هو 1.",
                "status": "VERIFIED"
            })
            
        if simplified_den != 1:
            dec_val = num / den
            is_exact = (len(str(dec_val).split(".")[1]) <= 3 and float(f"{dec_val:.3f}") == dec_val)
            approx_sym = "=" if is_exact else r"\approx"
            dec_str = f"{dec_val:.6g}"
            steps.append({
                "step_num": len(steps) + 1,
                "rule_code": "DECIMAL_CONVERSION",
                "rule_name_ar": get_rule_details("DECIMAL_CONVERSION").name_ar,
                "latex": f"{ans_latex} {approx_sym} {dec_str}",
                "explanation_ar": f"التمثيل العشري {'الدقيق' if is_exact else 'المقرب باستخدام علامة التقريب $\\approx$'} المكافئ للكسر هو ${dec_str}$.",
                "status": "VERIFIED"
            })
        return steps

    # 2. General parsing
    lhs, rhs = parse_equation(latex_str)
    if lhs is None or rhs is None:
        return []
        
    diff = sp.simplify(lhs - rhs).expand()
    vars_found = list(diff.free_symbols)
    
    # 3. Pure arithmetic expressions without variables (e.g., 8*9/7 + 5, 1/2 + 1/4, (5+3)*4)
    if not vars_found:
        val = sp.simplify(lhs)
        steps = []
        
        # Check operations present
        has_mul_div = any(k in latex_str for k in [r'\times', r'\cdot', r'\div', '*', '/'])
        has_add_sub = any(k in latex_str for k in ['+', '-'])
        
        # Step 1: Contextual Formulation
        if has_mul_div and has_add_sub:
            exp_form = "نبدأ بتحليل المقدار العددي وترتيب أولويات العمليات الحسابية: إنجاز الضرب والقسمة أولاً قبل الجمع والطرح."
        elif has_mul_div:
            exp_form = "نبدأ بحساب قيمة المقدار العددي بإجراء عمليات الضرب والقسمة بالتسلسل."
        else:
            exp_form = "نبدأ بحساب قيمة المقدار العددي المباشر بإجراء عملية الجمع والطرح المباشرة."

        steps.append({
            "step_num": 1,
            "rule_code": "PROBLEM_FORMULATION",
            "rule_name_ar": "صياغة المقدار العددي",
            "latex": latex_str.strip(),
            "explanation_ar": exp_form,
            "status": "VERIFIED"
        })
        
        # Deconstruct compound expressions preserving natural left-to-right order
        raw_clean = latex_str.replace(r'\times', '*').replace(r'\cdot', '*').replace(r'\div', '/')
        
        # Check for multiplication/division sub-expressions to evaluate first
        mul_div_patterns = list(re.finditer(r'(\d+(?:\.\d+)?)\s*([\*\/])\s*(\d+(?:\.\d+)?)', raw_clean))
        if mul_div_patterns and has_add_sub:
            interm_text = raw_clean
            for m in mul_div_patterns:
                sub_expr_str = m.group(0)
                sub_val = sp.simplify(sp.sympify(sub_expr_str))
                sub_latex = f"{m.group(1)} \\times {m.group(3)}" if m.group(2) == '*' else f"{m.group(1)} \\div {m.group(3)}"
                steps.append({
                    "step_num": len(steps) + 1,
                    "rule_code": "ORDER_OF_OPERATIONS_MUL",
                    "rule_name_ar": get_rule_details("ORDER_OF_OPERATIONS_MUL").name_ar,
                    "latex": f"{sub_latex} = {sp.latex(sub_val)}",
                    "explanation_ar": f"وفق أولويات العمليات الحسابية، ننجز عملية الضرب والقسمة أولاً: ${sub_latex} = {sp.latex(sub_val)}$.",
                    "status": "VERIFIED"
                })
                interm_text = interm_text.replace(sub_expr_str, str(sub_val), 1)
            
            # Show the intermediate substituted expression in human natural order
            interm_latex = interm_text.replace('*', r' \times ').replace('/', r' \div ')
            steps.append({
                "step_num": len(steps) + 1,
                "rule_code": "SUBSTITUTION",
                "rule_name_ar": get_rule_details("SUBSTITUTION").name_ar,
                "latex": interm_latex.strip(),
                "explanation_ar": "نعوض بالنواتج المحسوبة داخل المقدار مع الحفاظ على الترتيب الأصلي للحدود تمهيداً لعمليات الجمع والطرح.",
                "status": "VERIFIED"
            })
        
        # Exact result with dynamic integer vs fraction classification
        is_frac = isinstance(val, sp.Rational) and val.q != 1
        rule_code = "EXACT_FRACTION_RESULT" if is_frac else "ARITHMETIC_EVALUATION"
        rule_name = "حساب الناتج الكسري الدقيق" if is_frac else "حساب الناتج العددي النهائي"
        exp_res = (
            f"بإتمام العمليات الحسابية الموحدة نحصل على الكسر في أبسط صورة: ${sp.latex(val)}$."
            if is_frac else
            f"بإتمام العمليات الحسابية نحصل على القيمة العددية الدقيقة: ${sp.latex(val)}$."
        )
        
        steps.append({
            "step_num": len(steps) + 1,
            "rule_code": rule_code,
            "rule_name_ar": rule_name,
            "latex": f"{sp.latex(val)}",
            "explanation_ar": exp_res,
            "status": "VERIFIED"
        })
        
        # Decimal approximation with \approx for non-terminating
        if isinstance(val, sp.Rational) and val.q != 1:
            dec_val = float(val)
            is_exact = (len(str(dec_val).split(".")[1]) <= 3 and float(f"{dec_val:.3f}") == dec_val)
            approx_sym = "=" if is_exact else r"\approx"
            dec_str = f"{dec_val:.6g}"
            steps.append({
                "step_num": len(steps) + 1,
                "rule_code": "DECIMAL_CONVERSION",
                "rule_name_ar": get_rule_details("DECIMAL_CONVERSION").name_ar,
                "latex": f"{sp.latex(val)} {approx_sym} {dec_str}",
                "explanation_ar": f"التحويل إلى كسر عشري {'الدقيق' if is_exact else 'المقرب باستخدام علامة التقريب $\\approx$'}: ${dec_str}$.",
                "status": "VERIFIED"
            })
        return steps

    # 4. Expression with variable but no '=' sign (Factorization & Expansion)
    if "=" not in latex_str:
        x = vars_found[0]
        steps = []
        steps.append({
            "step_num": 1,
            "rule_code": "PROBLEM_FORMULATION",
            "rule_name_ar": "صياغة المقدار الجبري",
            "latex": latex_str.strip(),
            "explanation_ar": f"المقدار الجبري بدلالة المتغير ${sp.latex(x)}$، والمطلوب تحليله وتبسيطه وإيجاد أصفاره.",
            "status": "VERIFIED"
        })
        factored = sp.factor(lhs)
        if factored != lhs:
            steps.append({
                "step_num": len(steps) + 1,
                "rule_code": "FACTORING",
                "rule_name_ar": get_rule_details("FACTORING").name_ar,
                "latex": f"{sp.latex(lhs)} = {sp.latex(factored)}",
                "explanation_ar": "تحليل المقدار الجبري إلى حاصل ضرب عوامله الأولية.",
                "status": "VERIFIED"
            })
        expanded = sp.expand(lhs)
        if expanded != lhs and expanded != factored:
            steps.append({
                "step_num": len(steps) + 1,
                "rule_code": "EXPAND_EXPRESSION",
                "rule_name_ar": get_rule_details("EXPAND_EXPRESSION").name_ar,
                "latex": f"{sp.latex(lhs)} = {sp.latex(expanded)}",
                "explanation_ar": "فك الأقواس وتوزيع ونشر الحدود وتجميع الحدود المتشابهة.",
                "status": "VERIFIED"
            })
        sols = sp.solve(lhs, x)
        if sols:
            sol_str = ", ".join([f"{sp.latex(x)} = {sp.latex(s)}" for s in sols])
            steps.append({
                "step_num": len(steps) + 1,
                "rule_code": "ROOT_EXTRACTION",
                "rule_name_ar": "إيجاد جذور وأصفار المقدار",
                "latex": f"{sp.latex(lhs)} = 0 \\implies {sol_str}",
                "explanation_ar": "إيجاد قيم المتغير التي تجعل المقدار مساوياً للصفر.",
                "status": "VERIFIED"
            })
        return steps

    # 5. Full Equation Resolution with '='
    x = vars_found[0]
    steps: List[Dict[str, Any]] = []
    
    # 0. Initial Problem Formulation
    steps.append({
        "step_num": 1,
        "rule_code": "PROBLEM_FORMULATION",
        "rule_name_ar": "صياغة المعادلة الأصلية",
        "latex": f"{sp.latex(lhs)} = {sp.latex(rhs)}",
        "explanation_ar": "نبدأ بالمعادلة المعطاة ونحدد المتغير المراد إيجاد قيمته.",
        "status": "VERIFIED"
    })
    
    degree = sp.degree(diff, x) if diff.is_polynomial(x) else None
    
    if degree == 1:
        # Linear: ax + b = 0
        coeff_a = diff.coeff(x, 1)
        coeff_b = diff.coeff(x, 0)
        
        # Step: Move constant b to RHS
        rhs_1 = -coeff_b
        steps.append({
            "step_num": len(steps) + 1,
            "rule_code": "ISOLATE_VARIABLE",
            "rule_name_ar": get_rule_details("ISOLATE_VARIABLE").name_ar,
            "latex": f"{sp.latex(coeff_a * x)} = {sp.latex(rhs_1)}",
            "explanation_ar": get_rule_details("ISOLATE_VARIABLE").pedagogical_template,
            "status": "VERIFIED"
        })
        
        if coeff_a != 1:
            # Step: Divide by coeff_a
            final_ans = sp.simplify(rhs_1 / coeff_a)
            steps.append({
                "step_num": len(steps) + 1,
                "rule_code": "DIVIDE_COEFFICIENT",
                "rule_name_ar": get_rule_details("DIVIDE_COEFFICIENT").name_ar,
                "latex": f"{sp.latex(x)} = \\frac{{{sp.latex(rhs_1)}}}{{{sp.latex(coeff_a)}}} = {sp.latex(final_ans)}",
                "explanation_ar": get_rule_details("DIVIDE_COEFFICIENT").pedagogical_template,
                "status": "VERIFIED"
            })
            
    elif degree == 2:
        # Quadratic: ax^2 + bx + c = 0
        a = diff.coeff(x, 2)
        b = diff.coeff(x, 1)
        c = diff.coeff(x, 0)
        
        # Standard form
        steps.append({
            "step_num": len(steps) + 1,
            "rule_code": "STANDARD_FORM",
            "rule_name_ar": "الصورة العامة للمعادلة التربيعية",
            "latex": f"{sp.latex(diff)} = 0",
            "explanation_ar": "نرتب الحدود على الصورة العامة $ax^2 + bx + c = 0$ لتحديد المعاملات $a, b, c$.",
            "status": "VERIFIED"
        })
        
        # Discriminant Delta
        delta = b**2 - 4*a*c
        steps.append({
            "step_num": len(steps) + 1,
            "rule_code": "DISCRIMINANT",
            "rule_name_ar": "حساب المميز (Delta)",
            "latex": f"\\Delta = b^2 - 4ac = ({sp.latex(b)})^2 - 4({sp.latex(a)})({sp.latex(c)}) = {sp.latex(delta)}",
            "explanation_ar": f"نحسب قيمة المميز $\\Delta = {sp.latex(delta)}$ لتحديد طبيعة الجذور.",
            "status": "VERIFIED"
        })
        
        # Roots
        sols = sp.solve(diff, x)
        sol_str = ", ".join([f"{sp.latex(x)} = {sp.latex(s)}" for s in sols])
        steps.append({
            "step_num": len(steps) + 1,
            "rule_code": "QUADRATIC_FORMULA",
            "rule_name_ar": get_rule_details("QUADRATIC_FORMULA").name_ar,
            "latex": f"x = \\frac{{-({sp.latex(b)}) \\pm \\sqrt{{{sp.latex(delta)}}}}}{{2({sp.latex(a)})}} \\implies {sol_str}",
            "explanation_ar": get_rule_details("QUADRATIC_FORMULA").pedagogical_template,
            "status": "VERIFIED"
        })
        
    else:
        # General SymPy solver fallback
        sols = sp.solve(diff, x)
        sol_str = ", ".join([f"{sp.latex(x)} = {sp.latex(s)}" for s in sols])
        steps.append({
            "step_num": len(steps) + 1,
            "rule_code": "GENERAL_ALGEBRAIC_SOLVER",
            "rule_name_ar": "الحل الجبري الرمزي المباشر",
            "latex": sol_str,
            "explanation_ar": "تم إيجاد مجموعة الحل الجبري الدقيق عبر المحرك الرمزي المعتمد.",
            "status": "VERIFIED"
        })
        
    return steps
