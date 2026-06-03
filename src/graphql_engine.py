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

    async def resolve_post_id(self, post_url: str) -> Optional[str]:
        """Extract the feedback/post ID from a URL using regex."""
        import re
        import base64
        
        # E.g. facebook.com/pagename/posts/123456
        patterns = [
            r'/posts/(\d+)',
            r'/videos/(\d+)',
            r'/photos/[^/]+/(\d+)',
            r'fbid=(\d+)',
            r'/groups/[^/]+/permalink/(\d+)',
        ]
        
        raw_id = None
        for pattern in patterns:
            match = re.search(pattern, post_url)
            if match:
                raw_id = match.group(1)
                break
                
        if raw_id:
            # Facebook GraphQL usually expects the feedback ID to be base64 encoded
            return base64.b64encode(f"feedback:{raw_id}".encode('utf-8')).decode('utf-8')

        return None

    def get_stats(self) -> dict:
        return {
            "total_requests": self._total_requests,
            "failed_requests": self._failed_requests,
        }
