"""Data models for the Facebook Comment Exporter."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone

@dataclass
class CommentData:
    """Represents a comment or reply."""
    comment_id: str = ""
    post_id: str = ""
    text: str = ""
    author_name: str = ""
    author_url: str = ""
    reaction_count: int = 0
    feedback_id: str = ""
    expansion_token: str = ""
    is_reply: bool = False
    parent_comment_id: str = ""
    scraped_at: str = ""

    def __post_init__(self):
        if not self.scraped_at:
            self.scraped_at = datetime.now(timezone.utc).isoformat()

    def to_dataset_dict(self) -> dict:
        """Convert to a flat dictionary for Apify Dataset."""
        return {
            "comment_id": self.comment_id,
            "post_id": self.post_id,
            "author_name": self.author_name,
            "author_url": self.author_url,
            "text": self.text,
            "reaction_count": self.reaction_count,
            "is_reply": self.is_reply,
            "parent_comment_id": self.parent_comment_id,
            "scraped_at": self.scraped_at,
        }

    def to_excel_row(self) -> list:
        """Convert to a flat list for Excel row."""
        return [
            self.comment_id,
            self.post_id,
            self.author_name,
            self.author_url,
            self.text,
            self.reaction_count,
            "Yes" if self.is_reply else "No",
            self.parent_comment_id,
            self.scraped_at,
        ]

EXCEL_HEADERS = [
    "Comment ID",
    "Post ID",
    "Author Name",
    "Author URL",
    "Comment Text",
    "Reaction Count",
    "Is Reply",
    "Parent Comment ID",
    "Scraped At (ISO)",
]
