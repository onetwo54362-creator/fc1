import json
import re

with open("page_auth.html", "r", encoding="utf-8") as f:
    html = f.read()

# We need to extract the JSON object containing comment_rendering_instance_for_feed_location
# It's inside a deeply nested script tag. Let's find it.
start_idx = html.find('"comment_rendering_instance_for_feed_location"')
if start_idx != -1:
    # Walk backwards to find the start of the JSON object
    open_braces = 0
    obj_start = -1
    for i in range(start_idx, -1, -1):
        if html[i] == '{':
            open_braces -= 1
        elif html[i] == '}':
            open_braces += 1
            
        # This is a bit fragile for arbitrary JSON, but let's try a regex approach instead
        pass

# Let's just find the edges
edges_matches = re.finditer(r'"edges":(\[.*?\])', html)
for m in edges_matches:
    try:
        edges_str = m.group(1)
        # Try to parse it, it might fail if the regex grabbed too much
        # But we can look for "body":{"text": inside the string
        if '"body":{"text":' in edges_str:
            print("Found comment edges!")
            # Let's extract the text with regex to be safe
            texts = re.findall(r'"body":\{"text":"([^"]+)"\}', edges_str)
            for t in texts:
                print(f"Comment: {t}")
    except:
        pass
