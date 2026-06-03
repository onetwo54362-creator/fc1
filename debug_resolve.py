import asyncio
import logging
from src.graphql_engine import GraphQLEngine

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

async def test():
    cookie_str = """datr=zAccakdve75Q5nFvBLD_qM43; sb=zAccakUGljX7HgfycFxMxSer; ps_l=1; ps_n=1; dpr=1.25; c_user=61590573448977; fr=1sT2Cn7a80S0s37Ky.AWfIEGQKZNaHxhe1jXQPXiIBGtwIg9C2ms26qCmE9AE0OAckfSU.BqH_iJ..AAA.0.0.BqH_iJ.AWewOWR9KR880XG0RILrGyY3R4c; xs=34%3A5y1mxEc2d10ryA%3A2%3A1780437903%3A-1%3A-1%3A%3AAcyzCRJduudO0VEzbSnMogf7fcu5yuO7dS8l3_stXIg; presence=C%7B%22t3%22%3A%5B%5D%2C%22utc3%22%3A1780481203085%2C%22v%22%3A1%7D; wd=1146x732"""
    
    cookies = {}
    for part in cookie_str.split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            cookies[k.strip()] = v.strip()

    engine = GraphQLEngine(cookies=cookies, fb_dtsg="")
    
    # We will test JUST resolve_post_id and print matches
    post_url = "https://www.facebook.com/photo?fbid=1532133465628571&set=a.650104283831498"
    
    import re
    import base64
    
    headers = engine._client.headers.copy()
    headers.update({
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
    })
    
    response = await engine._client.get(post_url, headers=headers)
    
    patterns = [
        r'"feedback_id":"(ZmVlZGJh[^"]+)"',
        r'"feedback":\{"id":"(ZmVlZGJh[^"]+)"',
        r'"target_feedback":\{"id":"(ZmVlZGJh[^"]+)"',
        r'"feedback_target_with_context":\{"feedback_id":"(ZmVlZGJh[^"]+)"'
    ]
    
    found = False
    for p in patterns:
        matches = re.findall(p, response.text)
        print(f"Pattern {p} found matches: {len(matches)}")
        for m in matches:
            try:
                decoded = base64.b64decode(m).decode('utf-8')
                print(f"Decoded: {decoded}")
                if "feedback:" in decoded and "_" not in decoded:
                    print(f"WINNER: {m}")
                    found = True
                    break
            except Exception as e:
                print(f"Decode error: {e}")
        if found: break
        
    await engine.close()

asyncio.run(test())
