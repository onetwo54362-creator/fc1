import re
import json

with open("page_auth.html", "r", encoding="utf-8") as f:
    html = f.read()

# Facebook often embeds the GraphQL query map as a JSON object
# It usually looks like: e.exports="123456789" (where e is the module)
# But a better way is just to search for the query names in the HTML.
queries = [
    "CommentsListComponentsPaginationQuery",
    "CometPhotoRootQuery",
    "CometMediaRootQuery",
    "Depth1CommentsListPaginationQuery",
    "CometUFICommentsProviderQuery"
]

for q in queries:
    idx = html.find(q)
    if idx != -1:
        print(f"\nFound {q}!")
        # Find the doc_id associated with it. It might be nearby.
        context = html[max(0, idx-100):min(len(html), idx+200)]
        print(context)
        
        # Let's try to find a sequence of numbers (doc_id) near it
        # Actually, sometimes it's literally: id:"123456789",metadata:{},name:"CommentsListComponentsPaginationQuery"
        match = re.search(r'id:"(\d+)",metadata:.*?name:"' + q + r'"', html)
        if match:
            print(f"  Exact doc_id match: {match.group(1)}")
        else:
            match = re.search(r'name:"' + q + r'".*?id:"(\d+)"', html)
            if match:
                print(f"  Exact doc_id match (reverse): {match.group(1)}")
