import json
import re

def extract_comments_from_html(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    comments = []
    
    # Facebook uses <script type="application/json" ...> to store relay state
    # We can find all JSON objects in the HTML using a simple regex for script tags
    scripts = re.findall(r'<script type="application/json".*?>(.*?)</script>', html)
    
    def search_dict(d):
        if isinstance(d, dict):
            # Look for comment edges
            if "comment_rendering_instance_for_feed_location" in d:
                try:
                    edges = d["comment_rendering_instance_for_feed_location"]["comments"]["edges"]
                    for e in edges:
                        node = e.get("node", {})
                        if node and "body" in node:
                            text = node["body"].get("text", "")
                            author = node.get("author", {}).get("name", "")
                            if text:
                                comments.append(f"{author}: {text}")
                except Exception as ex:
                    pass
            for v in d.values():
                search_dict(v)
        elif isinstance(d, list):
            for v in d:
                search_dict(v)

    for s in scripts:
        try:
            data = json.loads(s)
            search_dict(data)
        except:
            pass

    print(f"Extracted {len(comments)} comments from HTML!")
    for i, c in enumerate(comments):
        print(f" {i+1}. {c}")

extract_comments_from_html("page_auth.html")
