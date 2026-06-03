"""Comment and reply scraper.

Uses GraphQL API to fetch all comments and nested replies for a post.
"""

from __future__ import annotations

import logging
from typing import Optional

from .constants import DOC_IDS, FRIENDLY_NAMES
from .models import CommentData

log = logging.getLogger(__name__)


# Facebook uses static node IDs for each reaction type in comment feedback.
# These are well-known and stable across the platform.
REACTION_ID_MAP = {
    "1635855486666999": "like",
    "1678524932434102": "love",
    "115940658764963":  "haha",
    "478547315650144":  "wow",
    "908563459236466":  "sad",
    "444813342392137":  "angry",
    "613557422527858":  "care",
}


def _extract_reaction_breakdown(feedback: dict) -> dict:
    """Extract per-type reaction counts from a comment's feedback node.
    
    Facebook's comment GraphQL returns reactions in feedback.top_reactions.edges.
    Each edge has {node: {id: "1635855486666999"}, reaction_count: N}.
    The node ID maps to a reaction type (Like, Love, Haha, etc.).
    """
    breakdown = {
        "total": 0, "like": 0, "love": 0, "haha": 0,
        "wow": 0, "sad": 0, "angry": 0, "care": 0,
    }
    
    top_reactions = feedback.get("top_reactions", {})
    if top_reactions and isinstance(top_reactions, dict):
        edges = top_reactions.get("edges", [])
        for edge in edges:
            reaction_node = edge.get("node", {})
            count = edge.get("reaction_count", 0)
            
            # Method 1: Map by node ID (comment feedback uses this)
            node_id = reaction_node.get("id", "")
            reaction_type = REACTION_ID_MAP.get(node_id, "")
            
            # Method 2: Fallback to reaction_type or localized_name (post feedback)
            if not reaction_type:
                reaction_type = (
                    reaction_node.get("reaction_type") 
                    or reaction_node.get("localized_name") 
                    or ""
                ).lower()
            
            if reaction_type in breakdown:
                breakdown[reaction_type] = count
    
    # Total from reactors.count_reduced (more reliable than summing)
    reactors = feedback.get("reactors", {})
    total = reactors.get("count_reduced", 0)
    if isinstance(total, str):
        total = int(total) if total.isdigit() else 0
    
    if total > 0:
        breakdown["total"] = total
    else:
        breakdown["total"] = sum(v for k, v in breakdown.items() if k != "total")
    
    return breakdown


