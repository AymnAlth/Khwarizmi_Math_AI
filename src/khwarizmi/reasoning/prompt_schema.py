from __future__ import annotations
import re
from typing import List, Dict, Any, Optional
from ..symbolic.rules import get_rule_details

SYSTEM_PROMPT = """أنت "خوارزمي" (Al-Khwarizmi Math AI)، نظام ذكاء اصطناعي رياضي استدلالي وتربوي فائق الذكاء والدقة.
مهمتك حل المسألة الرياضية المعطاة بذكاء واستدلال حقيقي غير مقيد بقوالب جامدة، مع الالتزام بالمعايير التالية:
1. التفكير الرياضي الحر والمنطقي (<think>):
   قبل كتابة أي خطوة، فكر بعمق وحلل المسألة في وسم <think>:
   - حدد نوع المدخل بدقة (هل هو تعبير عددي حسابي، أم مقدار جبري، أم معادلة تحتاج إيجاد مجهول، أم مسألة تفاضل/تكامل).
   - خطط لاستراتيجية الحل وناقش أولوية العمليات الحسابية خطوة بخطوة دون القفز أو تجاوز العمليات الوسيطة.
   - تحقق من صحة كل عملية حسابية وكسرية ذهنياً.
2. الشرح التربوي الشيق والواضح:
   اشرح للطالب "لماذا" نقوم بهذه الخطوة بأسلوب عربي فصيح ومبسط قبل تنفيذها.
3. الدقة الرياضية الصارمة:
   - فرّق دائماً بين التعبير العددي والمعادلة.
   - استخدم علامة التقريب \\approx عند تقريب الكسور غير المنتهية إلى أعداد عشرية، واستخدم = فقط للقيم الدقيقة.
4. البنية النهائية للمخرجات:
<think>
[تحليل المسألة واستدلال العمليات الحسابية والمنطق الرياضي خطوة بخطوة باللغة العربية]
</think>
<steps>
<step>
[RULE] اسم_القاعدة_بالرمز
[LATEX] التعبير_الرياضي_المحدث
[EXPLANATION_AR] الشرح_التربوي_المبسط
</step>
</steps>
<final_answer>الناتج_النهائي_الدقيق</final_answer>
"""

USER_TEMPLATE = "المسألة الرياضية: {equation_latex}\nالمطلوب: فكر بعمق وحل المسألة خطوة بخطوة مع الشرح التربوي باللغة العربية."


def format_prompt(equation_latex: str) -> str:
    """Format prompt for Qwen2.5-Math model."""
    return f"{SYSTEM_PROMPT}\n\n{USER_TEMPLATE.format(equation_latex=equation_latex)}"


def format_step_to_text(step: Dict[str, Any]) -> str:
    """Format single step into schema text."""
    rule = step.get("rule_code", "ALGEBRAIC_STEP")
    latex = step.get("latex", "")
    exp_ar = step.get("explanation_ar", "")
    return f"<step>\n[RULE] {rule}\n[LATEX] {latex}\n[EXPLANATION_AR] {exp_ar}\n</step>"


def format_full_solution_to_text(steps: List[Dict[str, Any]], thinking: Optional[str] = None, final_ans: Optional[str] = None) -> str:
    """Format entire solution with thinking and final answer."""
    parts = []
    if thinking:
        parts.append(f"<think>\n{thinking.strip()}\n</think>")
    
    steps_text = "\n\n".join([format_step_to_text(s) for s in steps])
    parts.append(f"<steps>\n{steps_text}\n</steps>")
    
    if final_ans:
        parts.append(f"<final_answer>{final_ans.strip()}</final_answer>")
    elif steps:
        parts.append(f"<final_answer>{steps[-1].get('latex', '').strip()}</final_answer>")
        
    return "\n\n".join(parts)


