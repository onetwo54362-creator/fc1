import re
import json

with open("test_page.html", "r", encoding="utf-8") as f:
    html = f.read()

author = None
author_match = re.search(r'"actors":\[\{"__typename":"(?:User|Page)","id":"\d+","name":"([^"]+)"', html)
if not author_match:
    author_match = re.search(r'"owning_profile":\{"__typename":"(?:User|Page)","id":"\d+","name":"([^"]+)"', html)
if author_match:
    author = author_match.group(1)
    print(f"Author found: {author}")
else:
    print("Author not found")

text = None
text_match = re.search(r'"message":\{"text":"([^"]+)"\}', html)
if text_match:
    # Unescape JSON string
    try:
        text = json.loads(f'"{text_match.group(1)}"')
    except:
        text = text_match.group(1)
    print(f"Text found: {text}")
else:
    print("Text not found")
