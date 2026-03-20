import praw
import time
from datetime import datetime
from config import *

reddit_client = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT,
)


def monitor_brand_mentions():
    """Find all Skeletal PT mentions across Reddit"""
    mentions = []

    for term in BRAND_SEARCH_TERMS:
        try:
            for post in reddit_client.subreddit('all').search(
                term, time_filter='week', limit=25
            ):
                mentions.append({
                    'platform': 'Reddit',
                    'type': 'post',
                    'title': post.title,
                    'url': f"https://reddit.com{post.permalink}",
                    'score': post.score,
                    'subreddit': post.subreddit.display_name,
                    'search_term': term,
                    'created': datetime.fromtimestamp(
                        post.created_utc).isoformat(),
                })
            time.sleep(2)
        except Exception as e:
            print(f"Brand monitor error '{term}': {e}")

    return mentions
