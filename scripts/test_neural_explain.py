import sys
from pathlib import Path
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

MODEL_NAME = "Qwen/Qwen2.5-Math-1.5B-Instruct"
ADAPTER_DIR = Path(__file__).resolve().parent.parent / "artifacts" / "qwen_khwarizmi_sft"

tokenizer = AutoTokenizer.from_pretrained(str(ADAPTER_DIR))
base_model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.bfloat16,
    device_map="cuda:0",
    trust_remote_code=True
)
model = PeftModel.from_pretrained(base_model, str(ADAPTER_DIR))
model.eval()

problems = ["6 + 12", r"100 - 25 \times 3 + 14"]

for prob in problems:
    print("\n" + "=" * 65)
    print(f"PROB: {prob}")
    print("=" * 65)
    messages = [
        {
            "role": "system",
            "content": (
                "أنت \"خوارزمي\"، معلم ومساعد ذكي في الرياضيات. "
                "اشرح للطالب الحل خطوة بخطوة باللغة العربية بأسلوب تعليمي واضح ومقنع ومنطقي دون قوالب جامدة."
            )
        },
        {
            "role": "user",
            "content": f"حل المسألة التالية خطوة بخطوة مع الشرح باللغة العربية: {prob}"
        }
    ]
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda:0")
    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=300,
            temperature=0.1,
            pad_token_id=tokenizer.eos_token_id
        )
    print(tokenizer.decode(out[0][inputs.input_ids.shape[1]:], skip_special_tokens=True))
