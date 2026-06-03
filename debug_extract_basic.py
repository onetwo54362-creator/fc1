import json
import re
import base64

with open("test_page.html", "r", encoding="utf-8") as f:
    html = f.read()

# Let's see if we can find author name and text easily via standard meta tags or regex
title_match = re.search(r'<title>(.*?)</title>', html)
print(f"Title: {title_match.group(1) if title_match else None}")

# Find author name
author_patterns = [
    r'"author":\{"name":"([^"]+)"',
    r'"actors":\[\{"name":"([^"]+)"',
    r'"name":"([^"]+)"'
]
for p in author_patterns:
    matches = re.findall(p, html)
    if matches:
        print(f"Author pattern {p} found: {matches[:3]}")

# Find post text
text_patterns = [
    r'"message":\{"text":"([^"]+)"\}',
    r'"message":"([^"]+)"'
]
for p in text_patterns:
    matches = re.findall(p, html)
    if matches:
        print(f"Text pattern {p} found: {matches[:3]}")

