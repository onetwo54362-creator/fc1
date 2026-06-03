import asyncio
import httpx
import re

async def test():
    url = "https://www.facebook.com/photo?fbid=1532133465628571&set=a.650104283831498"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "cookie": "c_user=61590573448977",
        "accept-language": "en-US,en;q=0.9",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "navigate",
    }
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        resp = await client.get(url, headers=headers)
        
        with open("page.html", "w", encoding="utf-8") as f:
            f.write(resp.text)
            
        print("HTML saved to page.html")
        
        # Let's find any base64 looking string that decodes to 'feedback:'
        import base64
        matches = set(re.findall(r'"([A-Za-z0-9+/=]{20,})"', resp.text))
        for m in matches:
            try:
                decoded = base64.b64decode(m).decode('utf-8')
                if "feedback:" in decoded.lower() or "feedback" in decoded.lower():
                    print(f"Found Base64: {m} -> {decoded}")
            except:
                pass

        # Also search for 'feedback' specifically
        print("\nSearching for 'feedback':")
        # Find 50 chars before and after any occurrence of 'feedback'
        # Since it might be huge, just print the first 5 occurrences
        occurrences = [m.start() for m in re.finditer(r'feedback', resp.text.lower())]
        for idx in occurrences[:5]:
            start = max(0, idx - 50)
            end = min(len(resp.text), idx + 50)
            print(f"Context: {resp.text[start:end]}")
        
asyncio.run(test())
