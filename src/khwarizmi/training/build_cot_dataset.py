"""
Al-Khwarizmi Neuro-Symbolic Math AI - CoT Dataset Synthesizer
Generates authentic Arabic Chain-of-Thought (CoT) reasoning datasets for fine-tuning
Qwen2.5-Math-1.5B with natural pedagogical rationale, granular step decomposition,
and SymPy verification.
"""

from __future__ import annotations
import json
import math
import random
from pathlib import Path
from typing import List, Dict, Any
import sympy as sp

from ..symbolic.engine import solve_step_by_step
from ..reasoning.prompt_schema import SYSTEM_PROMPT, USER_TEMPLATE, format_full_solution_to_text

random.seed(42)

OUT_DIR = Path("data/processed")
OUT_DIR.mkdir(parents=True, exist_ok=True)
TRAIN_FILE = OUT_DIR / "khwarizmi_cot_train.jsonl"
VAL_FILE = OUT_DIR / "khwarizmi_cot_val.jsonl"


def generate_arithmetic_cot() -> Dict[str, Any]:
    """Generate compound arithmetic expressions with explicit Order of Operations."""
    ops = [
        # (latex_str, thinking_ar)
        (
            r"8 \times 9 \div 7 + 5",
            "المسألة المطروحة هي مقدار عددي حسابي يتضمن عمليات ضرب وقسمة وجمع.\n"
            "وفقاً لأولويات العمليات الرياضية، نبدأ بالضرب والقسمة من اليسار إلى اليمين قبل الجمع.\n"
            "العملية الأولى: 8 * 9 = 72.\n"
            "العملية الثانية: 72 مقسومة على 7 تعطي الكسر 72/7.\n"
            "العملية الثالثة: جمع الكسر مع 5 بتوحيد المقامات: 5 = 35/7، ومجموع البسطين 72 + 35 = 107/7.\n"
            "التقريب العشري: بما أن 107/7 كسر غير منتهٍ، نستخدم علامة التقريب 107/7 ≈ 15.2857."
        ),
        (
            r"\frac{6}{8}",
            "المطلوب هو اختزال الكسر الاعتيادي 6/8 إلى أبسط صورة ممكنة.\n"
            "نبحث عن القاسم المشترك الأكبر (الع.م.أ) بين البسط (6) والمقام (8).\n"
            "عوامل 6 هي 1, 2, 3, 6، وعوامل 8 هي 1, 2, 4, 8. القاسم المشترك الأكبر هو 2.\n"
            "نقسم كلاً من البسط والمقام على 2: 6 ÷ 2 = 3، و 8 ÷ 2 = 4.\n"
            "إذن الكسر في أبسط صورة هو 3/4، والقيمة العشرية الدقيقة المكافئة هي 0.75."
        ),
        (
            r"12 + 15 \div 3 - 4 \times 2",
            "هذا مقدار عددي مركب يتضمن جمعاً وطرحاً وقسمة وضرباً.\n"
            "نحدد الأولويات: القسمة والضرب أولاً من اليسار لليمين:\n"
            "1. 15 ÷ 3 = 5\n"
            "2. 4 * 2 = 8\n"
            "التعويض في المقدار: 12 + 5 - 8.\n"
            "الآن نجري الجمع والطرح: 12 + 5 = 17، ثم 17 - 8 = 9."
        ),
        (
            r"\frac{1}{2} + \frac{1}{3} \times \frac{6}{5}",
            "نلاحظ وجود عملية ضرب كسور وعملية جمع.\n"
            "الأولوية للضرب: 1/3 * 6/5 = (1 * 6) / (3 * 5) = 6/15 = 2/5 بعد التبسيط.\n"
            "الآن نجمع 1/2 + 2/5: نوحد المقامات بإيجاد المضاعف المشترك الأصغر للمقامين 2 و 5 وهو 10.\n"
            "1/2 = 5/10 و 2/5 = 4/10.\n"
            "المجموع: (5 + 4) / 10 = 9/10 = 0.9."
        ),
    ]
    eq, think = random.choice(ops)
    steps = solve_step_by_step(eq)
    final_ans = steps[-1]["latex"] if steps else ""
    return {
        "problem": eq,
        "thinking": think,
        "steps": steps,
        "final_answer": final_ans
    }


