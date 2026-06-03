"""Rate limiter with random cooldown for anti-detection."""

from __future__ import annotations

import asyncio
import logging
import random

log = logging.getLogger(__name__)

class RateLimiter:
    """Random batch cooldown system to mimic human browsing behavior."""

    def __init__(
        self,
        min_batch: int = 10,
        max_batch: int = 30,
        min_delay: float = 2.0,
        max_delay: float = 8.0,
    ):
        self.min_batch = max(1, min_batch)
        self.max_batch = max(self.min_batch, max_batch)
        self.min_delay = max(0.5, min_delay)
        self.max_delay = max(self.min_delay, max_delay)
        
        self._requests_in_current_batch = 0
        self._batch_target = self._new_batch_target()
        self._total_cooldowns = 0
        self._total_cooldown_time = 0.0
        
        log.info(
            f"⏱️  Rate limiter initialized: cooldown every {self.min_batch}-{self.max_batch} requests, "
            f"delay {self.min_delay}-{self.max_delay}s"
        )

    def _new_batch_target(self) -> int:
        return random.randint(self.min_batch, self.max_batch)

    async def on_request(self) -> None:
        """Call this after each request is made."""
        self._requests_in_current_batch += 1
        
        if self._requests_in_current_batch >= self._batch_target:
            await self._cooldown()

    async def _cooldown(self) -> None:
        """Execute a random cooldown period."""
        base_delay = random.uniform(self.min_delay, self.max_delay)
        jitter = base_delay * random.uniform(-0.25, 0.25)
        actual_delay = max(0.5, base_delay + jitter)
        
        self._total_cooldowns += 1
        self._total_cooldown_time += actual_delay
        
        log.info(
            f"🛑 Cooldown #{self._total_cooldowns}: pausing {actual_delay:.1f}s "
            f"after {self._requests_in_current_batch} requests"
        )
        
        await asyncio.sleep(actual_delay)
        
        self._requests_in_current_batch = 0
        self._batch_target = self._new_batch_target()

    async def pagination_delay(self) -> None:
        """Small delay between pagination requests."""
        delay = random.uniform(1.0, 2.5)
        await asyncio.sleep(delay)

    def get_stats(self) -> dict:
        return {
            "total_cooldowns": self._total_cooldowns,
            "total_cooldown_time_seconds": round(self._total_cooldown_time, 1),
        }
