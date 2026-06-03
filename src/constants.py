"""Constants and configuration for the Facebook Comment Exporter."""

import random

# =============================================================================
# GraphQL Endpoint
# =============================================================================
GRAPHQL_URL = "https://www.facebook.com/api/graphql/"

# =============================================================================
# GraphQL Document IDs
# =============================================================================
DOC_IDS = {
    # Comments on a post (paginated)
    "COMMENTS": "25550760954572974",  # CommentsListComponentsPaginationQuery
    
    # Replies to a comment (depth-1)
    "REPLIES": "26570577339199586",  # Depth1CommentsListPaginationQuery
}

# =============================================================================
# GraphQL Friendly Names
# =============================================================================
FRIENDLY_NAMES = {
    "COMMENTS": "CommentsListComponentsPaginationQuery",
    "REPLIES": "Depth1CommentsListPaginationQuery",
}

# =============================================================================
# User Agent Pool
# =============================================================================
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
]

def get_random_user_agent() -> str:
    """Return a random user agent string."""
    return random.choice(USER_AGENTS)

def get_base_headers(user_agent: str | None = None, friendly_name: str | None = None) -> dict:
    """Build base headers for Facebook GraphQL requests."""
    ua = user_agent or get_random_user_agent()
    headers = {
        "user-agent": ua,
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://www.facebook.com",
        "referer": "https://www.facebook.com/",
        "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
    }
    if friendly_name:
        headers["x-fb-friendly-name"] = friendly_name
    return headers

# =============================================================================
# Block Detection Signals
# =============================================================================
BLOCK_STATUS_CODES = {403, 429, 503}
BLOCK_KEYWORDS = [
    "checkpoint",
    "login_required",
    "you must log in",
    "blocked",
    "temporarily blocked",
    "account has been disabled",
]

PROXY_ERROR_KEYWORDS = [
    "proxy",
    "407",
    "tunnel",
    "connection refused",
    "cannot connect to proxy",
    "eof occurred",
]

# =============================================================================
# Response Parsing
# =============================================================================
FB_RESPONSE_PREFIX = "for (;;);"

# =============================================================================
# Default Config
# =============================================================================
DEFAULT_REQUEST_TIMEOUT = 30  # seconds
DEFAULT_MAX_RETRIES = 5
DEFAULT_RETRY_BASE_DELAY = 2  # seconds (multiplied by attempt number)