def generate_linear_cot() -> Dict[str, Any]:
    """Generate linear equation with pedagogical reasoning."""
    a = random.choice([2, 3, 4, 5, 6, 7])
    b = random.randint(1, 15) * random.choice([1, -1])
    sol = random.randint(-10, 10)
    c = a * sol + b
    
    sign = "+" if b > 0 else "-"
    eq_str = f"{a}x {sign} {abs(b)} = {c}"
    
    think = (
        f"المسألة هي معادلة خطية من الدرجة الأولى بمجهول واحد هو x.\n"
        f"الهدف هو عزل المتغير x في طرف بمفرده.\n"
        f"الخطوة الأولى: التخلص من الحد الثابت ({b:+d}) بنقله إلى الطرف الأيمن بعكس إشارته: {c} - ({b}) = {c - b}.\n"
        f"تصبح المعادلة: {a}x = {c - b}.\n"
        f"الخطوة الثانية: التخلص من المعامل المضروب في x بقسمة طرفي المعادلة على {a}.\n"
        f"x = ({c - b}) / {a} = {sol}."
    )
    
    steps = solve_step_by_step(eq_str)
    final_ans = steps[-1]["latex"] if steps else f"x = {sol}"
    return {
        "problem": eq_str,
        "thinking": think,
        "steps": steps,
        "final_answer": final_ans
    }


def generate_quadratic_cot() -> Dict[str, Any]:
    """Generate quadratic equation with discriminant and root reasoning."""
    r1 = random.randint(-6, 6)
    r2 = random.randint(-6, 6)
    # (x - r1)(x - r2) = x^2 - (r1+r2)x + r1*r2 = 0
    b = -(r1 + r2)
    c = r1 * r2
    sign_b = "+" if b >= 0 else "-"
    sign_c = "+" if c >= 0 else "-"
    eq_str = f"x^2 {sign_b} {abs(b)}x {sign_c} {abs(c)} = 0"
    
    delta = b**2 - 4 * 1 * c
    think = (
        f"المعادلة المعطاة معادلة تربيعية على الصورة القياسية ax^2 + bx + c = 0 حيث a=1, b={b}, c={c}.\n"
        f"نحسب المميز دلتا (Delta) لتحديد طبيعة الجذور: Delta = b^2 - 4ac = ({b})^2 - 4(1)({c}) = {delta}.\n"
        f"بما أن المميز أكبر من أو يساوي الصفر، فللمعادلة جذران حقيقيان.\n"
        f"بتطبيق القانون العام أو التحليل إلى عوامل: (x - ({r1}))(x - ({r2})) = 0.\n"
        f"إذن الجذور هي x = {r1} أو x = {r2}."
    )
    
    steps = solve_step_by_step(eq_str)
    final_ans = steps[-1]["latex"] if steps else f"x = {r1}, x = {r2}"
    return {
        "problem": eq_str,
        "thinking": think,
        "steps": steps,
        "final_answer": final_ans
    }


def format_chatml_record(item: Dict[str, Any]) -> Dict[str, str]:
    """Formats item into standard Qwen2.5 ChatML format."""
    user_msg = USER_TEMPLATE.format(equation_latex=item["problem"])
    assistant_msg = format_full_solution_to_text(
        item["steps"],
        thinking=item["thinking"],
        final_ans=item["final_answer"]
    )
    
    # Standard ChatML formatted training instance
    prompt_text = (
        f"<|im_start|>system\n{SYSTEM_PROMPT}<|im_end|>\n"
        f"<|im_start|>user\n{user_msg}<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )
    target_text = f"{assistant_msg}<|im_end|>"
    
    return {
        "prompt": prompt_text,
        "target": target_text,
        "problem": item["problem"],
        "final_answer": item["final_answer"]
    }


def build_datasets(total_samples: int = 2000, val_ratio: float = 0.1):
    print(f"[*] Building {total_samples} authentic Arabic Chain-of-Thought reasoning samples...")
    generators = [generate_arithmetic_cot, generate_linear_cot, generate_quadratic_cot]
    
    records = []
    for _ in range(total_samples):
        gen = random.choice(generators)
        item = gen()
        if item["steps"]:
            records.append(format_chatml_record(item))
            
    random.shuffle(records)
    n_val = int(len(records) * val_ratio)
    val_records = records[:n_val]
    train_records = records[n_val:]
    
    with open(TRAIN_FILE, "w", encoding="utf-8") as f:
        for r in train_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            
    with open(VAL_FILE, "w", encoding="utf-8") as f:
        for r in val_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            
    print(f"[+] Saved {len(train_records)} training samples to {TRAIN_FILE}")
    print(f"[+] Saved {len(val_records)} validation samples to {VAL_FILE}")


if __name__ == "__main__":
    build_datasets(total_samples=1500)
