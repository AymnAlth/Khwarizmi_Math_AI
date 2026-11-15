"""
Test inference on fine-tuned Al-Khwarizmi Math model.
"""

from __future__ import annotations
import sys
from pathlib import Path
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

MODEL_NAME = "Qwen/Qwen2.5-Math-1.5B-Instruct"
ADAPTER_DIR = Path(__file__).resolve().parent.parent / "artifacts" / "qwen_khwarizmi_sft"

print(f"[*] Loading fine-tuned model from {ADAPTER_DIR}...")
tokenizer = AutoTokenizer.from_pretrained(str(ADAPTER_DIR))
base_model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.bfloat16,
    device_map="cuda:0",
    trust_remote_code=True
)
model = PeftModel.from_pretrained(base_model, str(ADAPTER_DIR))
model.eval()

problems = [
    r"8 \times 9 \div 7 + 5",
    r"x^2 - 5x + 6 = 0"
]

for problem in problems:
    print("\n" + "=" * 65)
    print(f"[*] Solving: {problem}")
    print("=" * 65)
    messages = [
        {
            "role": "system",
            "content": (
                "أنت \"خوارزمي\" (Al-Khwarizmi Math AI)، نظام ذكاء اصطناعي رياضي استدلالي وتربوي فائق الذكاء والدقة. "
                "مهمتك حل المسألة الرياضية المعطاة بذكاء واستدلال حقيقي غير مقيد بقوالب جامدة مع توضيح مسار التفكير <think> والخطوات المنظمة."
            )
        },
        {
            "role": "user",
            "content": f"المسألة الرياضية: {problem}\nالمطلوب: فكر بعمق وحل المسألة خطوة بخطوة مع الشرح التربوي باللغة العربية."
        }
    ]
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda:0")

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=400,
            temperature=0.2,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )

    response = tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
    print(response)

print("\n[✓] Inference Test Complete!")
