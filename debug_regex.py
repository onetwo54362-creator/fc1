import re

with open("page_auth.html", "r", encoding="utf-8") as f:
    html = f.read()

patterns = [
    r'"feedback_id":"(ZmVlZGJh[^"]+)"',
    r'"feedback":\{"id":"(ZmVlZGJh[^"]+)"',
    r'"target_feedback":\{"id":"(ZmVlZGJh[^"]+)"',
    r'"feedback_target_with_context":\{"feedback_id":"(ZmVlZGJh[^"]+)"'
]

for p in patterns:
    matches = re.findall(p, html)
    print(f"Pattern {p}: {matches}")
