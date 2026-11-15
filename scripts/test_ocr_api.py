import urllib.request
import io
from PIL import Image, ImageDraw

# Create image with equation
img = Image.new('RGB', (250, 60), color=(255, 255, 255))
d = ImageDraw.Draw(img)
d.text((20, 20), '3x - 9 = 15', fill=(0, 0, 0))

buf = io.BytesIO()
img.save(buf, format='PNG')
img_bytes = buf.getvalue()

boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
body = (
    f'--{boundary}\r\n'
    f'Content-Disposition: form-data; name="file"; filename="test.png"\r\n'
    f'Content-Type: image/png\r\n\r\n'
).encode('utf-8') + img_bytes + f'\r\n--{boundary}--\r\n'.encode('utf-8')

req = urllib.request.Request(
    'http://127.0.0.1:8000/api/v1/ocr',
    data=body,
    headers={'Content-Type': f'multipart/form-data; boundary={boundary}'}
)
try:
    with urllib.request.urlopen(req) as res:
        print('OCR API Status:', res.status)
        print('OCR API Response:', res.read().decode('utf-8'))
except Exception as e:
    print('OCR API Error:', e)
