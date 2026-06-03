import re
import json

with open("page_auth.html", "r", encoding="utf-8") as f:
    html = f.read()

print("Searching for doc_id...")
matches = re.finditer(r'"doc_id":"(\d+)"', html)
doc_ids = set(m.group(1) for m in matches)
print(f"Found {len(doc_ids)} unique doc_ids.")

print("\nSearching for comment related queries...")
queries = ["Comment", "Feedback", "CometPhoto", "Media"]
for q in queries:
    occurrences = [m.start() for m in re.finditer(q, html, re.IGNORECASE)]
    print(f"Found {len(occurrences)} occurrences of '{q}'")

# Look at the Relay preload data for the initial comments
idx = html.find('comment_rendering_instance_for_feed_location')
if idx != -1:
    print("\nFound comment_rendering_instance_for_feed_location!")
    context = html[max(0, idx-200):min(len(html), idx+200)]
    print(context)
else:
    print("\nNo initial comments found in HTML.")
