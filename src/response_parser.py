"""Response parsing for Facebook Comments API."""

import json
import logging

from .constants import FB_RESPONSE_PREFIX

log = logging.getLogger(__name__)

def parse_fb_json_first(response_text: str) -> dict:
    """Parse Facebook response and return the first valid JSON object."""
    text = response_text.strip()
    if text.startswith(FB_RESPONSE_PREFIX):
        text = text[len(FB_RESPONSE_PREFIX):]
    
    first_line = text.split("\n")[0].strip()
    try:
        return json.loads(first_line)
    except json.JSONDecodeError as e:
        log.warning(f"Failed to parse JSON block: {e}")
        return {}
