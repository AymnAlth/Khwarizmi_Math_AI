from __future__ import annotations
import os
import sys
from pathlib import Path
import torch

def resolve_project_root() -> Path:
    """Dynamically resolve project root across WSL and native Windows."""
    # 1. Environment variable if provided
    if "KHWARIZMI_ROOT" in os.environ:
        return Path(os.environ["KHWARIZMI_ROOT"]).resolve()
    
    # 2. File location resolution
    current = Path(__file__).resolve().parent
    for p in [current, current.parent, current.parent.parent]:
        if (p / "config").exists() and (p / "src").exists():
            return p
            
    # 3. Known WSL default
    wsl_path = Path("/home/ayman/ml-workspace/projects/Khwarizmi_Math_AI")
    if wsl_path.exists():
        return wsl_path
        
    # 4. Known Windows default
    win_path = Path(r"D:\AI\DL\Khwarizmi_Math_AI")
    if win_path.exists():
        return win_path
        
    return current.parent.parent

PROJECT_ROOT = resolve_project_root()
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
ARABIC_SYNTH_DIR = DATA_DIR / "arabic_synth"
GOLDEN_TEST_DIR = DATA_DIR / "golden_test"
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
REPORTS_DIR = PROJECT_ROOT / "reports"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

for directory in [CONFIG_DIR, DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, ARABIC_SYNTH_DIR, GOLDEN_TEST_DIR, ARTIFACTS_DIR, REPORTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Hardware setup
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
USE_AMP = torch.cuda.is_available()
SEED = 42

# Default Ports & Services
API_HOST = "0.0.0.0"
API_PORT = 8000
