from __future__ import annotations
import time
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
import numpy as np

from ..symbolic.engine import verify_step_equivalence, solve_step_by_step
from ..vision.syntax_guard import is_valid_latex_syntax
from ..reasoning.prompt_schema import parse_structured_output
from ..config import REPORTS_DIR

class GRPOSelfPlayEngine:
    """Group Relative Policy Optimization (GRPO) with Process-Supervised Rewards

    and Hard-Example Mining.
    """

    def __init__(self, num_generations: int = 6):
        self.num_generations = num_generations
        self.hard_examples_path = REPORTS_DIR / "hard_examples_log.jsonl"
        self.hard_examples_path.parent.mkdir(parents=True, exist_ok=True)

    def compute_step_rewards(self, initial_equation: str, steps: List[Dict[str, Any]]) -> Tuple[float, List[float]]:
        """Assigns Process Supervision rewards to each individual reasoning step.

        +1.0: Mathematically verified step
        -1.5: Algebraic violation / hallucination
        -2.0: Malformed LaTeX syntax
        +0.5: Clean pedagogical explanation bonus
        """
        if not steps:
            return -5.0, []

        step_rewards = []
        prev_eq = initial_equation

        for s in steps:
            latex = s.get("latex", "")
            exp_ar = s.get("explanation_ar", "")

            # 1. Syntax Guard
            if not is_valid_latex_syntax(latex):
                step_rewards.append(-2.0)
                continue

            # 2. Mathematical Equivalence
            if verify_step_equivalence(prev_eq, latex):
                r = 1.0
                if len(exp_ar) > 10:
                    r += 0.5 # Pedagogical clarity bonus
                step_rewards.append(r)
                prev_eq = latex
            else:
                step_rewards.append(-1.5)

        total_reward = float(np.sum(step_rewards))
        return total_reward, step_rewards

    def evaluate_group_rollouts(self, equation: str, rollouts: List[str]) -> Dict[str, Any]:
        """Evaluates G=6 parallel reasoning trajectories and computes GRPO advantages."""
        group_rewards = []
        detailed_rollouts = []

        for text in rollouts:
            steps = parse_structured_output(text)
            total_r, step_rs = self.compute_step_rewards(equation, steps)
            group_rewards.append(total_r)
            detailed_rollouts.append({
                "total_reward": total_r,
                "step_rewards": step_rs,
                "steps_count": len(steps)
            })

        rewards_arr = np.array(group_rewards, dtype=np.float32)
        mean_r = float(np.mean(rewards_arr))
        std_r = float(np.std(rewards_arr)) + 1e-6
        advantages = ((rewards_arr - mean_r) / std_r).tolist()

        # Hard-Example Detection: If all 6 rollouts failed (mean reward <= 0)
        is_hard_example = mean_r <= 0.0
        if is_hard_example:
            self.log_hard_example(equation, mean_r)

        best_idx = int(np.argmax(rewards_arr))

        return {
            "equation": equation,
            "mean_reward": round(mean_r, 3),
            "std_reward": round(std_r, 3),
            "advantages": [round(a, 3) for a in advantages],
            "best_trajectory_idx": best_idx,
            "best_trajectory_reward": float(rewards_arr[best_idx]),
            "is_hard_example": is_hard_example,
            "rollouts": detailed_rollouts
        }

    def log_hard_example(self, equation: str, score: float):
        """Logs difficult edge cases for automated mining and congeneric synthesis."""
        with open(self.hard_examples_path, "a", encoding="utf-8") as f:
            rec = {
                "equation": equation,
                "score": score,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
