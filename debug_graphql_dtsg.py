import asyncio
import httpx
import json
import re

async def test():
    cookie_str = """datr=zAccakdve75Q5nFvBLD_qM43; sb=zAccakUGljX7HgfycFxMxSer; ps_l=1; ps_n=1; dpr=1.25; c_user=61590573448977; fr=1sT2Cn7a80S0s37Ky.AWfIEGQKZNaHxhe1jXQPXiIBGtwIg9C2ms26qCmE9AE0OAckfSU.BqH_iJ..AAA.0.0.BqH_iJ.AWewOWR9KR880XG0RILrGyY3R4c; xs=34%3A5y1mxEc2d10ryA%3A2%3A1780437903%3A-1%3A-1%3A%3AAcyzCRJduudO0VEzbSnMogf7fcu5yuO7dS8l3_stXIg; presence=C%7B%22t3%22%3A%5B%5D%2C%22utc3%22%3A1780481203085%2C%22v%22%3A1%7D; wd=1146x732"""
    
    cookies = {}
    for part in cookie_str.split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            cookies[k.strip()] = v.strip()

    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://www.facebook.com",
    }
    
    # 1. Fetch fb_dtsg
    with open("page_auth.html", "r", encoding="utf-8") as f:
        html = f.read()
    
    fb_dtsg = ""
    match = re.search(r'"fb_dtsg":"([^"]+)"', html)
    if match:
        fb_dtsg = match.group(1)
        print(f"Found fb_dtsg: {fb_dtsg[:10]}...")
    else:
        # Sometimes it's inside hidden input
        match = re.search(r'name="fb_dtsg" value="([^"]+)"', html)
        if match:
            fb_dtsg = match.group(1)
            print(f"Found fb_dtsg (input): {fb_dtsg[:10]}...")
    
    if not fb_dtsg:
        print("Could not find fb_dtsg!")
        return
        
    true_fbid = "ZmVlZGJhY2s6MTUzMjEzMzgzODk2MTg2Nw==" # feedback:1532133838961867
    
    async with httpx.AsyncClient(cookies=cookies) as client:
        variables = {
            "commentsAfterCount": -1,
            "commentsAfterCursor": None,
            "commentsIntentToken": "RANKED_UNFILTERED_INTENT_V1",
            "feedLocation": "DEDICATED_COMMENTING_SURFACE",
            "focusCommentID": None,
            "scale": 1,
            "useDefaultActor": False,
            "id": true_fbid,
        }
        
        payload = {
            "av": "61590573448977",
            "__user": "61590573448977",
            "__a": "1",
            "fb_dtsg": fb_dtsg,
            "doc_id": "25550760954572974", 
            "variables": json.dumps(variables)
        }
        
        resp = await client.post("https://www.facebook.com/api/graphql/", data=payload, headers=headers)
        data = resp.text.split("\n")[0]
        if "for (;;);" in data:
            data = data.replace("for (;;);", "")
        js = json.loads(data)
        
        edges = js.get("data",{}).get("node",{}).get("comment_rendering_instance_for_feed_location",{}).get("comments",{}).get("edges",[])
        print(f"Edges found: {len(edges)}")
        if edges:
            print(f"  First comment: {edges[0]['node']['body']['text']}")
        else:
            print(f"Full response: {json.dumps(js)[:500]}")

asyncio.run(test())
