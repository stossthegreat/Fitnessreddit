import praw
import json
from openai import OpenAI
from config import *

reddit_client = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT,
)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

FORM_CHECK_SUBREDDITS = ['formcheck', 'weightlifting', 'powerlifting']


def find_creator_opportunities():
    """Find Reddit users who post form checks — potential micro-creators"""
    opportunities = []

    for sub_name in FORM_CHECK_SUBREDDITS:
        try:
            sub = reddit_client.subreddit(sub_name)
            for post in sub.hot(limit=30):
                # Form check posts = people who film themselves training
                # These are potential creators
                if any(kw in post.title.lower() for kw in
                       ['form check', 'rate my', 'how does my']):
                    score = _score_creator_potential(post)
                    if score >= 6:
                        opportunities.append({
                            'username': str(post.author),
                            'post_title': post.title,
                            'post_score': post.score,
                            'creator_score': score,
                            'url': f"https://reddit.com{post.permalink}",
                            'subreddit': sub_name,
                        })
        except Exception as e:
            print(f"Influencer finder error r/{sub_name}: {e}")

    return sorted(opportunities,
                  key=lambda x: x['creator_score'], reverse=True)[:20]


def _score_creator_potential(post):
    """Score a Reddit user's potential as a Skeletal PT creator"""
    score = 0
    if post.score > 100:
        score += 3
    elif post.score > 50:
        score += 2
    elif post.score > 20:
        score += 1

    if post.num_comments > 20:
        score += 2
    elif post.num_comments > 10:
        score += 1

    # Check if they post videos (linked media)
    if hasattr(post, 'url') and any(
        ext in post.url for ext in ['.mp4', '.gif', 'youtube', 'youtu.be',
                                     'streamable', 'imgur']
    ):
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
