import requests
import time
from datetime import datetime
from openai import OpenAI
from config import *

HEADERS = {
    'User-Agent': 'SkeletalPT Intelligence Bot 1.0',
}

openai_client = OpenAI(api_key=OPENAI_API_KEY)


def _fetch_subreddit_hot(sub_name, limit=75):
    """Fetch hot posts from a subreddit using public JSON endpoint"""
    url = f"https://www.reddit.com/r/{sub_name}/hot.json?limit={limit}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return [child['data'] for child in data['data']['children']]
    except Exception as e:
        print(f"Reddit fetch error r/{sub_name}: {e}")
        return []


def _search_reddit(query, time_filter='week', limit=25):
    """Search all of Reddit using public JSON endpoint"""
    url = (f"https://www.reddit.com/search.json"
           f"?q={requests.utils.quote(query)}&t={time_filter}"
           f"&limit={limit}&sort=relevance")
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return [child['data'] for child in data['data']['children']]
    except Exception as e:
        print(f"Reddit search error '{query}': {e}")
        return []


def scan_pain_points(hours_back=48):
    """Scan Reddit for real user pain points Skeletal PT solves"""
    pain_points = []
    opportunities = []

    for sub_name in SUBREDDITS:
        try:
            posts = _fetch_subreddit_hot(sub_name, limit=75)

            for post in posts:
                age_hours = (time.time() - post.get('created_utc', 0)) / 3600
                if age_hours > hours_back:
                    continue

                title = post.get('title', '')
                selftext = post.get('selftext', '')
                text = f"{title} {selftext}".lower()
                score = post.get('score', 0)
                permalink = post.get('permalink', '')

                for keyword in PAIN_POINT_KEYWORDS:
                    if keyword in text and score >= 30:
                        pain_points.append({
                            'subreddit': sub_name,
                            'title': title,
                            'body_preview': selftext[:300],
                            'score': score,
                            'comments': post.get('num_comments', 0),
                            'url': f"https://reddit.com{permalink}",
                            'keyword_matched': keyword,
                            'created': datetime.fromtimestamp(
                                post.get('created_utc', 0)).isoformat(),
                        })

                        opp_score = _score_opportunity(title, selftext[:400])
                        if opp_score >= 7:
                            reply = _generate_reply(title, selftext[:300])
                            opportunities.append({
                                **pain_points[-1],
                                'opportunity_score': opp_score,
                                'suggested_reply': reply,
                            })
                        break

            time.sleep(3)
        except Exception as e:
            print(f"Reddit error r/{sub_name}: {e}")

    return pain_points, opportunities


def _score_opportunity(title, body):
    try:
        resp = openai_client.chat.completions.create(
            model=GPT_MODEL,
            messages=[{'role': 'user', 'content':
                f"""Score 1-10 how well Skeletal PT solves this person's problem.
Skeletal PT = AI phone camera that overlays skeleton on body, counts reps automatically,
checks form depth, 500+ exercises, 100% offline, no wearables.
10 = this person desperately needs exactly this.
Return only a single integer.

Post: {title}
Body: {body}"""}],
            max_tokens=5,
            temperature=0.1,
        )
        return int(resp.choices[0].message.content.strip())
    except Exception:
        return 0


def _generate_reply(title, body):
    try:
        resp = openai_client.chat.completions.create(
            model=GPT_MODEL,
            messages=[{'role': 'user', 'content':
                f"""Write a genuine Reddit reply. Be helpful first.
Mention Skeletal PT only if completely natural and directly relevant.
Sound like a real person. Under 3 sentences. Never sound like an ad.

Post: {title}
Body: {body}"""}],
            max_tokens=120,
            temperature=0.7,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return ''
