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
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
        "accept-language": "en-US,en;q=0.9",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
    }
    
    url = "https://m.facebook.com/photo.php?fbid=1532133465628571&set=a.650104283831498"
    
    async with httpx.AsyncClient(cookies=cookies, follow_redirects=True) as client:
        resp = await client.get(url, headers=headers)
        
        with open("m_page.html", "w", encoding="utf-8") as f:
            f.write(resp.text)
            
        soup = BeautifulSoup(resp.text, 'html.parser')
        print(f"Status: {resp.status_code}")
        
        # In m.facebook.com, comments usually have class names or specific structures
        # Let's just find the text "comments" or look for all divs with text
        comments_section = soup.find_all('div', string=lambda text: text and 'View more comments' in text)
        print(f"Found 'View more comments' buttons: {len(comments_section)}")
        
        # Let's try to extract basic comments
        # Often comments have a specific nested div structure.
        # Just search for common comment strings or user names.
        all_text = soup.get_text(separator=' | ', strip=True)
        print(f"Text snippet: {all_text[500:1000]}")
        
asyncio.run(test())
