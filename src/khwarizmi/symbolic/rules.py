"""
Mathematical Rules Definition and Arabic Nomenclature.
This module classifies and maps algebraic and analytical rules with exact
pedagogical Arabic definitions.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict

@dataclass(frozen=True)
class MathRule:
    code: str
    name_ar: str
    name_en: str
    category: str
    pedagogical_template: str

RULES_CATALOG: Dict[str, MathRule] = {
    # Stage 0: Arithmetic & Fractions
    "ORDER_OF_OPERATIONS_MUL": MathRule(
        code="ORDER_OF_OPERATIONS_MUL",
        name_ar="إجراء عمليات الضرب والقسمة أولاً",
        name_en="Order of Operations (Multiplication & Division First)",
        category="arithmetic",
        pedagogical_template="وفق الترتيب الرياضي لأولويات العمليات، ننجز عمليات الضرب والقسمة من اليسار إلى اليمين قبل البدء بالجمع والطرح."
    ),
    "SUBSTITUTION": MathRule(
        code="SUBSTITUTION",
        name_ar="التعويض بالقيم المحسوبة في المقدار",
        name_en="Intermediate Value Substitution",
        category="arithmetic",
        pedagogical_template="نعوض بالقيم الوسيطة الناتجة عن عمليات الضرب والقسمة داخل المقدار العددي تمهيداً لعمليات الجمع والطرح."
    ),
    "COMMON_DENOMINATOR": MathRule(
        code="COMMON_DENOMINATOR",
        name_ar="توحيد المقامات لإجراء الجمع والطرح",
        name_en="Finding Common Denominator",
        category="arithmetic",
        pedagogical_template="لجمع أو طرح الكسور مع الأعداد الصحيحة، نوحد المقامات بإيجاد المضاعف المشترك الأصغر للمقامات."
    ),
    "EXACT_FRACTION_RESULT": MathRule(
        code="EXACT_FRACTION_RESULT",
        name_ar="حساب الناتج الكسري الدقيق",
        name_en="Exact Rational Simplification",
        category="arithmetic",
        pedagogical_template="نقوم بجمع وبسط الحدود بعد توحيد المقامات للوصول إلى الكسر الاعتيادي الدقيق في أبسط صورة."
    ),
    "GREATEST_COMMON_DIVISOR": MathRule(
        code="GREATEST_COMMON_DIVISOR",
        name_ar="إيجاد القاسم المشترك الأكبر (الع.م.أ)",
        name_en="Greatest Common Divisor (GCD)",
        category="arithmetic",
        pedagogical_template="نبحث عن أكبر عدد صحيح يقسم كلاً من البسط والمقام بدون باقٍ لاختزال الكسر لأبسط صورة ممكنة."
    ),
    "DECIMAL_CONVERSION": MathRule(
        code="DECIMAL_CONVERSION",
        name_ar="التحويل إلى كسر عشري",
        name_en="Decimal Conversion",
        category="arithmetic",
        pedagogical_template="نقسم البسط على المقام للحصول على القيمة العشرية الدقيقة المكافئة للكسر الاعتيادي."
    ),
    "ARITHMETIC_EVALUATION": MathRule(
        code="ARITHMETIC_EVALUATION",
        name_ar="إجراء العمليات الحسابية وفق الأولويات",
        name_en="Arithmetic Evaluation & Order of Operations",
        category="arithmetic",
        pedagogical_template="نطبق ترتيب العمليات الحسابية بدقة: الأقواس، الأسس والجذور، الضرب والقسمة، ثم الجمع والطرح."
    ),
    "EXPAND_EXPRESSION": MathRule(
        code="EXPAND_EXPRESSION",
        name_ar="نشر وفك المقدار الجبري",
        name_en="Algebraic Expansion",
        category="basic_algebra",
        pedagogical_template="نقوم بفك الأقواس وتوزيع الضرب على الجمع ثم دمج الحدود المتشابهة لتنظيم المقدار."
    ),

    # Stage 1: Basic Algebra
    "SIMPLIFY_FRACTIONS": MathRule(
        code="SIMPLIFY_FRACTIONS",
        name_ar="توحيد المقامات وتبسيط الكسور",
        name_en="Common Denominator & Fraction Simplification",
        category="basic_algebra",
        pedagogical_template="لتبسيط الجمع أو الطرح بين الكسور، نقوم بتوحيد المقامات عبر إيجاد المضاعف المشترك الأصغر للمقامات."
    ),
    "ISOLATE_VARIABLE": MathRule(
        code="ISOLATE_VARIABLE",
        name_ar="عزل المتغير ونقل الحدود",
        name_en="Variable Isolation & Transposition",
        category="basic_algebra",
        pedagogical_template="نقوم بنقل الحدود الثابتة إلى الطرف الآخر مع تغيير إشارتها لعزل المتغير في طرف بمفرده."
    ),
    "DIVIDE_COEFFICIENT": MathRule(
        code="DIVIDE_COEFFICIENT",
        name_ar="القسمة على معامل المتغير",
        name_en="Division by Variable Coefficient",
        category="basic_algebra",
        pedagogical_template="للتخلص من المعامل المضروب في المتغير والحصول على قيمته النهائية، نقسم طرفي المعادلة على ذلك المعامل."
    ),
    "EXPONENT_RULES": MathRule(
        code="EXPONENT_RULES",
        name_ar="تطبيق قوانين الأسس",
        name_en="Exponent Power Laws",
        category="basic_algebra",
        pedagogical_template="عند ضرب الأساسات المتشابهة تجمع الأسس، وعند القسمة تطرح الأسس."
    ),
    
    # Stage 2: Advanced Algebra
    "QUADRATIC_FORMULA": MathRule(
        code="QUADRATIC_FORMULA",
        name_ar="القانون العام لحل المعادلة التربيعية",
        name_en="Quadratic Formula",
        category="advanced_algebra",
        pedagogical_template="نستخدم القانون العام $x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$ بعد حساب المميز $\\Delta = b^2 - 4ac$ لتحديد عدد ونوع الجذور."
    ),
    "FACTORING": MathRule(
        code="FACTORING",
        name_ar="التحليل إلى العوامل",
        name_en="Factoring Polynomials",
        category="advanced_algebra",
        pedagogical_template="نقوم بتحليل المقدار الجبري إلى حاصل ضرب عوامله الأولية لتسهيل إيجاد الحلول."
    ),
    "COMPLETING_SQUARE": MathRule(
        code="COMPLETING_SQUARE",
        name_ar="إكمال المربع",
        name_en="Completing the Square",
        category="advanced_algebra",
        pedagogical_template="نضيف ونطرح مربع نصف معامل الحد الأوسط لتحويل الطرف إلى مربع كامل."
    ),
    "SYSTEM_ELIMINATION": MathRule(
        code="SYSTEM_ELIMINATION",
        name_ar="طريقة الحذف في نظم المعادلات",
        name_en="System of Equations Elimination",
        category="advanced_algebra",
        pedagogical_template="نضرب إحدى المعادلتين في عدد مناسب لجعل معاملي أحد المتغيرين متعاكسين ثم نجمعهما لحذف ذلك المتغير."
    ),
    
    # Stage 3: Transcendental Functions
    "TRIG_IDENTITY": MathRule(
        code="TRIG_IDENTITY",
        name_ar="المتطابقات المثلثية الأساسية",
        name_en="Fundamental Trigonometric Identities",
        category="transcendental",
        pedagogical_template="نطبق متطابقة فيثاغورس $\\sin^2(x) + \\cos^2(x) = 1$ لتبسيط المعادلة وتوحيد الدوال المثلثية."
    ),
    "LOG_PROPERTIES": MathRule(
        code="LOG_PROPERTIES",
        name_ar="خواص اللوغاريتمات",
        name_en="Logarithm Laws",
        category="transcendental",
        pedagogical_template="نحول الجمع بين اللوغاريتمات إلى لوغاريتم لحاصل الضرب: $\\log(a) + \\log(b) = \\log(ab)$."
    ),
    
    # Stage 4: Calculus
    "POWER_RULE_DERIVATIVE": MathRule(
        code="POWER_RULE_DERIVATIVE",
        name_ar="قاعدة القوة في الاشتقاق",
        name_en="Power Rule for Differentiation",
        category="calculus",
        pedagogical_template="لاشتقاق الحد $x^n$، ننزل الأس كمعامل وننقص من الأس واحداً: $\\frac{d}{dx} x^n = n x^{n-1}$."
    ),
    "CHAIN_RULE": MathRule(
        code="CHAIN_RULE",
        name_ar="قاعدة السلسلة (قاعدة مشتقة الدالة المركبة)",
        name_en="Chain Rule",
        category="calculus",
        pedagogical_template="نشتق الدالة الخارجية أولاً بالنسبة للداخلية، ثم نضرب الناتج في مشتقة الدالة الداخلية."
    ),
    "INTEGRATION_BY_PARTS": MathRule(
        code="INTEGRATION_BY_PARTS",
        name_ar="التكامل بالتجزيء",
        name_en="Integration by Parts",
        category="calculus",
        pedagogical_template="نستخدم صيغة $\\int u\\,dv = uv - \\int v\\,du$ باختيار $u$ يسهل اشتقاقه و$dv$ يسهل تكامله."
    ),
}


def get_rule_details(rule_code: str) -> MathRule:
    """Retrieve rule details by code with safe fallback."""
    clean_code = rule_code.strip().upper().replace(" ", "_")
    return RULES_CATALOG.get(clean_code, MathRule(
        code=clean_code,
        name_ar="خطوة تبسيط جبري عامة",
        name_en="General Algebraic Simplification",
        category="general",
        pedagogical_template="نقوم بتبسيط الحدود المتشابهة لتسريع الوصول إلى الحل الصحيح."
    ))
