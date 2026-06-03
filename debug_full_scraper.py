import asyncio
import logging
from src.graphql_engine import GraphQLEngine
from src.comment_scraper import CommentScraper
from src.rate_limiter import RateLimiter

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

async def test():
    cookie_str = """datr=zAccakdve75Q5nFvBLD_qM43; sb=zAccakUGljX7HgfycFxMxSer; ps_l=1; ps_n=1; dpr=1.25; c_user=61590573448977; fr=1sT2Cn7a80S0s37Ky.AWfIEGQKZNaHxhe1jXQPXiIBGtwIg9C2ms26qCmE9AE0OAckfSU.BqH_iJ..AAA.0.0.BqH_iJ.AWewOWR9KR880XG0RILrGyY3R4c; xs=34%3A5y1mxEc2d10ryA%3A2%3A1780437903%3A-1%3A-1%3A%3AAcyzCRJduudO0VEzbSnMogf7fcu5yuO7dS8l3_stXIg; presence=C%7B%22t3%22%3A%5B%5D%2C%22utc3%22%3A1780481203085%2C%22v%22%3A1%7D; wd=1146x732"""
    
    cookies = {}
    for part in cookie_str.split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            cookies[k.strip()] = v.strip()

    engine = GraphQLEngine(cookies=cookies, fb_dtsg="")
    
    print("Auto-fetching fb_dtsg...")
    await engine.auto_fetch_fb_dtsg()
    
    print("Resolving post ID...")
    feedback_id = await engine.resolve_post_id("https://www.facebook.com/photo?fbid=1532133465628571&set=a.650104283831498")
    print(f"Feedback ID: {feedback_id}")
    
    if not feedback_id:
        return
        
    rate_limiter = RateLimiter(min_batch=5, max_batch=10, min_delay=1, max_delay=2)
    scraper = CommentScraper(engine, rate_limiter, include_replies=True)
    
    print("Fetching comments...")
    comments = await scraper.fetch_comments(feedback_id, feedback_id, max_comments=10)
    print(f"Scraped {len(comments)} comments!")
    
    for c in comments:
        print(f" - {c.author_name}: {c.content}")
        for r in c.replies:
            print(f"   ↳ {r.author_name}: {r.content}")
            
    await engine.close()

asyncio.run(test())
