from __future__ import annotations
import sys
import time
import argparse
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "src"))

from khwarizmi.config import ARABIC_SYNTH_DIR
from khwarizmi.reasoning.generator import EnhancedCurriculumGenerator

STAGES = {
    1: ("stage_1_basic_algebra", "curriculum_stage1_basic_algebra.jsonl"),
    2: ("stage_2_advanced_algebra", "curriculum_stage2_advanced_algebra.jsonl"),
    3: ("stage_3_transcendental", "curriculum_stage3_transcendental.jsonl"),
    4: ("stage_4_calculus", "curriculum_stage4_calculus.jsonl")
}

def main():
    parser = argparse.ArgumentParser(description="Al-Khwarizmi Curriculum Dataset Generator")
    parser.add_argument("--stage", type=int, choices=[1, 2, 3, 4, 0], default=1, help="Curriculum stage (1-4, 0 for all)")
    parser.add_argument("--count", type=int, default=5000, help="Number of verified problems per stage")
    args = parser.parse_args()

    gen = EnhancedCurriculumGenerator(seed=42)
    stages_to_run = [args.stage] if args.stage != 0 else [1, 2, 3, 4]

    for s in stages_to_run:
        name, filename = STAGES[s]
        out_path = ARABIC_SYNTH_DIR / filename
        print(f"\n--- Generating Stage {s}: {name} ({args.count:,} problems) ---")
        t0 = time.time()
        gen.export_curriculum_batch(stage_num=s, count=args.count, output_file=out_path)
        elapsed = time.time() - t0
        print(f"Completed Stage {s} in {elapsed:.2f}s ({args.count/elapsed:.1f} samples/sec). File: {out_path.name}")

if __name__ == "__main__":
    main()
