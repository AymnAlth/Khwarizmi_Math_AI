from __future__ import annotations
import ctypes
import os
import re
from pathlib import Path
from ..config import PROJECT_ROOT

_SO_PATH = PROJECT_ROOT / "src/khwarizmi/symbolic/cpp_ext/libmath_core.so"
_CPP_LIB = None

if _SO_PATH.exists():
    try:
        _CPP_LIB = ctypes.CDLL(str(_SO_PATH))
        _CPP_LIB.khwarizmi_validate_latex_brackets.argtypes = [ctypes.c_char_p]
        _CPP_LIB.khwarizmi_validate_latex_brackets.restype = ctypes.c_int32
        
        _CPP_LIB.khwarizmi_normalize_latex.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int32]
        _CPP_LIB.khwarizmi_normalize_latex.restype = ctypes.c_int32

        _CPP_LIB.khwarizmi_formula_hash.argtypes = [ctypes.c_char_p]
        _CPP_LIB.khwarizmi_formula_hash.restype = ctypes.c_uint64
    except Exception:
        _CPP_LIB = None


def validate_brackets_fast(latex_str: str) -> bool:
    """Fast validation of balanced brackets and braces using C++ or pure Python."""
    if not latex_str or not latex_str.strip():
        return False
        
    if _CPP_LIB is not None:
        return bool(_CPP_LIB.khwarizmi_validate_latex_brackets(latex_str.encode("utf-8")))
    
    # Pure Python fallback
    stack = []
    pairs = {')': '(', '}': '{', ']': '['}
    i = 0
    n = len(latex_str)
    while i < n:
        c = latex_str[i]
        if c == '\\' and i + 1 < n and latex_str[i+1] in '{}[]':
            i += 2
            continue
        if c in '({[':
            stack.append(c)
        elif c in ')}]':
            if not stack or stack[-1] != pairs[c]:
                return False
            stack.pop()
        i += 1
    return len(stack) == 0


def validate_environments(latex_str: str) -> bool:
    """Validate begin/end block consistency."""
    begins = re.findall(r'\\begin\{([a-zA-Z*]+)\}', latex_str)
    ends = re.findall(r'\\end\{([a-zA-Z*]+)\}', latex_str)
    return begins == ends


def is_valid_latex_syntax(latex_str: str) -> bool:
    """Composite LaTeX syntax guard."""
    return validate_brackets_fast(latex_str) and validate_environments(latex_str)


def normalize_latex(latex_str: str) -> str:
    """Normalize whitespace and operators."""
    if not latex_str:
        return ""
    if _CPP_LIB is not None:
        buf = ctypes.create_string_buffer(len(latex_str) * 2 + 128)
        ret = _CPP_LIB.khwarizmi_normalize_latex(latex_str.encode("utf-8"), buf, len(buf))
        if ret > 0:
            return buf.value.decode("utf-8", errors="ignore")
            
    # Python fallback
    s = re.sub(r'\s+', ' ', latex_str).strip()
    s = s.replace('*', r'\cdot ')
    return s


def compute_formula_hash(latex_str: str) -> int:
    """64-bit canonical FNV-1a hash."""
    if _CPP_LIB is not None:
        return int(_CPP_LIB.khwarizmi_formula_hash(latex_str.encode("utf-8")))
    # Python fallback fnv1a
    h = 14695981039346656037
    for b in latex_str.encode("utf-8"):
        if not chr(b).isspace():
            h ^= b
            h = (h * 1099511628211) & 0xFFFFFFFFFFFFFFFF
    return h
