"""
Export and merge LoRA adapter into base model, then convert to GGUF format for edge deployment.
"""

from __future__ import annotations
import sys
import os
import subprocess
from pathlib import Path
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

BASE_DIR = Path(__file__).resolve().parent.parent
ADAPTER_DIR = BASE_DIR / "artifacts" / "qwen_khwarizmi_sft"
MERGED_DIR = BASE_DIR / "artifacts" / "qwen_khwarizmi_merged"
GGUF_DIR = BASE_DIR / "artifacts" / "gguf"
GGUF_OUTFILE = GGUF_DIR / "khwarizmi_math_1.5b_q8_0.gguf"
LLAMA_CPP_DIR = Path.home() / "tools" / "llama.cpp"

def merge_and_export():
    print(f"[*] Step 1: Merging LoRA adapter from {ADAPTER_DIR} into base model...")
    MERGED_DIR.mkdir(parents=True, exist_ok=True)
    GGUF_DIR.mkdir(parents=True, exist_ok=True)
    
    tokenizer = AutoTokenizer.from_pretrained(str(ADAPTER_DIR))
    print("[*] Loading base model Qwen/Qwen2.5-Math-1.5B-Instruct in bfloat16...")
    base_model = AutoModelForCausalLM.from_pretrained(
        "Qwen/Qwen2.5-Math-1.5B-Instruct",
        torch_dtype=torch.bfloat16,
        device_map="cuda" if torch.cuda.is_available() else "cpu",
        trust_remote_code=True
    )
    
    print("[*] Applying LoRA weights...")
    model = PeftModel.from_pretrained(base_model, str(ADAPTER_DIR))
    merged_model = model.merge_and_unload()
    
    print(f"[*] Saving merged model to {MERGED_DIR}...")
    merged_model.save_pretrained(str(MERGED_DIR), safe_serialization=True)
    tokenizer.save_pretrained(str(MERGED_DIR))
    print("[+] Model successfully merged and saved!")
    
    # Free GPU memory before GGUF conversion
    del merged_model
    del base_model
    del model
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

def convert_to_gguf():
    print(f"[*] Step 2: Converting merged model to GGUF (Q8_0 quantization) at {GGUF_OUTFILE}...")
    convert_script = LLAMA_CPP_DIR / "convert_hf_to_gguf.py"
    if not convert_script.exists():
        raise FileNotFoundError(f"convert_hf_to_gguf.py not found at {convert_script}")
        
    cmd = [
        sys.executable,
        str(convert_script),
        str(MERGED_DIR),
        "--outfile", str(GGUF_OUTFILE),
        "--outtype", "q8_0"
    ]
    
    print(f"[*] Running conversion command: {' '.join(cmd)}")
    res = subprocess.run(cmd, check=True)
    print(f"[+] GGUF conversion completed with exit code: {res.returncode}")
    print(f"[+] GGUF file size: {GGUF_OUTFILE.stat().st_size / (1024 * 1024):.2f} MB")

if __name__ == "__main__":
    merge_and_export()
    convert_to_gguf()
    print("\n[=== SUCCESS ===] Edge model packaged as GGUF ready for instant deployment!")
