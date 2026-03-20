import requests
import json
from openai import OpenAI
from config import *

HEADERS = {
    'User-Agent': 'SkeletalPT Intelligence Bot 1.0',
}

openai_client = OpenAI(api_key=OPENAI_API_KEY)

FORM_CHECK_SUBREDDITS = ['formcheck', 'weightlifting', 'powerlifting']


def find_creator_opportunities():
    """Find Reddit users who post form checks — potential micro-creators"""
    opportunities = []

    for sub_name in FORM_CHECK_SUBREDDITS:
        try:
            url = f"https://www.reddit.com/r/{sub_name}/hot.json?limit=30"
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            data = resp.json()

            import time
            time.sleep(3)

            for child in data['data']['children']:
                post = child['data']
                title = post.get('title', '')

                if any(kw in title.lower() for kw in
                       ['form check', 'rate my', 'how does my']):
                    score = _score_creator_potential(post)
                    if score >= 6:
                        opportunities.append({
                            'username': post.get('author', '[deleted]'),
                            'post_title': title,
                            'post_score': post.get('score', 0),
                            'creator_score': score,
                            'url': f"https://reddit.com{post.get('permalink', '')}",
                            'subreddit': sub_name,
                        })
        except Exception as e:
            print(f"Influencer finder error r/{sub_name}: {e}")

    return sorted(opportunities,
                  key=lambda x: x['creator_score'], reverse=True)[:20]


def _score_creator_potential(post):
    """Score a Reddit user's potential as a Skeletal PT creator"""
    score = 0
    post_score = post.get('score', 0)
    num_comments = post.get('num_comments', 0)
    url = post.get('url', '')

    if post_score > 100:
        score += 3
    elif post_score > 50:
        score += 2
    elif post_score > 20:
        score += 1

    if num_comments > 20:
        score += 2
    elif num_comments > 10:
        score += 1

    if any(ext in url for ext in ['.mp4', '.gif', 'youtube', 'youtu.be',
                                   'streamable', 'imgur', 'v.redd.it']):
        score += 3

    return score


def generate_outreach_messages(opportunities):
    """Generate personalised outreach for top creator opportunities"""
    messages = []

    for opp in opportunities[:10]:
        try:
            resp = openai_client.chat.completions.create(
                model=GPT_MODEL,
                messages=[{'role': 'user', 'content':
                    f"""Write a short Reddit DM to this person about Skeletal PT.
They posted: "{opp['post_title']}"
They are interested in form and filming themselves training.

Skeletal PT overlays a glowing skeleton on their body while they train,
counts reps automatically, checks form depth. Free to download.
We are looking for people to try it and share their honest reaction.

Write a genuine DM. Under 4 sentences. Sound human. No hype. Reference their post.
Offer a free Pro account in exchange for trying it and posting their reaction."""}],
                max_tokens=150,
                temperature=0.7,
            )
            messages.append({
                **opp,
                'outreach_message': resp.choices[0].message.content.strip(),
            })
        except Exception as e:
            print(f"Outreach generation error: {e}")

    return messages
