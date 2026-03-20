import praw
import time
from datetime import datetime
from openai import OpenAI
from config import *

reddit_client = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT,
)
openai_client = OpenAI(api_key=OPENAI_API_KEY)


def scan_pain_points(hours_back=48):
    """Scan Reddit for real user pain points Skeletal PT solves"""
    pain_points = []
    opportunities = []

    for sub_name in SUBREDDITS:
        try:
            sub = reddit_client.subreddit(sub_name)
            for post in sub.hot(limit=75):
                age_hours = (time.time() - post.created_utc) / 3600
                if age_hours > hours_back:
                    continue

                text = f"{post.title} {post.selftext}".lower()

                for keyword in PAIN_POINT_KEYWORDS:
                    if keyword in text and post.score >= 30:
                        pain_points.append({
                            'subreddit': sub_name,
                            'title': post.title,
                            'body_preview': post.selftext[:300],
                            'score': post.score,
                            'comments': post.num_comments,
                            'url': f"https://reddit.com{post.permalink}",
                            'keyword_matched': keyword,
                            'created': datetime.fromtimestamp(
                                post.created_utc).isoformat(),
                        })

                        # Score as opportunity
                        opp_score = _score_opportunity(post.title,
                                                       post.selftext[:400])
                        if opp_score >= 7:
                            reply = _generate_reply(post.title,
                                                    post.selftext[:300])
                            opportunities.append({
                                **pain_points[-1],
                                'opportunity_score': opp_score,
                                'suggested_reply': reply,
                            })
                        break

            time.sleep(2)
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
