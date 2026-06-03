"""Main orchestrator for Facebook Comment Exporter."""

import asyncio
import logging
from datetime import datetime, timezone

from apify import Actor

from .graphql_engine import GraphQLEngine
from .proxy_manager import ProxyManager
from .rate_limiter import RateLimiter
from .comment_scraper import CommentScraper
from .excel_exporter import ExcelExporter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("fb-comments")

def parse_cookies(cookie_str: str) -> dict:
    import json
    cookies = {}
    cookie_str = cookie_str.strip()
    
    # 1. Try JSON format
    try:
        parsed = json.loads(cookie_str)
        if isinstance(parsed, list):
            for c in parsed:
                if 'name' in c and 'value' in c:
                    cookies[c['name']] = c['value']
        elif isinstance(parsed, dict):
            cookies = parsed
        return cookies
    except json.JSONDecodeError:
        pass

    # 2. Try Netscape format (tab-separated)
    if "# Netscape" in cookie_str or "\t" in cookie_str:
        for line in cookie_str.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) >= 7:
                cookies[parts[5]] = parts[6]
        if cookies:
            return cookies

    # 3. Try key=value; format
    for part in cookie_str.split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            cookies[k.strip()] = v.strip()
            
    return cookies

async def main():
    async with Actor:
        actor_input = await Actor.get_input() or {}

        post_urls = actor_input.get("postUrls", [])
        cookie_str = actor_input.get("cookies", "").strip()
        fb_dtsg = actor_input.get("fbDtsg", "").strip()
        max_comments = actor_input.get("maxComments", 0)
        include_replies = actor_input.get("includeReplies", True)
        
        min_batch = actor_input.get("minBatchSize", 10)
        max_batch = actor_input.get("maxBatchSize", 30)
        min_cooldown = actor_input.get("minCooldownSeconds", 2)
        max_cooldown = actor_input.get("maxCooldownSeconds", 8)
        
        proxy_url = actor_input.get("proxyUrl", "").strip() or None
        excel_export = actor_input.get("excelExport", True)

        if not post_urls:
            await Actor.fail(status_message="postUrls is required")
            return
        if not cookie_str:
            await Actor.fail(status_message="cookies is required")
            return

        cookies = parse_cookies(cookie_str)
        if "c_user" not in cookies:
            await Actor.fail(status_message="Cookie string must contain 'c_user'")
            return

        proxy_manager = ProxyManager(proxy_url=proxy_url)
        rate_limiter = RateLimiter(
            min_batch=min_batch,
            max_batch=max_batch,
            min_delay=min_cooldown,
            max_delay=max_cooldown,
        )

        engine = GraphQLEngine(
            cookies=cookies,
            fb_dtsg=fb_dtsg or "",
            proxy_manager=proxy_manager,
        )
        
        if not fb_dtsg:
            log.info("No fb_dtsg provided in input, attempting to auto-fetch...")
            await engine.auto_fetch_fb_dtsg()

        exporter = ExcelExporter() if excel_export else None
        scraper = CommentScraper(engine, rate_limiter, include_replies)

        for post_url in post_urls:
            if not post_url.strip():
                continue
                
            log.info(f"🎯 Processing Post URL: {post_url}")
            
            # 1. Resolve Feedback ID
            # In Facebook's backend, the post ID is often the feedback ID,
            # or it requires a base64 encoded string.
            # We will use our basic regex resolver.
            post_info = await engine.resolve_post_id(post_url)
            if not post_info or not post_info.get("feedback_id"):
                log.warning(f"❌ Could not resolve feedback/post ID for {post_url}. Make sure it's a direct post URL.")
                continue
                
            feedback_id = post_info["feedback_id"]
            log.info(f"✅ Found ID: {feedback_id} | Author: {post_info.get('post_author_name')}")
            
            # 2. Fetch comments
            comments = await scraper.fetch_comments(
                feedback_id=feedback_id, 
                post_id=feedback_id, 
                max_comments=max_comments,
                post_info=post_info
            )
            
            # 3. Export
            for c in comments:
                await Actor.push_data(c.to_dataset_dict())
                if exporter:
                    exporter.add_comment(c)

        if exporter and exporter.get_stats()["total_rows"] > 0:
            excel_bytes = exporter.save_to_bytes()
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = f"comments_{timestamp}.xlsx"

            kvs = await Actor.open_key_value_store()
            await kvs.set_value(
                filename,
                excel_bytes,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            log.info(f"✅ Excel saved: {filename}")

        stats = scraper.get_stats()
        await Actor.set_status_message(f"Done! Scraped {stats['total_comments']} comments and {stats['total_replies']} replies.")
        await engine.close()

if __name__ == "__main__":
    asyncio.run(main())
