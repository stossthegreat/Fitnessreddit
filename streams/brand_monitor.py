import requests
import time
from datetime import datetime
from config import *

HEADERS = {
    'User-Agent': 'SkeletalPT Intelligence Bot 1.0',
}


def monitor_brand_mentions():
    """Find all Skeletal PT mentions across Reddit"""
    mentions = []

    for term in BRAND_SEARCH_TERMS:
        try:
            url = (f"https://www.reddit.com/search.json"
                   f"?q={requests.utils.quote(term)}&t=week"
                   f"&limit=25&sort=relevance")
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            data = resp.json()

            for child in data['data']['children']:
                post = child['data']
                mentions.append({
                    'platform': 'Reddit',
                    'type': 'post',
                    'title': post.get('title', ''),
                    'url': f"https://reddit.com{post.get('permalink', '')}",
                    'score': post.get('score', 0),
                    'subreddit': post.get('subreddit', ''),
                    'search_term': term,
                    'created': datetime.fromtimestamp(
                        post.get('created_utc', 0)).isoformat(),
                })
            time.sleep(3)
        except Exception as e:
            print(f"Brand monitor error '{term}': {e}")

    return mentions
