import re
import base64

with open("page_auth.html", "r", encoding="utf-8") as f:
    html = f.read()

print(f"Total HTML length: {len(html)}")

# Find all unique ZmVlZGJh matches
matches = set(re.findall(r'"id":"(ZmVlZGJh[^"]+)"', html))
matches.update(re.findall(r'"feedback_id":"(ZmVlZGJh[^"]+)"', html))

print(f"Found {len(matches)} unique feedback IDs:")
for m in matches:
    decoded = base64.b64decode(m).decode('utf-8')
    print(f"  {m} -> {decoded}")

# Let's find what is associated with the actual photo ID
photo_id = "1532133465628571"
idx = html.find(photo_id)
if idx != -1:
    context = html[max(0, idx-200):min(len(html), idx+500)]
    print(f"\nContext around photo ID:\n{context}")
