"""Debug: inspect the raw GraphQL response for comments to check 
what attachment-related fields exist in the node."""

import asyncio
import json
import httpx

GRAPHQL_URL = "https://www.facebook.com/api/graphql/"
DOC_ID = "25550760954572974"

# Use a post with reactions on comments for testing
FEEDBACK_ID = "ZmVlZGJhY2s6MTUzMjEzMzgzODk2MTg2Nw=="

COOKIES = "datr=zAccakdve75Q5nFvBLD_qM43; sb=zAccakUGljX7HgfycFxMxSer; ps_l=1; ps_n=1; dpr=1.25; c_user=61590573448977; fr=1IUzmkXrksEF9BiE8.AWcCcRMSNdQQNWqFt3K2-RjtP2YTuXOa6joieOrMGf91nkHND-A.BqH_iJ..AAA.0.0.BqH_iJ.AWewOWR9KR880XG0RILrGyY3R4c; xs=34%3A5y1mxEc2d10ryA%3A2%3A1780437903%3A-1%3A-1%3A%3AAcyzCRJduudO0VEzbSnMogf7fcu5yuO7dS8l3_stXIg; presence=C%7B%22t3%22%3A%5B%5D%2C%22utc3%22%3A1780481203085%2C%22v%22%3A1%7D; wd=1146x732"

async def main():
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://www.facebook.com",
        "referer": "https://www.facebook.com/",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "x-fb-friendly-name": "CommentsListComponentsPaginationQuery",
        "cookie": COOKIES,
    }
    
    cursor = None
    count = 0
    found_media = 0
    
    async with httpx.AsyncClient() as client:
        while count < 200:
            variables = {
                "commentsAfterCount": -1,
                "commentsAfterCursor": cursor,
                "commentsIntentToken": "REVERSE_CHRONOLOGICAL_UNFILTERED_INTENT_V1",
                "feedLocation": "DEDICATED_COMMENTING_SURFACE",
                "focusCommentID": None,
                "scale": 2,
                "useDefaultActor": False,
                "id": FEEDBACK_ID,
            }
            
            payload = {
                "variables": json.dumps(variables),
                "doc_id": DOC_ID,
                "fb_api_req_friendly_name": "CommentsListComponentsPaginationQuery",
            }
            
            resp = await client.post(GRAPHQL_URL, data=payload, headers=headers)
            text = resp.text
            
            # Parse FB response
            comments_data = None
            for line in text.split("\n"):
                line = line.strip()
                if line.startswith("for (;;);"):
                    line = line[len("for (;;);"):]
                if not line.startswith("{"):
                    continue
                try:
                    obj = json.loads(line)
                    data = obj.get("data", {})
                    if data and "node" in data:
                        comments_data = data
                        break
                except json.JSONDecodeError:
                    continue
            
            if not comments_data:
                print("No more data.")
                break
                
            comments_block = (comments_data.get("node", {})
                .get("comment_rendering_instance_for_feed_location", {})
                .get("comments", {}))
                
            edges = comments_block.get("edges", [])
            if not edges:
                break
                
            for edge in edges:
                count += 1
                node = edge.get("node", {})
                author = node.get("author", {})
                body = (node.get("body") or {}).get("text", "")
                
                attachments = node.get("attachments", [])
                if attachments:
                    found_media += 1
                    print(f"\n--- Comment {count}: {author.get('name')} ---")
                    print(f"Text: {body[:80]}")
                    print(f"Attachments: {json.dumps(attachments, indent=2, ensure_ascii=False)}")
                    
            cursor = comments_block.get("page_info", {}).get("end_cursor")
            if not cursor:
                break
                
    print(f"\nScanned {count} comments, found {found_media} with attachments.")

asyncio.run(main())
