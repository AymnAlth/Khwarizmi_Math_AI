from __future__ import annotations
import io
import re
from pathlib import Path
from typing import Union, Dict, Any
import numpy as np
from PIL import Image, ImageOps, ImageEnhance
import torch

try:
    import easyocr
    _HAS_EASYOCR = True
except ImportError:
    _HAS_EASYOCR = False

from .syntax_guard import is_valid_latex_syntax, normalize_latex

_EASYOCR_READER = None


def get_easyocr_reader():
    global _EASYOCR_READER
    if _EASYOCR_READER is None and _HAS_EASYOCR:
        use_gpu = torch.cuda.is_available()
        _EASYOCR_READER = easyocr.Reader(['en'], gpu=use_gpu)
    return _EASYOCR_READER


def clean_ocr_to_math(raw_text: str) -> str:
    """Cleans up raw OCR recognized text into a clean mathematical expression."""
    text = raw_text.strip()
    if not text:
        return ""

    # Replace common unicode math symbols with standard ASCII/LaTeX
    text = text.replace('×', '*').replace('÷', '/').replace('·', '*').replace('•', '*')
    text = text.replace('—', '-').replace('–', '-').replace('−', '-')
    text = text.replace('²', '^2').replace('³', '^3')

    # Fractions: e.g. 4 / 2 -> 4/2
    text = re.sub(r'(\d)\s*/\s*(\d)', r'\1/\2', text)
    
    # Clean up accidental OCR misidentifications
    # Common digit misidentifications in math: e.g. 'O' or 'o' between numbers -> '0'
    text = re.sub(r'(?<=\d)[Oo](?=\d)', '0', text)

    # Normalize variable multiplication: e.g. 3 x -> 3x
    text = re.sub(r'(\d)\s+([a-zA-Z])\b', r'\1\2', text)

    # Normalize operator spacing
    text = re.sub(r'\s*([=+\-*/])\s*', r' \1 ', text)
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def recognize_latex_from_image(image_input: Union[str, Path, bytes, Image.Image]) -> Dict[str, Any]:
    """Extracts mathematical formula from image using EasyOCR with contrast and inversion preprocessing."""
    if isinstance(image_input, (str, Path)):
        img = Image.open(image_input).convert("RGB")
    elif isinstance(image_input, bytes):
        img = Image.open(io.BytesIO(image_input)).convert("RGB")
    elif isinstance(image_input, Image.Image):
        img = image_input.convert("RGB")
    else:
        raise ValueError("Unsupported image input type.")

    # 1. Image Preprocessing: Handle chalkboard images (dark background, light drawing)
    gray = img.convert('L')
    mean_val = float(np.mean(gray))
    if mean_val < 110:
        # Dark background (chalkboard) -> Invert to black text on white background
        processed_img = ImageOps.invert(img)
    else:
        processed_img = img

    # 2. Enhance contrast to make strokes crisp
    enhancer = ImageEnhance.Contrast(processed_img)
    processed_img = enhancer.enhance(1.8)

    # 3. OCR Extraction
    reader = get_easyocr_reader()
    detected_lines = []
    conf = 0.90

    if reader is not None:
        arr = np.array(processed_img)
        # Read text blocks
        results = reader.readtext(arr, detail=1)
        for bbox, text, score in results:
            clean_token = text.strip()
            if clean_token:
                detected_lines.append(clean_token)
                conf = max(conf, float(score))

    raw_joined = " ".join(detected_lines)
    cleaned_math = clean_ocr_to_math(raw_joined)

    if not cleaned_math:
        return {
            "latex": "",
            "confidence": 0.0,
            "is_syntax_valid": False,
        }

    return {
        "latex": cleaned_math,
        "confidence": round(conf, 2),
        "is_syntax_valid": is_valid_latex_syntax(cleaned_math)
    }
