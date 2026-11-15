from __future__ import annotations
import sys
import time
import argparse
from pathlib import Path

# Add src to path
_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "src"))

from khwarizmi.config import ARABIC_SYNTH_DIR
from khwarizmi.reasoning.generator import HybridArabicMathGenerator

def main():
    parser = argparse.ArgumentParser(description="Al-Khwarizmi Hybrid Arabic Math Dataset Generator")
    parser.add_argument("--count", type=int, default=1000, help="Number of verified problems to generate")
    parser.add_argument("--output", type=str, default=str(ARABIC_SYNTH_DIR / "arabic_math_dataset.jsonl"))
    args = parser.parse_args()

    print(f"=== Starting Hybrid Arabic Math Dataset Generation ===")
    print(f"Target count: {args.count:,} problems")
    print(f"Output path:  {args.output}")

    gen = HybridArabicMathGenerator(seed=42)
    t0 = time.time()
    out_file = gen.export_to_jsonl(args.count, Path(args.output))
    elapsed = time.time() - t0

    print(f"Successfully generated {args.count:,} mathematically verified problems.")
    print(f"File size: {out_file.stat().st_size / (1024*1024):.2f} MB")
    print(f"Time taken: {elapsed:.2f} seconds ({args.count / elapsed:.1f} samples/sec)")

if __name__ == "__main__":
    main()
