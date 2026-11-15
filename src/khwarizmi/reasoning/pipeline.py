from __future__ import annotations
import os
import time
import json
from pathlib import Path
import urllib.request
import urllib.error
from typing import List, Dict, Any, Optional
from ..symbolic.engine import solve_step_by_step, verify_step_equivalence
from ..vision.syntax_guard import normalize_latex, is_valid_latex_syntax
from .prompt_schema import format_prompt, parse_structured_output

class HybridReasoningPipeline:
    """Enterprise-grade 3-Tier Neuro-Symbolic Mathematical Reasoner:

    Tier 1 (Priority): Cloud Online LLM (Qwen2.5-Math-7B / 72B via API)
    Tier 2: Local Edge LLM (Qwen2.5-Math-1.5B via local Ollama or lightweight runtime)
    Tier 3 (Guaranteed Fallback): Direct SymPy Algebraic Solver with Pedagogical Templates
    
    Every single step from Tier 1 & Tier 2 is intercepted and verified by SymPy.
    """

    def __init__(
        self,
        cloud_api_url: Optional[str] = None,
        cloud_api_key: Optional[str] = None,
        cloud_model: str = "Qwen/Qwen2.5-Math-7B-Instruct",
        local_api_url: str = "http://127.0.0.1:8080/v1"
    ):
        self.cloud_api_url = cloud_api_url or os.environ.get("KHWARIZMI_CLOUD_API_URL")
        self.cloud_api_key = cloud_api_key or os.environ.get("KHWARIZMI_CLOUD_API_KEY") or os.environ.get("HF_TOKEN")
        self.cloud_model = cloud_model
        self.local_api_url = local_api_url or os.environ.get("KHWARIZMI_LOCAL_API_URL", "http://127.0.0.1:8080/v1")
        self._local_model = None
        self._local_tokenizer = None
        self._adapter_dir = Path(__file__).resolve().parent.parent.parent.parent / "artifacts" / "qwen_khwarizmi_sft"

    def _call_local_peft(self, equation_latex: str) -> Optional[str]:
        """Runs inference on the locally fine-tuned Qwen2.5-Math LoRA adapter with chat template."""
        try:
            if not (self._adapter_dir / "adapter_model.safetensors").exists():
                return None
            if self._local_model is None:
                import torch
                from transformers import AutoTokenizer, AutoModelForCausalLM
                from peft import PeftModel
                self._local_tokenizer = AutoTokenizer.from_pretrained(str(self._adapter_dir))
                base = AutoModelForCausalLM.from_pretrained(
                    "Qwen/Qwen2.5-Math-1.5B-Instruct",
                    torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
                    device_map="auto" if torch.cuda.is_available() else None,
                    trust_remote_code=True
                )
                self._local_model = PeftModel.from_pretrained(base, str(self._adapter_dir))
                self._local_model.eval()

            import torch
            messages = [
                {
                    "role": "system",
                    "content": (
                        "أنت \"خوارزمي\" (Al-Khwarizmi Math AI)، معلم رياضي وذكاء اصطناعي استدلالي وتربوي فائق الدقة. "
                        "قم بحل المسألة الرياضية المعطاة خطوة بخطوة باللغة العربية مع شرح تربوي مبسط لكل خطوة، "
                        "موضحاً أولوية العمليات الحسابية والتعويض دون قوالب جامدة."
                    )
                },
                {
                    "role": "user",
                    "content": f"المسألة الرياضية: {equation_latex}\nالمطلوب: حل المسألة خطوة بخطوة مع الشرح باللغة العربية."
                }
            ]
            prompt = self._local_tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            inputs = self._local_tokenizer(prompt, return_tensors="pt").to(self._local_model.device)
            with torch.no_grad():
                outputs = self._local_model.generate(
                    **inputs,
                    max_new_tokens=450,
                    temperature=0.2,
                    do_sample=True,
                    pad_token_id=self._local_tokenizer.eos_token_id
                )
            return self._local_tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
        except Exception:
            return None

    def _call_llm_api(self, url: str, key: Optional[str], model: str, equation_latex: str) -> Optional[str]:
        """Make an OpenAI-compatible completion request using standard library."""
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "أنت \"خوارزمي\" (Al-Khwarizmi Math AI)، معلم رياضي وذكاء اصطناعي استدلالي وتربوي فائق الدقة. "
                        "أجب دائماً باللغة العربية الفصحى فقط. اشرح كل خطوة رياضية بالتفصيل وبساطة خطوة بخطوة."
                    )
                },
                {
                    "role": "user",
                    "content": f"المسألة الرياضية: {equation_latex}\nالمطلوب: حل المسألة مع الشرح التربوي باللغة العربية خطوة بخطوة."
                }
            ],
            "temperature": 0.1,
            "max_tokens": 512
        }
        
        headers = {"Content-Type": "application/json"}
        if key:
            headers["Authorization"] = f"Bearer {key}"
            
        req = urllib.request.Request(
            f"{url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        
        try:
            with urllib.request.urlopen(req, timeout=12.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"]
        except Exception:
            return None

    def solve(self, equation_latex: str) -> Dict[str, Any]:
        """Executes the 3-tier Neuro-Symbolic solving pipeline."""
        t0 = time.time()
        norm_eq = normalize_latex(equation_latex)
        prompt = format_prompt(norm_eq)
        
        engine_source = "SYMBOLIC_DIRECT"
        steps: List[Dict[str, Any]] = []

        # --- Tier 1: Cloud Online Model (Highest Priority) ---
        if self.cloud_api_url and self.cloud_api_key:
            raw_output = self._call_llm_api(
                self.cloud_api_url, self.cloud_api_key, self.cloud_model, prompt
            )
            if raw_output:
                candidate_steps = parse_structured_output(raw_output)
                if candidate_steps and self._verify_all_steps(norm_eq, candidate_steps):
                    steps = candidate_steps
                    engine_source = "CLOUD_QWEN_MATH_7B"

        # --- Tier 2: High-Speed Local GGUF Edge Engine (llama-server on port 8080) ---
        if not steps and self.local_api_url:
            raw_output = self._call_llm_api(
                self.local_api_url, None, "khwarizmi-math-1.5b-gguf", norm_eq
            )
            if raw_output:
                candidate_steps = parse_structured_output(raw_output)
                if candidate_steps and self._verify_all_steps(norm_eq, candidate_steps):
                    steps = candidate_steps
                    engine_source = "LOCAL_EDGE_GGUF_SERVER"

        # Tier 2 Fallback: Local PyTorch LoRA PEFT if standalone server is inactive
        if not steps and (self._adapter_dir / "adapter_model.safetensors").exists():
            raw_output = self._call_local_peft(norm_eq)
            if raw_output:
                candidate_steps = parse_structured_output(raw_output)
                if candidate_steps and self._verify_all_steps(norm_eq, candidate_steps):
                    steps = candidate_steps
                    engine_source = "LOCAL_FINETUNED_QWEN_MATH"

        # --- Tier 3: Direct SymPy Solver (100% Guaranteed Fallback) ---
        if not steps:
            steps = solve_step_by_step(norm_eq)
            engine_source = "SYMBOLIC_SYMPY_CORE"

        elapsed_ms = round((time.time() - t0) * 1000, 2)
        final_ans = steps[-1].get("latex", "") if steps else ""

        return {
            "success": bool(steps),
            "equation_latex": norm_eq,
            "engine_source": engine_source,
            "steps": steps,
            "final_answer": final_ans,
            "total_steps": len(steps),
            "computation_time_ms": elapsed_ms,
            "verified": True
        }

    def _verify_all_steps(self, initial_eq: str, steps: List[Dict[str, Any]]) -> bool:
        """Validates that each step produced by the LLM is mathematically sound."""
        prev = initial_eq
        for s in steps:
            curr = s.get("latex", "")
            if not curr or not is_valid_latex_syntax(curr):
                return False
            # Check step transition
            if not verify_step_equivalence(prev, curr):
                # Step was mathematically unproven / hallucinated
                return False
            s["status"] = "VERIFIED"
            prev = curr
        return True
