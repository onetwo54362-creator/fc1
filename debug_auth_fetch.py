import asyncio
import httpx
import re

async def test():
    url = "https://www.facebook.com/photo?fbid=1532133465628571&set=a.650104283831498"
    
    # User's provided cookies from their message
    cookie_str = """datr=zAccakdve75Q5nFvBLD_qM43; sb=zAccakUGljX7HgfycFxMxSer; ps_l=1; ps_n=1; dpr=1.25; c_user=61590573448977; fr=1sT2Cn7a80S0s37Ky.AWfIEGQKZNaHxhe1jXQPXiIBGtwIg9C2ms26qCmE9AE0OAckfSU.BqH_iJ..AAA.0.0.BqH_iJ.AWewOWR9KR880XG0RILrGyY3R4c; xs=34%3A5y1mxEc2d10ryA%3A2%3A1780437903%3A-1%3A-1%3A%3AAcyzCRJduudO0VEzbSnMogf7fcu5yuO7dS8l3_stXIg; presence=C%7B%22t3%22%3A%5B%5D%2C%22utc3%22%3A1780481203085%2C%22v%22%3A1%7D; wd=1146x732"""
    
    cookies = {}
    for part in cookie_str.split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            cookies[k.strip()] = v.strip()

    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "accept-language": "en-US,en;q=0.9",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    }
    
    async with httpx.AsyncClient(cookies=cookies, follow_redirects=True) as client:
        resp = await client.get(url, headers=headers)
        print(f"Status: {resp.status_code}")
        
        with open("page_auth.html", "w", encoding="utf-8") as f:
            f.write(resp.text)
            
        print("HTML saved to page_auth.html")
        
        # Test the regexes
        patterns = [
            r'"feedback_id":"(ZmVlZGJh[^"]+)"',
            r'"feedback":\{"id":"(ZmVlZGJh[^"]+)"',
            r'"target_feedback":\{"id":"(ZmVlZGJh[^"]+)"',
            r'"feedback_target_with_context":\{"feedback_id":"(ZmVlZGJh[^"]+)"',
            r'"feedback":\{"id":"([^"]+)"',
            r'"feedback_id":"([^"]+)"'
        ]
        
        for p in patterns:
            match = re.search(p, resp.text)
            if match:
                print(f"Match for {p}: {match.group(1)}")

asyncio.run(test())
