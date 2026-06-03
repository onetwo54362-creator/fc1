import re
import httpx
import asyncio

async def test():
    with open("page_auth.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Find all JS files
    js_urls = re.findall(r'src="(https://static[^"]+\.js\?[^"]+)"', html)
    print(f"Found {len(js_urls)} JS files.")
    
    # We only need to search them
    # To speed up, we can use an AsyncClient to fetch them concurrently
    async with httpx.AsyncClient(timeout=30) as client:
        async def fetch_and_search(url):
            try:
                resp = await client.get(url)
                if "CommentsListComponentsPaginationQuery" in resp.text:
                    print(f"\nFound CommentsListComponentsPaginationQuery in {url}!")
                    # Find doc_id
                    match = re.search(r'id:"(\d+)",metadata:.*?name:"CommentsListComponentsPaginationQuery"', resp.text)
                    if match:
                        print(f"  -> Exact doc_id: {match.group(1)}")
                    else:
                        match = re.search(r'name:"CommentsListComponentsPaginationQuery".*?id:"(\d+)"', resp.text)
                        if match:
                            print(f"  -> Exact doc_id (reverse): {match.group(1)}")
                            
                if "Depth1CommentsListPaginationQuery" in resp.text:
                    print(f"\nFound Depth1CommentsListPaginationQuery in {url}!")
                    # Find doc_id
                    match = re.search(r'id:"(\d+)",metadata:.*?name:"Depth1CommentsListPaginationQuery"', resp.text)
                    if match:
                        print(f"  -> Exact doc_id: {match.group(1)}")
                    else:
                        match = re.search(r'name:"Depth1CommentsListPaginationQuery".*?id:"(\d+)"', resp.text)
                        if match:
                            print(f"  -> Exact doc_id (reverse): {match.group(1)}")
                            
            except Exception as e:
                pass
                
        # Batch requests
        batch_size = 10
        for i in range(0, len(js_urls), batch_size):
            batch = js_urls[i:i+batch_size]
            await asyncio.gather(*(fetch_and_search(u) for u in batch))

asyncio.run(test())
