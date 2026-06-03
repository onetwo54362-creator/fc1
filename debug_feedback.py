import asyncio
import httpx
import base64
import json

async def test():
    fbid = "1532133465628571"
    b64_fbid = base64.b64encode(f(f"feedback:{fbid}").encode('utf-8')).decode('utf-8')
    print(f"Encoded feedback id: {b64_fbid}")

asyncio.run(test())
