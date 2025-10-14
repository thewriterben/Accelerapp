"""
Community forum management system.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class ForumPost:
    """Represents a forum post."""

    id: str
    category: str
    title: str
    author: str
    content: str
    tags: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    replies: List["ForumReply"] = field(default_factory=list)
    views: int = 0
    likes: int = 0
    is_pinned: bool = False
    is_locked: bool = False


@dataclass
class ForumReply:
    """Represents a reply to a forum post."""

    id: str
    post_id: str
    author: str
    content: str
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    likes: int = 0


class ForumManager:
    """
    Manages community forums with categories, posts, and replies.
    """

    def __init__(self):
        """Initialize forum manager."""
        self.posts: Dict[str, ForumPost] = {}
        self.categories = [
            "General Discussion",
            "Hardware Support",
            "Software Development",
            "Feature Requests",
            "Showcase",
            "Tutorials",
        ]

    def create_post(
        self,
        post_id: str,
        category: str,
        title: str,
        author: str,
        content: str,
        tags: Optional[List[str]] = None,
    ) -> ForumPost:
        """
        Create a new forum post.

        Args:
            post_id: Unique post identifier
            category: Post category
            title: Post title
            author: Post author
            content: Post content
            tags: Optional tags

        Returns:
            Created ForumPost
        """
        if category not in self.categories:
            raise ValueError(f"Invalid category: {category}")

        post = ForumPost(
            id=post_id,
            category=category,
            title=title,
            author=author,
            content=content,
            tags=tags or [],
        )
        self.posts[post_id] = post
        return post

    def add_reply(self, post_id: str, reply_id: str, author: str, content: str) -> ForumReply:
        """
        Add a reply to a post.

        Args:
            post_id: Post identifier
            reply_id: Reply identifier
            author: Reply author
            content: Reply content

        Returns:
            Created ForumReply
        """
        if post_id not in self.posts:
            raise ValueError(f"Post not found: {post_id}")

        reply = ForumReply(id=reply_id, post_id=post_id, author=author, content=content)
        self.posts[post_id].replies.append(reply)
        return reply

    def get_post(self, post_id: str) -> Optional[ForumPost]:
        """
        Get a post by ID.

        Args:
            post_id: Post identifier

        Returns:
            ForumPost or None
        """
        post = self.posts.get(post_id)
        if post:
            post.views += 1
        return post

    def list_posts(
        self, category: Optional[str] = None, tags: Optional[List[str]] = None
    ) -> List[ForumPost]:
        """
        List posts with optional filters.

        Args:
            category: Filter by category
            tags: Filter by tags

        Returns:
            List of ForumPost
        """
        posts = list(self.posts.values())

        if category:
            posts = [p for p in posts if p.category == category]

        if tags:
            posts = [p for p in posts if any(tag in p.tags for tag in tags)]

        # Sort: pinned first, then by creation date
        posts.sort(key=lambda p: (not p.is_pinned, p.created_at), reverse=True)
        return posts

    def like_post(self, post_id: str) -> bool:
        """
        Like a post.

        Args:
            post_id: Post identifier

        Returns:
            True if successful
        """
        if post_id in self.posts:
            self.posts[post_id].likes += 1
            return True
        return False

    def pin_post(self, post_id: str, pinned: bool = True) -> bool:
        """
        Pin or unpin a post.

        Args:
            post_id: Post identifier
            pinned: Pin status

        Returns:
            True if successful
        """
        if post_id in self.posts:
            self.posts[post_id].is_pinned = pinned
            return True
        return False

    def lock_post(self, post_id: str, locked: bool = True) -> bool:
        """
        Lock or unlock a post.

        Args:
            post_id: Post identifier
            locked: Lock status

        Returns:
            True if successful
        """
        if post_id in self.posts:
            self.posts[post_id].is_locked = locked
            return True
        return False

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get forum statistics.

        Returns:
            Statistics dictionary
        """
        total_posts = len(self.posts)
        total_replies = sum(len(p.replies) for p in self.posts.values())
        posts_by_category = {}

        for post in self.posts.values():
            posts_by_category[post.category] = posts_by_category.get(post.category, 0) + 1

        return {
            "total_posts": total_posts,
            "total_replies": total_replies,
            "total_interactions": total_posts + total_replies,
            "posts_by_category": posts_by_category,
            "categories": self.categories,
        }
