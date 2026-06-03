import re

with open("page_auth.html", "r", encoding="utf-8") as f:
    html = f.read()

# Look for queryID, server_req, etc.
matches = re.finditer(r'(query_id|queryID|doc_id|docId)["\']?\s*:\s*["\']?(\d+)', html, re.IGNORECASE)
qids = set(m.group(2) for m in matches)
print(f"Found IDs: {qids}")

# Let's print the context for each
for qid in qids:
    idx = html.find(qid)
    if idx != -1:
        print(f"\n--- Context for {qid} ---")
        print(html[max(0, idx-100):min(len(html), idx+200)])
