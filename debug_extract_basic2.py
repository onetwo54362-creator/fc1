import re
import json

with open("test_page.html", "r", encoding="utf-8") as f:
    html = f.read()

# find {"name":"..."} and print context
matches = re.finditer(r'\{"name":"([^"]+)"', html)
for i, m in enumerate(matches):
    if i > 20: break
    start = max(0, m.start() - 50)
    end = min(len(html), m.end() + 50)
    print(f"Match {i+1}: {m.group(1)} | Context: {html[start:end]}")

