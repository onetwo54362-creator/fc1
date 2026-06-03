"""GraphQL HTTP request engine for Facebook API."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Optional

import httpx

from .constants import (
    GRAPHQL_URL,
    DEFAULT_REQUEST_TIMEOUT,
    DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_BASE_DELAY,
    get_base_headers,
    get_random_user_agent,
)
from .proxy_manager import ProxyManager
from .response_parser import parse_fb_json_first

log = logging.getLogger(__name__)

class GraphQLEngine:
    """Pure HTTP engine for Facebook GraphQL API requests."""

    def __init__(
        self,
        cookies: dict,
        fb_dtsg: str,
        proxy_manager: Optional[ProxyManager] = None,
        timeout: int = DEFAULT_REQUEST_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ):
        self.cookies = cookies
        self.fb_dtsg = fb_dtsg
        self.proxy_manager = proxy_manager or ProxyManager()
        self.timeout = timeout
        self.max_retries = max_retries
        self._user_agent = get_random_user_agent()
        self._total_requests = 0
        self._failed_requests = 0

        proxy_url = self.proxy_manager.get_proxy_dict()
        self._client = httpx.AsyncClient(
            proxy=proxy_url,
            timeout=httpx.Timeout(timeout),
            follow_redirects=True,
            cookies=cookies,
        )

        user_id = cookies.get("c_user", "0")
        log.info(f"🔗 GraphQL engine initialized (user_id: {user_id})")

    async def close(self):
        await self._client.aclose()

    def _build_payload(self, doc_id: str, variables: dict, friendly_name: str = "") -> dict:
        user_id = self.cookies.get("c_user", "0")
        return {
            "av": user_id,
            "__user": user_id,
            "__a": "1",
            "fb_dtsg": self.fb_dtsg,
            "fb_api_caller_class": "RelayModern",
            "fb_api_req_friendly_name": friendly_name,
            "server_timestamps": "true",
            "doc_id": doc_id,
            "variables": json.dumps(variables),
        }

    async def request_json(
        self,
        doc_id: str,
        variables: dict,
        friendly_name: str = "",
    ) -> dict:
        headers = get_base_headers(
            user_agent=self._user_agent,
            friendly_name=friendly_name,
        )
        payload = self._build_payload(doc_id, variables, friendly_name)

        for attempt in range(1, self.max_retries + 1):
            try:
                self._total_requests += 1
                response = await self._client.post(
                    GRAPHQL_URL,
                    data=payload,
                    headers=headers,
                )

                if self.proxy_manager.is_blocked(
                    status_code=response.status_code,
                    response_text=response.text[:500] if response.status_code != 200 else "",
                ):
                    if attempt < self.max_retries:
                        wait = attempt * DEFAULT_RETRY_BASE_DELAY
                        await asyncio.sleep(wait)
                    continue

                if response.status_code == 200:
                    self.proxy_manager.on_success()
                    return parse_fb_json_first(response.text)

                if attempt < self.max_retries:
                    wait = attempt * DEFAULT_RETRY_BASE_DELAY
                    await asyncio.sleep(wait)

            except Exception as e:
                self._failed_requests += 1
                log.warning(f"  ⚠️ Attempt {attempt}/{self.max_retries}: {e}")
                if attempt < self.max_retries:
                    wait = attempt * DEFAULT_RETRY_BASE_DELAY
                    await asyncio.sleep(wait)

        return {}

    async def auto_fetch_fb_dtsg(self) -> Optional[str]:
        """Auto-fetch the fb_dtsg CSRF token from Facebook.
        
        Tries multiple pages and regex patterns to find the token.
        """
        import re
        log.info("🔑 Auto-fetching fb_dtsg token from Facebook...")

        # All known patterns for fb_dtsg in Facebook HTML/JS
        dtsg_patterns = [
            r'\["DTSGInitData",\[\],\{"token":"([^"]+)"',
            r'\["DTSGInitialData",\[\],\{"token":"([^"]+)"',
            r'"DTSGInitData",\[\],\{"token":"([^"]+)"',
            r'"DTSGInitialData",\[\],\{"token":"([^"]+)"',
            r'"dtsg":\{"token":"([^"]+)"',
            r'"fb_dtsg":"([^"]+)"',
            r'name="fb_dtsg" value="([^"]+)"',
        ]

        urls_to_try = [
            "https://www.facebook.com/",
            "https://www.facebook.com/settings",
        ]

        for url in urls_to_try:
            try:
                headers = get_base_headers(user_agent=self._user_agent)
                headers.update({
                    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                    "sec-fetch-dest": "document",
                    "sec-fetch-mode": "navigate",
                    "sec-fetch-site": "none",
                    "sec-fetch-user": "?1",
                    "upgrade-insecure-requests": "1",
                })
                response = await self._client.get(url, headers=headers)

                if response.status_code != 200:
                    continue

                for pattern in dtsg_patterns:
                    matches = re.findall(pattern, response.text)
                    for token in matches:
                        if len(token) > 10 and not token.isdigit():
                            log.info(f"✅ Auto-fetched fb_dtsg token from {url}")
                            self.fb_dtsg = token
                            return token

            except Exception as e:
                continue

        log.warning("⚠️ Could not find fb_dtsg automatically. GraphQL requests may fail!")
        return None

    async def resolve_post_id(self, post_url: str) -> Optional[dict]:
        """Fetch the post URL and extract the actual base64 feedback ID from the HTML, 
        along with basic post context (author name, text)."""
        import re
        import json
        import base64
        
        post_info = {
            "post_url": post_url,
            "feedback_id": "",
            "post_author_name": "",
            "post_text": ""
        }
        
        try:
            headers = get_base_headers(user_agent=self._user_agent)
            headers.update({
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "none",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1",
            })
            response = await self._client.get(post_url, headers=headers)
            
            if response.status_code == 200:
                html = response.text
                
                # Extract basic info for context
                author_match = re.search(r'"actors":\[\{[^}]*?"name":"([^"]+)"', html)
                if not author_match:
                    author_match = re.search(r'"owning_profile":\{[^}]*?"name":"([^"]+)"', html)
                if author_match:
                    post_info["post_author_name"] = author_match.group(1)
                    
                text_match = re.search(r'"message":\{"text":"([^"]+)"\}', html)
                if text_match:
                    try:
                        post_info["post_text"] = json.loads(f'"{text_match.group(1)}"')
                    except:
                        post_info["post_text"] = text_match.group(1)
                
                # Look for feedback ID in the deeply nested JSON of the page source
                patterns = [
                    r'"feedback_id":"(ZmVlZGJh[^"]+)"',
                    r'"feedback":\{"id":"(ZmVlZGJh[^"]+)"',
                    r'"target_feedback":\{"id":"(ZmVlZGJh[^"]+)"',
                    r'"feedback_target_with_context":\{"feedback_id":"(ZmVlZGJh[^"]+)"'
                ]
                
                for p in patterns:
                    matches = re.findall(p, html)
                    for m in matches:
                        try:
                            decoded = base64.b64decode(m).decode('utf-8')
                            if "feedback:" in decoded and "_" not in decoded:
                                post_info["feedback_id"] = m
                                return post_info
                        except:
                            pass
                        
                # Fallback to URL regex if HTML parsing fails
                fallback_patterns = [
                    r'/posts/(\d+)',
                    r'/videos/(\d+)',
                    r'/photos/[^/]+/(\d+)',
                    r'fbid=(\d+)',
                    r'/groups/[^/]+/permalink/(\d+)',
                ]
                raw_id = None
                for fp in fallback_patterns:
                    m = re.search(fp, post_url)
                    if m:
                        raw_id = m.group(1)
                        break
                        
                if raw_id:
                    post_info["feedback_id"] = base64.b64encode(f"feedback:{raw_id}".encode('utf-8')).decode('utf-8')
                    return post_info
                    
        except Exception as e:
            log.error(f"Error fetching post URL to resolve ID: {e}")

        return None

    def get_stats(self) -> dict:
        return {
            "total_requests": self._total_requests,
            "failed_requests": self._failed_requests,
        }
