#!/usr/bin/env bash
# ==============================================================================
# Al-Khwarizmi Neuro-Symbolic Math AI - Environment Setup Script
# ==============================================================================

set -e

echo "=== [1/4] Detecting Environment & Python ==="
PYTHON_BIN="/home/ayman/miniforge3/envs/torch-gpu/bin/python"
PIP_BIN="/home/ayman/miniforge3/envs/torch-gpu/bin/pip"

if [ ! -f "$PYTHON_BIN" ]; then
    echo "Using system python..."
    PYTHON_BIN=$(which python3)
    PIP_BIN=$(which pip3)
fi

echo "Python: $($PYTHON_BIN --version)"
echo "PyTorch CUDA Status: $($PYTHON_BIN -c "import torch; print('CUDA Available:', torch.cuda.is_available(), '| Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')")"

echo ""
echo "=== [2/4] Compiling C++ Math Core Shared Library ==="
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"
g++ -O3 -fPIC -shared src/khwarizmi/symbolic/cpp_ext/math_core.cpp -o src/khwarizmi/symbolic/cpp_ext/libmath_core.so
echo "Compiled: src/khwarizmi/symbolic/cpp_ext/libmath_core.so"

echo ""
echo "=== [3/4] Testing Symbolic Engine & C++ Interop ==="
$PYTHON_BIN -c "
import sys; sys.path.insert(0, '$PROJECT_ROOT/src')
from khwarizmi.vision.syntax_guard import is_valid_latex_syntax
from khwarizmi.symbolic.engine import solve_step_by_step
print('Syntax Guard Check:', is_valid_latex_syntax(r'\frac{a}{b} = c'))
steps = solve_step_by_step('2*x + 4 = 10')
print(f'Symbolic Solver Check: {len(steps)} steps generated successfully.')
"

echo ""
echo "=== [4/4] Setup Completed Successfully ==="
echo "To run API Server:"
echo "  $PYTHON_BIN scripts/run_api.py"
echo "To run Flutter App:"
echo "  cd flutter_app && flutter run"
