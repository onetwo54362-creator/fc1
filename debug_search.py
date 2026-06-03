import asyncio
import httpx
import re

async def test():
    with open("page.html", "r", encoding="utf-8") as f:
        html = f.read()
        
    print(f"HTML size: {len(html)}")
    
    # Let's search for the ID 1532133465628571
    target = "1532133465628571"
    
    print("\nSearching for the target ID context:")
    occurrences = [m.start() for m in re.finditer(target, html)]
    for idx in occurrences[:10]:
        start = max(0, idx - 100)
        end = min(len(html), idx + 100)
        print(f"Context: {html[start:end]}")

asyncio.run(test())
