import requests
import json
from openai import OpenAI
from config import *

HEADERS = {
    'User-Agent': 'SkeletalPT Intelligence Bot 1.0',
}

openai_client = OpenAI(api_key=OPENAI_API_KEY)


def get_trending_topics():
    """Identify trending fitness topics and angles for Skeletal PT"""
    top_posts = []

    try:
        url = ("https://www.reddit.com/r/"
               "fitness+weightlifting+bodybuilding+xxfitness"
               "/hot.json?limit=40")
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        for child in data['data']['children']:
            post = child['data']
            top_posts.append({
                'title': post.get('title', ''),
                'score': post.get('score', 0),
                'subreddit': post.get('subreddit', ''),
            })
    except Exception as e:
        print(f"Trend stream error: {e}")
        return []

    posts_text = '\n'.join([
        f"{p['title']} ({p['score']} upvotes, r/{p['subreddit']})"
        for p in top_posts
    ])

    try:
        resp = openai_client.chat.completions.create(
            model=GPT_MODEL,
            messages=[{'role': 'user', 'content':
                f"""These are the top fitness posts on Reddit right now.
{posts_text}

Identify top 5 trending themes this week.
For each theme explain how Skeletal PT (AI skeleton overlay, auto rep counter,
form check, 500 exercises, offline) can create content around it.

Return JSON array only:
[{{
  "theme": str,
  "why_trending": str,
  "skeletal_pt_angle": str,
  "hook": str (max 8 words, stops the scroll),
  "caption": str (1 punchy sentence)
}}]"""}],
            max_tokens=700,
            temperature=0.7,
        )
        clean = resp.choices[0].message.content.strip()
        clean = clean.replace('```json', '').replace('```', '').strip()
        return json.loads(clean)
    except Exception as e:
        print(f"Trend analysis error: {e}")
        return []
