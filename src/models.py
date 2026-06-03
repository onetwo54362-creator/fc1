"""Data models for the Facebook Comment Exporter."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone

@dataclass
class CommentData:
    """Represents a comment or reply."""
    post_url: str = ""
    post_author_name: str = ""
    post_text: str = ""
    comment_number: str = ""        # e.g. "#1", "#2", "#2.1", "#2.2"
    type: str = "Comment"           # "Comment" or "↳ Reply"
    comment_id: str = ""
    post_id: str = ""
    text: str = ""
    author_name: str = ""
    author_url: str = ""
    media_type: str = ""            # "photo", "video", "gif", "sticker"
    media_url: str = ""             # URL to the attached media
    reaction_count: int = 0
    reactions_like: int = 0
    reactions_love: int = 0
    reactions_haha: int = 0
    reactions_wow: int = 0
    reactions_sad: int = 0
    reactions_angry: int = 0
    reactions_care: int = 0
    reply_count: int = 0
    feedback_id: str = ""
    expansion_token: str = ""
    is_reply: bool = False
    parent_comment_id: str = ""
    scraped_at: str = ""

    def __post_init__(self):
        if not self.scraped_at:
            self.scraped_at = datetime.now(timezone.utc).isoformat()
        if self.is_reply:
            self.type = "↳ Reply"

    def to_dataset_dict(self) -> dict:
        """Convert to a flat dictionary for Apify Dataset."""
        return {
            "post_url": self.post_url or "No post URL",
            "post_author_name": self.post_author_name or "No post author name",
            "post_text": self.post_text or "No post text",
            "comment_number": self.comment_number or "No comment number",
            "type": self.type,
            "comment_id": self.comment_id or "No comment ID",
            "post_id": self.post_id or "No post ID",
            "author_name": self.author_name or "No author name",
            "author_url": self.author_url or "No author URL",
            "text": self.text or "No comment text",
            "media_type": self.media_type or "No media type",
            "media_url": self.media_url or "No media URL",
            "reaction_count": self.reaction_count,
            "reactions_like": self.reactions_like,
            "reactions_love": self.reactions_love,
            "reactions_haha": self.reactions_haha,
            "reactions_wow": self.reactions_wow,
            "reactions_sad": self.reactions_sad,
            "reactions_angry": self.reactions_angry,
            "reactions_care": self.reactions_care,
            "reply_count": self.reply_count,
            "is_reply": self.is_reply,
            "parent_comment_id": self.parent_comment_id or "No parent comment ID",
            "scraped_at": self.scraped_at,
        }

    def to_excel_row(self) -> list:
        """Convert to a flat list for Excel row."""
        return [
            self.post_url or "No post URL",
            self.post_author_name or "No post author name",
            self.post_text or "No post text",
            self.comment_number or "No comment number",
            self.type,
            self.comment_id or "No comment ID",
            self.post_id or "No post ID",
            self.author_name or "No author name",
            self.author_url or "No author URL",
            self.text or "No comment text",
            self.media_type or "No media type",
            self.media_url or "No media URL",
            self.reaction_count,
            self.reactions_like,
            self.reactions_love,
            self.reactions_haha,
            self.reactions_wow,
            self.reactions_sad,
            self.reactions_angry,
            self.reactions_care,
            self.reply_count,
            "Yes" if self.is_reply else "No",
            self.parent_comment_id or "No parent comment ID",
            self.scraped_at,
        ]

EXCEL_HEADERS = [
    "Post URL",
    "Post Author Name",
    "Post Text",
    "Comment #",
    "Type",
    "Comment ID",
    "Post ID",
    "Author Name",
    "Author URL",
    "Comment Text",
    "Media Type",
    "Media URL",
    "Reactions Total",
    "👍 Like",
    "❤️ Love",
    "😂 Haha",
    "😮 Wow",
    "😢 Sad",
    "😠 Angry",
    "🤗 Care",
    "Reply Count",
    "Is Reply",
    "Parent Comment ID",
    "Scraped At (ISO)",
]


