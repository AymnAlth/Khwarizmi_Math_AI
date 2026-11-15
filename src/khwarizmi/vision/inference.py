from __future__ import annotations
import io
from pathlib import Path
from typing import Union, Dict, Any
from PIL import Image
from torchvision import transforms
from .encoder_decoder import VisionToLatexModel
from .syntax_guard import is_valid_latex_syntax, normalize_latex

_GLOBAL_OCR_MODEL: VisionToLatexModel | None = None

def get_ocr_model() -> VisionToLatexModel:
    global _GLOBAL_OCR_MODEL
    if _GLOBAL_OCR_MODEL is None:
        _GLOBAL_OCR_MODEL = VisionToLatexModel()
    return _GLOBAL_OCR_MODEL


def recognize_latex_from_image(image_input: Union[str, Path, bytes, Image.Image]) -> Dict[str, Any]:
    """Extracts LaTeX mathematical formula from image with syntax guard validation."""
    if isinstance(image_input, (str, Path)):
        img = Image.open(image_input).convert("RGB")
    elif isinstance(image_input, bytes):
        img = Image.open(io.BytesIO(image_input)).convert("RGB")
    elif isinstance(image_input, Image.Image):
        img = image_input.convert("RGB")
    else:
        raise ValueError("Unsupported image input type.")

    model = get_ocr_model()
    if model.processor is not None:
        pixel_tensor = model.processor(img, return_tensors="pt").pixel_values
    else:
        tf = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        pixel_tensor = tf(img).unsqueeze(0)

    latex, conf = model.decode_with_syntax_guard(pixel_tensor)
    valid = is_valid_latex_syntax(latex)

    return {
        "latex": latex,
        "confidence": conf,
        "is_syntax_valid": valid
    }
