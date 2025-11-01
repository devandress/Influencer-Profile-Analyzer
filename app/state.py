import reflex as rx
from typing import TypedDict, Optional
import logging
from datetime import datetime


class Post(TypedDict):
    shortcode: str
    display_url: str
    likes: int
    comments: int
    caption: str
    timestamp: int


class Profile(TypedDict):
    username: str
    followers: str
    following: str
    posts: int
    bio: str
    profile_pic_url: str
    is_private: bool
    engagement_rate: float
    avg_likes: int
    avg_comments: int
    recent_posts: list[Post]
    engagement_data: list[dict]


class AppState(rx.State):
    """The main application state."""

    search_query: str = ""
    is_loading: bool = False
    error_message: Optional[str] = None
    profile_data: Optional[Profile] = None

    @rx.event
    def handle_search(self, form_data: dict):
        """Handle the search form submission."""
        self.search_query = form_data["username"]
        if not self.search_query.strip():
            self.error_message = "Please enter a username."
            return
        yield AppState.fetch_profile

    @rx.event(background=True)
    async def fetch_profile(self):
        """Fetch profile data from Instagram using instaloader."""
        async with self:
            self.is_loading = True
            self.error_message = None
            self.profile_data = None
        try:
            import instaloader
            import humanize

            L = instaloader.Instaloader()
            profile = instaloader.Profile.from_username(L.context, self.search_query)
            if profile.is_private:
                async with self:
                    self.error_message = "Cannot analyze a private profile."
                    self.is_loading = False
                return
            posts_data = []
            total_likes = 0
            total_comments = 0
            post_count = 0
            engagement_data = []
            for post in profile.get_posts():
                if post_count < 12:
                    total_likes += post.likes
                    total_comments += post.comments
                    post_item: Post = {
                        "shortcode": post.shortcode,
                        "display_url": post.url,
                        "likes": post.likes,
                        "comments": post.comments,
                        "caption": post.caption if post.caption else "",
                        "timestamp": int(post.date_utc.timestamp()),
                    }
                    posts_data.append(post_item)
                    engagement_data.append(
                        {
                            "name": post.date_utc.strftime("%b %d"),
                            "likes": post.likes,
                            "comments": post.comments,
                        }
                    )
                    post_count += 1
                else:
                    break
            avg_likes = total_likes / post_count if post_count > 0 else 0
            avg_comments = total_comments / post_count if post_count > 0 else 0
            engagement_rate = (
                (total_likes + total_comments) / post_count / profile.followers * 100
                if profile.followers > 0 and post_count > 0
                else 0
            )
            async with self:
                self.profile_data = {
                    "username": profile.username,
                    "followers": humanize.intword(profile.followers, format="%.1f"),
                    "following": humanize.intword(profile.followees, format="%.1f"),
                    "posts": profile.mediacount,
                    "bio": profile.biography,
                    "profile_pic_url": profile.profile_pic_url,
                    "is_private": profile.is_private,
                    "engagement_rate": round(engagement_rate, 2),
                    "avg_likes": int(avg_likes),
                    "avg_comments": int(avg_comments),
                    "recent_posts": posts_data,
                    "engagement_data": list(reversed(engagement_data)),
                }
                self.is_loading = False
        except Exception as e:
            logging.exception(f"Error fetching profile: {e}")
            async with self:
                self.error_message = (
                    f"Failed to fetch profile: An unexpected error occurred."
                )
                self.is_loading = False
        yield