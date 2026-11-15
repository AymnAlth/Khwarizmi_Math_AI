from __future__ import annotations
import sys
import uvicorn
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "src"))

from khwarizmi.config import API_HOST, API_PORT

if __name__ == "__main__":
    print(f"=== Starting Al-Khwarizmi Math AI API ===")
    print(f"Listening on http://{API_HOST}:{API_PORT}")
    print(f"Interactive Docs: http://localhost:{API_PORT}/docs")
    uvicorn.run("khwarizmi.api.app:app", host="0.0.0.0", port=API_PORT, reload=True, reload_dirs=[str(_ROOT / "src")])
