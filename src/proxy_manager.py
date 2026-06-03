"""Proxy manager with block detection and rotation."""

from __future__ import annotations

import logging
from typing import Optional

from .constants import BLOCK_STATUS_CODES, BLOCK_KEYWORDS, PROXY_ERROR_KEYWORDS

log = logging.getLogger(__name__)

class ProxyManager:
    """Manages proxy rotation and block detection."""

    def __init__(self, proxy_url: Optional[str] = None):
        self.proxy_url = proxy_url
        self._block_count = 0
        self._total_requests = 0
        
        if proxy_url:
            log.info(f"🔒 Proxy configured: {self._mask_proxy(proxy_url)}")
        else:
            log.info("⚠️  No proxy configured — requests will use direct connection")

    def get_proxy_dict(self) -> Optional[dict]:
        if self.proxy_url:
            return self.proxy_url
        return None

    def is_blocked(self, status_code: int = 0, response_text: str = "") -> bool:
        self._total_requests += 1
        
        if status_code in BLOCK_STATUS_CODES:
            self._block_count += 1
            log.warning(f"🚫 Block detected: HTTP {status_code} (total blocks: {self._block_count})")
            return True
        
        if response_text:
            text_lower = response_text[:500].lower()
            for keyword in BLOCK_KEYWORDS:
                if keyword in text_lower:
                    self._block_count += 1
                    log.warning(f"🚫 Block detected: '{keyword}' in response")
                    return True
        
        return False

    def on_success(self) -> None:
        self._total_requests += 1

    def get_stats(self) -> dict:
        return {
            "total_requests": self._total_requests,
            "blocks_detected": self._block_count,
            "proxy_configured": bool(self.proxy_url),
        }

    @staticmethod
    def _mask_proxy(url: str) -> str:
        if "@" in url:
            parts = url.split("@")
            return f"***@{parts[-1]}"
        return url
