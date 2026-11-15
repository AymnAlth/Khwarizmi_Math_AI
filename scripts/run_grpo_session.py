"""
Al-Khwarizmi Math AI - GRPO Reinforcement Learning & Process Supervision Runner
Evaluates G=6 parallel rollouts per problem against SymPy Process Reward.
Mines Hard-Examples and computes Step Verification metrics.
"""

from __future__ import annotations
import sys
import time
import json
from pathlib import Path
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "src"))

from khwarizmi.training.grpo_loop import GRPOSelfPlayEngine
from khwarizmi.reasoning.prompt_schema import format_prompt, parse_structured_output
from khwarizmi.config import REPORTS_DIR

MODEL_NAME = "Qwen/Qwen2.5-Math-1.5B-Instruct"
ADAPTER_DIR = _ROOT / "artifacts" / "qwen_khwarizmi_sft"
DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"

# 20 diverse curriculum benchmark problems
BENCHMARK_PROBLEMS = [
    # 1. Arithmetic & Order of Operations
    r"8 \times 9 \div 7 + 5",
    r"12 - 4 \times 2 + 18 \div 3",
    r"15 + 6 \times 7 - 9",
    r"100 - 25 \times 3 + 14",
    # 2. Fractions & GCD Simplification
    r"6/8",
    r"14/21",
    r"18/24",
    r"\frac{3}{5} + \frac{2}{7}",
    # 3. Linear Equations
    r"3x - 9 = 15",
    r"5x + 10 = 35",
    r"2(x - 4) = 16",
    r"7x - 21 = 0",
    # 4. Quadratic Equations
    r"x^2 - 5x + 6 = 0",
    r"x^2 - 4 = 0",
    r"2x^2 + 5x - 3 = 0",
    r"x^2 - 6x + 9 = 0",
    # 5. Hard Edge Cases & Polynomials
    r"x^2 + 2x + 5 = 0",
    r"x^3 - 8 = 0",
    # 6. Basic Calculus & Derivatives
    r"\frac{d}{dx}(3x^2 + 4x - 5)",
    r"\frac{d}{dx}(x^3 - 2x)"
]


def run_grpo_session(num_generations: int = 6):
    print("=" * 70)
    print("   Al-Khwarizmi Math AI - GRPO Process Supervision Session")
    print("=" * 70)
    print(f"[*] Base Model: {MODEL_NAME}")
    print(f"[*] LoRA Adapter: {ADAPTER_DIR}")
    print(f"[*] Device: {DEVICE}")
    print(f"[*] Parallel Rollouts per Problem (G): {num_generations}")
    print(f"[*] Total Problems in Batch: {len(BENCHMARK_PROBLEMS)}")
    print(f"[*] Total Planned Trajectories: {len(BENCHMARK_PROBLEMS) * num_generations}")
    print("=" * 70)

    # 1. Load fine-tuned model
    print("[*] Loading Tokenizer & Fine-Tuned Model...")
    tokenizer = AutoTokenizer.from_pretrained(str(ADAPTER_DIR))
    base_model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
        device_map="auto" if torch.cuda.is_available() else None,
        trust_remote_code=True
    )
    model = PeftModel.from_pretrained(base_model, str(ADAPTER_DIR))
    model.eval()

    # 2. Initialize GRPO Engine
    engine = GRPOSelfPlayEngine(num_generations=num_generations)

    session_results = []
    total_rollouts = 0
    verified_steps_count = 0
    total_steps_count = 0
    hard_examples_count = 0
    group_rewards_all = []

    t_start = time.time()

    for idx, prob in enumerate(BENCHMARK_PROBLEMS, 1):
        print(f"\n[{idx}/{len(BENCHMARK_PROBLEMS)}] Evaluating: {prob}")
        prompt = format_prompt(prob)
        inputs = tokenizer(prompt, return_tensors="pt").to(DEVICE)

        rollouts = []
        with torch.no_grad():
            for g in range(num_generations):
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=450,
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )
                gen_text = tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
                rollouts.append(gen_text)
                total_rollouts += 1

        eval_res = engine.evaluate_group_rollouts(prob, rollouts)
        session_results.append(eval_res)
        group_rewards_all.append(eval_res["mean_reward"])

        if eval_res["is_hard_example"]:
            hard_examples_count += 1
            print(f"   [!] HARD EXAMPLE MINED! Mean Reward: {eval_res['mean_reward']:.2f}")
        else:
            print(f"   [✓] Mean Reward: {eval_res['mean_reward']:.2f} | Best Trajectory Reward: {eval_res['best_trajectory_reward']:.2f}")

        # Accumulate step verification counts
        for r_info in eval_res["rollouts"]:
            total_steps_count += r_info["steps_count"]
            for s_r in r_info["step_rewards"]:
                if s_r >= 1.0:
                    verified_steps_count += 1

    elapsed = time.time() - t_start

    # 3. Compile Statistics & Report
    avg_reward = float(np.mean(group_rewards_all))
    step_verification_acc = (verified_steps_count / max(1, total_steps_count)) * 100
    hard_ratio = (hard_examples_count / len(BENCHMARK_PROBLEMS)) * 100

    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_problems": len(BENCHMARK_PROBLEMS),
        "rollouts_per_problem": num_generations,
        "total_rollouts_generated": total_rollouts,
        "total_reasoning_steps": total_steps_count,
        "mathematically_verified_steps": verified_steps_count,
        "step_verification_accuracy_percent": round(step_verification_acc, 2),
        "mean_group_process_reward": round(avg_reward, 3),
        "hard_examples_mined": hard_examples_count,
        "hard_example_rate_percent": round(hard_ratio, 2),
        "elapsed_seconds": round(elapsed, 1),
        "device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"
    }

    report_path = REPORTS_DIR / "grpo_session_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n" + "=" * 70)
    print("   GRPO Session Completed Successfully!")
    print("=" * 70)
    print(f"[*] Total Rollouts Generated: {total_rollouts}")
    print(f"[*] Total Reasoning Steps: {total_steps_count}")
    print(f"[*] Mathematically Verified Steps: {verified_steps_count} ({step_verification_acc:.1f}%)")
    print(f"[*] Mean Process Reward: {avg_reward:.3f}")
    print(f"[*] Hard Examples Mined: {hard_examples_count} ({hard_ratio:.1f}%)")
    print(f"[*] Report Saved: {report_path}")
    print(f"[*] Hard Examples Log: {engine.hard_examples_path}")
    print(f"[*] Total Time: {elapsed:.1f}s")
    print("=" * 70)


if __name__ == "__main__":
    run_grpo_session(num_generations=4)
