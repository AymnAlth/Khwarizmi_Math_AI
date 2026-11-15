import io
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "src"))

from khwarizmi.vision.inference import recognize_latex_from_image

def test_drawing():
    # 1. Dark canvas simulation (HandwritingCanvasDialog)
    img = Image.new('RGB', (800, 520), color=(10, 12, 18))
    draw = ImageDraw.Draw(img)
    pen_color = (96, 165, 250)
    stroke_w = 7

    # Draw '4'
    draw.line([(250, 150), (200, 300), (320, 300)], fill=pen_color, width=stroke_w)
    draw.line([(280, 200), (280, 380)], fill=pen_color, width=stroke_w)

    # Draw '/'
    draw.line([(400, 140), (350, 400)], fill=pen_color, width=stroke_w)

    # Draw '2'
    draw.arc([(440, 150), (540, 260)], 180, 360, fill=pen_color, width=stroke_w)
    draw.line([(540, 205), (440, 370), (550, 370)], fill=pen_color, width=stroke_w)

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    res = recognize_latex_from_image(buf.getvalue())
    print("Result for drawn strokes 4/2:", res)

    # 2. Text image (e.g. from photo / printed / clean text)
    from PIL import ImageFont
    img2 = Image.new('RGB', (500, 200), color=(255, 255, 255))
    d2 = ImageDraw.Draw(img2)
    # Default font or large text
    d2.text((150, 60), "4 / 2", fill=(0, 0, 0))
    buf2 = io.BytesIO()
    img2.save(buf2, format='PNG')
    res2 = recognize_latex_from_image(buf2.getvalue())
    print("Result for printed 4 / 2:", res2)

    # 3. Another equation: 2x + 5 = 15
    img3 = Image.new('RGB', (600, 200), color=(255, 255, 255))
    d3 = ImageDraw.Draw(img3)
    d3.text((100, 60), "2x + 5 = 15", fill=(0, 0, 0))
    buf3 = io.BytesIO()
    img3.save(buf3, format='PNG')
    res3 = recognize_latex_from_image(buf3.getvalue())
    print("Result for 2x + 5 = 15:", res3)

if __name__ == "__main__":
    test_drawing()