def parse_structured_output(output_text: str) -> List[Dict[str, Any]]:
    """Parse model output text into structured step list.
    Supports both explicit XML <step> tags and natural-language Step 1: / الخطوة 1: formats.
    """
    steps = []
    step_blocks = re.findall(r'<step>(.*?)</step>', output_text, re.DOTALL)
    
    if step_blocks:
        for i, block in enumerate(step_blocks, 1):
            rule_match = re.search(r'\[RULE\]\s*(.*?)(?=\n|\[|$)', block)
            latex_match = re.search(r'\[LATEX\]\s*(.*?)(?=\n|\[|$)', block)
            exp_match = re.search(r'\[EXPLANATION_AR\]\s*(.*?)(?=\n|\[|$)', block, re.DOTALL)
            
            rule = rule_match.group(1).strip() if rule_match else "UNKNOWN_RULE"
            latex = latex_match.group(1).strip() if latex_match else ""
            exp = exp_match.group(1).strip() if exp_match else ""
            
            steps.append({
                "step_num": i,
                "rule_code": rule,
                "rule_name_ar": get_rule_details(rule).name_ar,
                "latex": latex,
                "explanation_ar": exp,
                "status": "UNVERIFIED"
            })
        return steps

    # Resilient fallback: parse natural step indicators and numbered lists
    splits = re.split(r'(?:^|\n)\s*(?:(?:Step|\bالخطوة)\s*(\d+)[:\.]?|(\d+)[\.\)])\s*', output_text, flags=re.IGNORECASE)
    if len(splits) >= 4:
        for i in range(1, len(splits), 3):
            num_str = splits[i] or splits[i+1]
            if not num_str or i+2 >= len(splits):
                continue
            s_num = int(num_str)
            s_content = splits[i+2].strip()
            
            # Extract math expressions
            math_match = re.search(r'([0-9a-zA-Z\s\+\-\*\/\^\(\)\.\=\<\>\\\{\}]+(?:=|\\approx)[0-9a-zA-Z\s\+\-\*\/\^\(\)\.\<\>\\\{\}]+)', s_content)
            if not math_match:
                math_match = re.search(r'([0-9a-zA-Z\s\+\-\*\/\^\(\)\.\<\>\\\{\}]{3,})', s_content)
                
            if math_match:
                latex_cand = math_match.group(1).strip()
                # Clean explanation
                exp_cand = s_content.replace(latex_cand, "").strip(" :.,\n-")
                if not exp_cand:
                    exp_cand = s_content
            else:
                latex_cand = s_content
                exp_cand = "تنفيذ الخطوة الرياضية المنهجية."
                
            steps.append({
                "step_num": s_num,
                "rule_code": f"STEP_{s_num}",
                "rule_name_ar": get_rule_details(f"STEP_{s_num}").name_ar,
                "latex": latex_cand,
                "explanation_ar": exp_cand,
                "status": "UNVERIFIED"
            })
        if steps:
            return steps

    # Fallback: parse chained inline mathematical equalities (e.g. A = B = C)
    if "=" in output_text:
        # Clean latex formatting artifacts
        clean_text = re.sub(r'\\(?:boxed|quad)\s*\{?([^{}]+)\}?', r'\1', output_text)
        eq_parts = [p.strip() for p in clean_text.split('=') if p.strip() and not p.strip().startswith(('\\boxed', 'The '))]
        if len(eq_parts) >= 2:
            chained_steps = []
            for k, part in enumerate(eq_parts, 1):
                clean_part = re.sub(r'\s*\\(?:quad|boxed).*$', '', part).strip()
                if k == 1:
                    exp = "صياغة المقدار الرياضي تمهيداً لترتيب العمليات."
                    r_name = "صياغة المقدار"
                elif k == len(eq_parts):
                    exp = f"إتمام العمليات الحسابية للوصول إلى الناتج النهائي: ${clean_part}$."
                    r_name = "الناتج النهائي الدقيق"
                else:
                    exp = f"التعويض بالقيم المحسوبة وفق أولويات العمليات الحسابية: ${clean_part}$."
                    r_name = "ترتيب أولويات العمليات"
                    
                chained_steps.append({
                    "step_num": k,
                    "rule_code": f"STEP_{k}",
                    "rule_name_ar": r_name,
                    "latex": clean_part,
                    "explanation_ar": exp,
                    "status": "UNVERIFIED"
                })
            return chained_steps

    return []


def extract_thinking(output_text: str) -> Optional[str]:
    """Extract free-form thinking trace if present."""
    m = re.search(r'<think>(.*?)</think>', output_text, re.DOTALL)
    return m.group(1).strip() if m else None


def extract_final_answer(output_text: str) -> Optional[str]:
    """Extract explicit final answer tag if present."""
    m = re.search(r'<final_answer>(.*?)</final_answer>', output_text, re.DOTALL)
    return m.group(1).strip() if m else None
