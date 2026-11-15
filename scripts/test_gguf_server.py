import urllib.request
import json
import time

payload = {
    "messages": [
        {
            "role": "system",
            "content": "أنت \"خوارزمي\" (Al-Khwarizmi Math AI)، معلم رياضي وذكاء اصطناعي استدلالي وتربوي. أجب دائماً باللغة العربية الفصحى فقط. اشرح كل خطوة رياضية بالتفصيل وبساطة خطوة بخطوة."
        },
        {
            "role": "user",
            "content": "المسألة الرياضية: 100 - 25 * 3 + 14\nالمطلوب: حل المسألة مع الشرح التربوي باللغة العربية خطوة بخطوة."
        }
    ],
    "max_tokens": 300,
    "temperature": 0.1
}

t0 = time.time()
req = urllib.request.Request(
    "http://127.0.0.1:8080/v1/chat/completions",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)

with urllib.request.urlopen(req, timeout=15) as resp:
    data = json.loads(resp.read().decode("utf-8"))
    elapsed = round((time.time() - t0) * 1000, 2)
    print(f"[+] Response received in {elapsed} ms:\n")
    print(data["choices"][0]["message"]["content"])