class CommentScraper:
    """Fetches comments and replies for Facebook posts."""

    def __init__(self, graphql_engine, rate_limiter=None, include_replies=True):
        self.engine = graphql_engine
        self.rate_limiter = rate_limiter
        self.include_replies = include_replies
        self._total_comments = 0
        self._total_replies = 0

    async def fetch_comments(
        self, feedback_id: str, post_id: str, max_comments: int = 0, post_info: dict = None
    ) -> list[CommentData]:
        if not feedback_id:
            log.warning("No feedback_id provided, cannot fetch comments.")
            return []

        # Phase 1: Collect all top-level comments
        raw_comments = []
        cursor = None
        page_num = 0

        while True:
            page_num += 1
            variables = {
                "commentsAfterCount": -1,
                "commentsAfterCursor": cursor,
                "commentsIntentToken": "REVERSE_CHRONOLOGICAL_UNFILTERED_INTENT_V1",
                "feedLocation": "DEDICATED_COMMENTING_SURFACE",
                "focusCommentID": None,
                "scale": 2,
                "useDefaultActor": False,
                "id": feedback_id,
            }

            if self.rate_limiter:
                await self.rate_limiter.on_request()

            response = await self.engine.request_json(
                doc_id=DOC_IDS["COMMENTS"],
                variables=variables,
                friendly_name=FRIENDLY_NAMES["COMMENTS"],
            )

            if not response:
                break

            comments_block = (
                response.get("data", {})
                .get("node", {})
                .get("comment_rendering_instance_for_feed_location", {})
                .get("comments", {})
            )

            edges = comments_block.get("edges", [])
            if not edges:
                break

            for edge in edges:
                node = edge.get("node", {})
                fb = node.get("feedback", {})
                reactions = _extract_reaction_breakdown(fb)

                comment_id = node.get("legacy_fbid") or node.get("id") or ""
                author_node = node.get("author", {}) or {}
                
                comment = CommentData(
                    post_url=post_info.get("post_url", "") if post_info else "",
                    post_author_name=post_info.get("post_author_name", "") if post_info else "",
                    post_text=post_info.get("post_text", "") if post_info else "",
                    comment_id=comment_id,
                    post_id=post_id,
                    text=(node.get("body") or {}).get("text", ""),
                    author_name=author_node.get("name", ""),
                    author_url=author_node.get("url", ""),
                    reaction_count=reactions["total"],
                    reactions_like=reactions["like"],
                    reactions_love=reactions["love"],
                    reactions_haha=reactions["haha"],
                    reactions_wow=reactions["wow"],
                    reactions_sad=reactions["sad"],
                    reactions_angry=reactions["angry"],
                    reactions_care=reactions["care"],
                    feedback_id=fb.get("id", ""),
                    expansion_token=(
                        fb.get("expansion_info", {}).get("expansion_token", "")
                    ),
                    is_reply=False
                )

                raw_comments.append(comment)
                self._total_comments += 1

                if max_comments > 0 and self._total_comments >= max_comments:
                    break

            if max_comments > 0 and self._total_comments >= max_comments:
                break

            cursor = comments_block.get("page_info", {}).get("end_cursor")
            if not cursor:
                break

            if self.rate_limiter:
                await self.rate_limiter.pagination_delay()

        # Phase 2: Fetch replies for each comment, number everything, 
        # and build final threaded list
        results = []
        comment_num = 0

        for comment in raw_comments:
            comment_num += 1
            comment.comment_number = f"#{comment_num}"

            # Fetch replies if available
            replies = []
            if self.include_replies and comment.feedback_id and comment.expansion_token:
                replies = await self._fetch_replies(comment)

            # Set reply_count on the parent comment
            comment.reply_count = len(replies)

            # Number the replies: #1.1, #1.2, etc.
            for reply_idx, reply in enumerate(replies, 1):
                reply.comment_number = f"#{comment_num}.{reply_idx}"

            # Append in threaded order: comment first, then its replies
            results.append(comment)
            results.extend(replies)

        log.info(
            f"  💬 Fetched {self._total_comments} comments, "
            f"{self._total_replies} replies for post {post_id}"
        )
        return results

    async def _fetch_replies(self, parent_comment: CommentData) -> list[CommentData]:
        """Fetch replies for a single comment."""
        variables = {
            "clientKey": None,
            "expansionToken": parent_comment.expansion_token,
            "feedLocation": "POST_PERMALINK_DIALOG",
            "focusCommentID": None,
            "scale": 2,
            "useDefaultActor": False,
            "id": parent_comment.feedback_id,
        }

        if self.rate_limiter:
            await self.rate_limiter.on_request()
            await self.rate_limiter.pagination_delay()

        response = await self.engine.request_json(
            doc_id=DOC_IDS["REPLIES"],
            variables=variables,
            friendly_name=FRIENDLY_NAMES["REPLIES"],
        )

        if not response:
            return []

        replies = []
        edges = (
            response.get("data", {})
            .get("node", {})
            .get("replies_connection", {})
            .get("edges", [])
        )

        for edge in edges:
            node = edge.get("node", {})
            fb = node.get("feedback", {})
            reactions = _extract_reaction_breakdown(fb)
            
            reply_id = node.get("legacy_fbid") or node.get("id") or ""
            author_node = node.get("author", {}) or {}

            reply = CommentData(
                post_url=parent_comment.post_url,
                post_author_name=parent_comment.post_author_name,
                post_text=parent_comment.post_text,
                comment_id=reply_id,
                post_id=parent_comment.post_id,
                text=(node.get("body") or {}).get("text", ""),
                author_name=author_node.get("name", ""),
                author_url=author_node.get("url", ""),
                reaction_count=reactions["total"],
                reactions_like=reactions["like"],
                reactions_love=reactions["love"],
                reactions_haha=reactions["haha"],
                reactions_wow=reactions["wow"],
                reactions_sad=reactions["sad"],
                reactions_angry=reactions["angry"],
                reactions_care=reactions["care"],
                is_reply=True,
                parent_comment_id=parent_comment.comment_id
            )
            replies.append(reply)
            self._total_replies += 1

        return replies

    def get_stats(self) -> dict:
        return {
            "total_comments": self._total_comments,
            "total_replies": self._total_replies,
        }
