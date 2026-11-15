---
language:
- ar
- en
license: mit
base_model: Qwen/Qwen2.5-Math-1.5B-Instruct
library_name: peft
pipeline_tag: text-generation
tags:
- math
- reasoning
- arabic
- neuro-symbolic
- cot
- qlora
- grpo
- education
- sympy
- qwen2.5-math
model_creator: Ayman Al-Dhahabi
model_name: Al-Khwarizmi Math AI (Qwen2.5-Math-1.5B-Arabic-Reasoner)
widget:
- text: "اشرح باللغة العربية خطوة بخطوة مع أولويات العمليات حل المقدار: 100 - 25 * 3 + 14"
---

# 🧮 خوارزمي | Al-Khwarizmi Math AI
### نموذج الاستدلال الرياضي والشرح التربوي العصبي-الرمزي باللغة العربية
**An Industrial-Grade, Neuro-Symbolic Mathematical Reasoner & Pedagogical Explainer**

[![Developer](https://img.shields.io/badge/Developer-Ayman%20Al--Dhahabi-blue.svg)](https://github.com/AymnAlth)
[![GitHub Repo](https://img.shields.io/badge/GitHub-Khwarizmi__Math__AI-black?logo=github)](https://github.com/AymnAlth/Khwarizmi_Math_AI)
[![Base Model](https://img.shields.io/badge/Base%20Model-Qwen2.5--Math--1.5B-indigo)](https://huggingface.co/Qwen/Qwen2.5-Math-1.5B-Instruct)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 👤 معلومات المطور (Developer Profile)
* **المطور الرئيسي:** **أيمن الذاهبي (Ayman Al-Dhahabi)**
* **البريد الإلكتروني:** [a77499n@gmail.com](mailto:a77499n@gmail.com)
* **الهاتف / واتساب:** [+967 774998429](tel:+967774998429)
* **المستودع الرسمي:** [https://github.com/AymnAlth/Khwarizmi_Math_AI](https://github.com/AymnAlth/Khwarizmi_Math_AI)

---

## 📌 نبذة عن النموذج (Model Overview)
نموذج **خوارزمي (Al-Khwarizmi Math AI)** هو نموذج استدلالي متخصص تم تدريبه بالاعتماد على `Qwen/Qwen2.5-Math-1.5B-Instruct` لتقديم حلول وشروحات تربوية دقيقة خطوة بخطوة للمسائل والمعادلات الرياضية باللغة العربية الفصحى.

تم تصميم النموذج ليعمل ضمن معمارية **عصبية-رمزية (Neuro-Symbolic Architecture)** هجينة، حيث تتولى الشبكة العصبية تفكيك المسألة واستنتاج سلاسل التفكير المنطقي (`<think>`) وصياغة الشرح التربوي باللغة العربية، بينما يتولى المحرك الرمزي (SymPy) التحقق الحسابي القطعي لكل خطوة للقضاء التام على الهلوسة الحسابية.

---

## 🎯 تفاصيل التدريب المنهجي (Training Details)
* **تقنية التدريب:** QLoRA (4-bit NormalFloat quantization with `bfloat16` compute).
* **معاملات LoRA:** رتبة المصفوفة $r = 16$، معامل التكبير $\alpha = 32$، ومعدل الإسقاط $\text{dropout} = 0.05$.
* **الوحدات المستهدفة (Target Modules):** `q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj`.
* **المنهج التعليمي (Curriculum Learning):** تم التدريب على 4 مراحل تصاعدية:
  1. **المرحلة الأولى:** العمليات الحسابية، أولويات العمليات، تبسيط الكسور، والمعادلات الخطية.
  2. **المرحلة الثانية:** المعادلات التربيعية، المميز الجبري، وتحليل المقادير.
  3. **المرحلة الثالثة:** الدوال الأسية واللوغاريتمية.
  4. **المرحلة الرابعة:** التفاضل، الاشتقاق، والتكامل.
* **التعلم التعزيزي (GRPO):** تحسين الاستدلال عبر خوارزمية *Group Relative Policy Optimization* مع الإشراف على خطوات الحل (Process Supervision).

---

## 💻 طريقة استخدام النموذج برمجياً (Quick Inference Code)

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

BASE_MODEL = "Qwen/Qwen2.5-Math-1.5B-Instruct"
ADAPTER_REPO = "ModeAyman/Khwarizmi-Math-AI"

# 1. تحميل الموزع والنموذج الأساسي
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    torch_dtype=torch.bfloat16,
    device_map="auto",
    trust_remote_code=True,
)

# 2. دمج أوزان خوارزمي المدربة (LoRA)
model = PeftModel.from_pretrained(base_model, ADAPTER_REPO)
model.eval()

# 3. إعداد المدخل باللغة العربية
prompt = "حل المقدار التالي مع الشرح التربوي باللغة العربية وأولويات العمليات: 100 - 25 * 3 + 14"
messages = [{"role": "user", "content": prompt}]
text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = tokenizer([text], return_tensors="pt").to(model.device)

# 4. توليد الحل الاستدلالي
outputs = model.generate(**inputs, max_new_tokens=512, temperature=0.3)
response = tokenizer.decode(outputs[0][len(inputs.input_ids[0]):], skip_special_tokens=True)
print(response)
```

---

## 📜 الترخيص (License)
هذا النموذج منشور ومتاح للاستخدام الأكاديمي والبحثي تحت رخصة **MIT License**.
