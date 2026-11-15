"""
Al-Khwarizmi Math AI - SFT Training Runner
Fine-tunes Qwen2.5-Math-1.5B-Instruct with native bfloat16 LoRA on Arabic CoT dataset.
Optimized for NVIDIA RTX 5060 Laptop GPU (sm_120 Blackwell, 8GB VRAM).
"""

from __future__ import annotations
import os
import sys
import time
import math
from pathlib import Path
import torch
from torch.utils.data import DataLoader
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    get_cosine_schedule_with_warmup
)
from peft import LoraConfig, get_peft_model

_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_ROOT / "src"))

from khwarizmi.training.sft_trainer import MathSFTDataset

MODEL_NAME = "Qwen/Qwen2.5-Math-1.5B-Instruct"
TRAIN_FILE = _ROOT / "data" / "processed" / "khwarizmi_cot_train.jsonl"
VAL_FILE = _ROOT / "data" / "processed" / "khwarizmi_cot_val.jsonl"
OUTPUT_DIR = _ROOT / "artifacts" / "qwen_khwarizmi_sft"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Training hyperparameters (Optimized for RTX 5060 8GB Blackwell)
BATCH_SIZE = 1
GRAD_ACCUM = 16  # Effective batch size = 16
LEARNING_RATE = 2e-4
EPOCHS = 2
MAX_LENGTH = 960
WARMUP_RATIO = 0.05
DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


def train():
    print("=" * 65)
    print("   Al-Khwarizmi Neuro-Symbolic Math AI - SFT Training")
    print("=" * 65)
    print(f"[*] Base Model: {MODEL_NAME}")
    print(f"[*] Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")
    print(f"[*] Train Dataset: {TRAIN_FILE}")
    print(f"[*] Output Directory: {OUTPUT_DIR}")
    print("=" * 65)

    # 1. Tokenizer
    print("[*] Loading Tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # 2. Datasets
    print("[*] Preparing Datasets...")
    train_dataset = MathSFTDataset(TRAIN_FILE, tokenizer, max_length=MAX_LENGTH)
    val_dataset = MathSFTDataset(VAL_FILE, tokenizer, max_length=MAX_LENGTH)
    print(f"[+] Loaded {len(train_dataset)} training samples, {len(val_dataset)} validation samples.")

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, pin_memory=False)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)

    # 3. Model with native bfloat16 + LoRA
    print("[*] Loading model with native bfloat16...")
    base_model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.bfloat16,
        device_map="cuda:0",
        trust_remote_code=True
    )
    base_model.gradient_checkpointing_enable()

    lora_config = LoraConfig(
        r=8,
        lora_alpha=16,
        target_modules=["q_proj", "v_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )

    model = get_peft_model(base_model, lora_config)
    model.print_trainable_parameters()

    # 4. Optimizer & Scheduler
    total_steps = (len(train_loader) // GRAD_ACCUM) * EPOCHS
    warmup_steps = int(total_steps * WARMUP_RATIO)
    optimizer = torch.optim.AdamW(model.parameters(), lr=LEARNING_RATE, weight_decay=0.01)
    scheduler = get_cosine_schedule_with_warmup(optimizer, warmup_steps, total_steps)

    print(f"[*] Total Optimization Steps: {total_steps} (Warmup: {warmup_steps})")
    print("[*] Starting Training Loop...")

    model.train()
    step_count = 0
    start_time = time.time()

    for epoch in range(1, EPOCHS + 1):
        running_loss = 0.0
        optimizer.zero_grad()
        torch.cuda.empty_cache()

        for batch_idx, batch in enumerate(train_loader):
            input_ids = batch["input_ids"].to(DEVICE)
            attention_mask = batch["attention_mask"].to(DEVICE)
            labels = batch["labels"].to(DEVICE)

            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels
            )
            loss = outputs.loss / GRAD_ACCUM
            loss.backward()

            running_loss += loss.item() * GRAD_ACCUM

            if (batch_idx + 1) % GRAD_ACCUM == 0 or (batch_idx + 1) == len(train_loader):
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad()
                torch.cuda.empty_cache()
                step_count += 1

                if step_count % 5 == 0:
                    lr = scheduler.get_last_lr()[0]
                    avg_loss = running_loss / 5.0
                    running_loss = 0.0
                    elapsed = time.time() - start_time
                    vram_mb = torch.cuda.memory_allocated() / (1024 ** 2)
                    print(f"  [Epoch {epoch}/{EPOCHS} | Step {step_count}/{total_steps}] "
                          f"Loss: {avg_loss:.4f} | LR: {lr:.2e} | VRAM: {vram_mb:.0f}MB | Elapsed: {elapsed:.1f}s")

        # Validation at end of epoch
        model.eval()
        val_loss = 0.0
        torch.cuda.empty_cache()
        with torch.no_grad():
            for v_idx, val_batch in enumerate(val_loader):
                if v_idx >= 50:  # Validate first 50 samples for speed
                    break
                v_ids = val_batch["input_ids"].to(DEVICE)
                v_mask = val_batch["attention_mask"].to(DEVICE)
                v_labels = val_batch["labels"].to(DEVICE)
                v_out = model(input_ids=v_ids, attention_mask=v_mask, labels=v_labels)
                val_loss += v_out.loss.item()
        val_loss /= min(len(val_loader), 50)
        print(f"\n[+] === Epoch {epoch} Complete | Validation Loss: {val_loss:.4f} ===\n")
        model.train()

    # 5. Save Adapter Checkpoint
    print(f"[*] Saving trained LoRA adapter to {OUTPUT_DIR}...")
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    print(f"[✓] Training Completed Successfully in {time.time() - start_time:.1f}s!")


if __name__ == "__main__":
    train()
