import asyncio
import httpx
from bs4 import BeautifulSoup

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
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
    }
    
    url = "https://mbasic.facebook.com/photo.php?fbid=1532133465628571"
    
    async with httpx.AsyncClient(cookies=cookies, follow_redirects=True) as client:
        resp = await client.get(url, headers=headers)
        
        with open("mbasic_page.html", "w", encoding="utf-8") as f:
            f.write(resp.text)
            
        soup = BeautifulSoup(resp.text, 'html.parser')
        print(f"Status: {resp.status_code}")
        
        # Check for comments
        # In mbasic, comments usually have an id starting with "ufi_" or similar, or they are just divs.
        # Let's search for the author name we saw earlier if we knew it.
        # Let's just print text
        print("Done. Saved to mbasic_page.html")
        
asyncio.run(test())
