from __future__ import annotations
import sys
import json
import argparse
from pathlib import Path
from datasets import load_dataset

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "src"))

from khwarizmi.config import RAW_DATA_DIR, REPORTS_DIR
from khwarizmi.vision.syntax_guard import is_valid_latex_syntax, normalize_latex

SOURCES = {
    "numina_math": {
        "repo_id": "AI-MO/NuminaMath-CoT",
        "split": "train",
        "description": "860k CoT Mathematical Reasoning Dataset"
    },
    "prm800k": {
        "repo_id": "tasksource/PRM800K",
        "split": "train",
        "description": "OpenAI Process Supervision (Step-Level Reward) Dataset"
    },
    "im2latex": {
        "repo_id": "yuntian-deng/im2latex-100k",
        "split": "train",
        "description": "100k Printed Mathematical Formulas to LaTeX"
    }
}


def download_and_sample_dataset(name: str, repo_id: str, split: str, sample_size: int = 50):
    print(f"\n--- Loading {name} ({repo_id}) [Streaming mode] ---")
    out_file = RAW_DATA_DIR / f"{name}_sample.jsonl"
    
    try:
        ds = load_dataset(repo_id, split=split, streaming=True)
        records = []
        valid_latex_count = 0
        
        for i, item in enumerate(ds):
            if i >= sample_size:
                break
                
            clean_item = {}
            for k, v in item.items():
                if isinstance(v, (str, int, float, bool, list, dict)):
                    clean_item[k] = v
                else:
                    clean_item[k] = str(v)
                    
            records.append(clean_item)
            
        with open(out_file, 'w', encoding='utf-8') as f:
            for r in records:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
                
        print(f"Saved {len(records)} samples to {out_file}")
        return len(records)
    except Exception as exc:
        print(f"Error loading {name}: {exc}")
        return 0


def main():
    parser = argparse.ArgumentParser(description="Download and verify dataset streams")
    parser.add_argument("--samples", type=int, default=100, help="Number of samples per source to fetch")
    args = parser.parse_args()
    
    print("=== Al-Khwarizmi Quad-Source Data Pipeline Ingestion ===")
    manifest = {}
    for name, meta in SOURCES.items():
        count = download_and_sample_dataset(name, meta["repo_id"], meta["split"], args.samples)
        manifest[name] = {
            "repo_id": meta["repo_id"],
            "description": meta["description"],
            "sample_count": count,
            "status": "ACCESSIBLE" if count > 0 else "FAILED"
        }
        
    manifest_path = REPORTS_DIR / "data_sources_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"\nSaved Data Sourcing Manifest to: {manifest_path}")

if __name__ == "__main__":
    main()
