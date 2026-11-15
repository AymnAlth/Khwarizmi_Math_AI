from __future__ import annotations
import random
import math
from typing import Tuple, Optional
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance
import torch
from torch.utils.data import Dataset
from torchvision import transforms

class PhoneCameraMathAugmenter:
    """Robust augmentations simulating real smartphone cameras:

    1. Lined/ruled paper simulation (دفتر مسطر)
    2. Cast shadow simulation (ظل اليد أو الهاتف)
    3. Slanted rotation & perspective distortion (+- 15 degrees)
    4. Lighting drop and blur
    """

    def __init__(self, p_ruled: float = 0.4, p_shadow: float = 0.4, max_angle: float = 15.0):
        self.p_ruled = p_ruled
        self.p_shadow = p_shadow
        self.max_angle = max_angle

    def apply_ruled_paper(self, img: Image.Image) -> Image.Image:
        """Draw faint horizontal ruled notebook lines."""
        if random.random() > self.p_ruled:
            return img
            
        img = img.convert("RGBA")
        overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)
        
        spacing = random.randint(24, 40)
        line_color = (180, 200, 220, random.randint(35, 75)) # Faint blue notebook line
        
        for y in range(spacing, img.height, spacing):
            draw.line([(0, y), (img.width, y)], fill=line_color, width=1)
            
        out = Image.alpha_composite(img, overlay)
        return out.convert("RGB")

    def apply_shadow(self, img: Image.Image) -> Image.Image:
        """Simulate phone or hand shadow falling diagonally across the formula."""
        if random.random() > self.p_shadow:
            return img
            
        arr = np.array(img).astype(np.float32)
        h, w = arr.shape[:2]
        
        # Linear gradient shadow mask
        x_coords = np.linspace(0, 1, w)
        y_coords = np.linspace(0, 1, h)
        xv, yv = np.meshgrid(x_coords, y_coords)
        
        angle = random.uniform(0, 2 * math.pi)
        grad = xv * math.cos(angle) + yv * math.sin(angle)
        grad = (grad - grad.min()) / (grad.max() - grad.min() + 1e-6)
        
        shadow_intensity = random.uniform(0.35, 0.70)
        mask = 1.0 - (grad * shadow_intensity)
        mask = np.expand_dims(mask, axis=-1)
        
        arr = np.clip(arr * mask, 0, 255).astype(np.uint8)
        return Image.fromarray(arr)

    def __call__(self, img: Image.Image) -> Image.Image:
        # 1. Geometry: Slanted angle (-15 to +15 deg)
        angle = random.uniform(-self.max_angle, self.max_angle)
        img = img.rotate(angle, resample=Image.BICUBIC, expand=False, fillcolor=(255, 255, 255))
        
        # 2. Ruled paper
        img = self.apply_ruled_paper(img)
        
        # 3. Phone shadow
        img = self.apply_shadow(img)
        
        # 4. Color jitter (contrast/brightness)
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(random.uniform(0.8, 1.2))
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(random.uniform(0.8, 1.2))
        
        return img


class MathFormulaDataset(Dataset):
    """Dataset loader for Im2LaTeX / HME100K formula image pairs."""

    def __init__(self, records: list, tokenizer=None, image_size: Tuple[int, int] = (224, 224), is_train: bool = True):
        self.records = records
        self.tokenizer = tokenizer
        self.image_size = image_size
        self.is_train = is_train
        self.augmenter = PhoneCameraMathAugmenter() if is_train else None
        
        self.tensor_transform = transforms.Compose([
            transforms.Resize(image_size),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def __len__(self) -> int:
        return len(self.records)

    def __getitem__(self, idx: int) -> dict:
        item = self.records[idx]
        image_path = item.get("image_path")
        latex_str = item.get("latex", "")
        
        if image_path:
            img = Image.open(image_path).convert("RGB")
        else:
            # Synthetic placeholder rendering for demonstration
            img = Image.new("RGB", (256, 96), color=(255, 255, 255))
            draw = ImageDraw.Draw(img)
            draw.text((10, 30), latex_str[:25], fill=(0, 0, 0))
            
        if self.augmenter:
            img = self.augmenter(img)
            
        pixel_values = self.tensor_transform(img)
        
        result = {"pixel_values": pixel_values, "latex": latex_str}
        if self.tokenizer:
            labels = self.tokenizer(latex_str, padding="max_length", max_length=128, truncation=True, return_tensors="pt").input_ids
            result["labels"] = labels.squeeze(0)
            
        return result
