import json
from openai import OpenAI
from config import *

openai_client = OpenAI(api_key=OPENAI_API_KEY)


def generate_weekly_calendar(pain_points, competitor_data,
                              youtube_insights, trending_topics):
    """Generate a 7-day content calendar from all intelligence gathered"""

    # Build context
    pain_summary = '\n'.join([p['title'] for p in pain_points[:12]])

    competitor_summary = '\n'.join([
        f"{c['app']}: " + ', '.join([
            t.get('complaint', '') for t in c.get('themes', [])[:3]
        ])
        for c in competitor_data
    ])

    youtube_summary = '\n'.join([
        f"{i['channel']}: " + ', '.join([
            q.get('question', '')
            for q in i.get('insights', {}).get('questions', [])[:2]
        ])
        for i in youtube_insights[:4]
    ])

    trending_summary = '\n'.join([
        f"{t.get('theme', '')}: {t.get('skeletal_pt_angle', '')}"
        for t in trending_topics[:4]
    ])

    prompt = f"""Create a 7-day content calendar for Skeletal PT.

ABOUT THE APP:
- Real-time AI skeleton overlay on body during workout via phone camera
- Automatically counts every rep across 500+ exercises
- Skeleton gauge only counts rep when correct depth/form achieved
- 100% offline — no internet, no wearables
- Power levels, 162 trophies, streaks
- Free to start — works anywhere
- Looks like nothing else in fitness

REAL PAIN POINTS FROM REDDIT THIS WEEK:
{pain_summary}

WHAT COMPETITOR USERS COMPLAIN ABOUT:
{competitor_summary}

WHAT FITNESS YOUTUBE VIEWERS ARE ASKING:
{youtube_summary}

TRENDING FITNESS TOPICS RIGHT NOW:
{trending_summary}

Create 7 pieces of content (one per day, Mon-Sun).
Each must be filmable with a phone, feature the skeleton visually,
solve a REAL pain point from the data above.

For each return:
- day: Monday/Tuesday etc
- platform: TikTok / Instagram Reels / YouTube Shorts
- hook: First 2 seconds — max 8 words — stops the scroll
- concept: What actually happens in the video (2 sentences)
- caption: The actual post caption — punchy, creates FOMO or curiosity
- hashtags: 5 relevant hashtags
- pain_point_solved: Which exact Reddit/YouTube complaint this addresses
- viral_mechanic: Why people will share or comment this specific video

Return a JSON array only. No markdown. No explanation."""

    try:
        resp = openai_client.chat.completions.create(
            model=GPT_MODEL,
            messages=[{'role': 'user', 'content': prompt}],
            max_tokens=2000,
            temperature=0.8,
        )
        clean = resp.choices[0].message.content.strip()
        clean = clean.replace('```json', '').replace('```', '').strip()
        return json.loads(clean)
    except Exception as e:
        print(f"Calendar generation error: {e}")
        return []


def generate_content_ideas_from_pain(pain_points):
    """Extract viral content ideas directly from pain points"""
    pain_text = '\n'.join([p['title'] for p in pain_points[:20]])

    try:
        resp = openai_client.chat.completions.create(
            model=GPT_MODEL,
            messages=[{'role': 'user', 'content':
                f"""You are the marketing brain for Skeletal PT.
Real Reddit posts from gym users this week:
{pain_text}

Extract 5 viral video ideas that directly address these pain points.
Each idea must show the Skeletal PT skeleton solving the exact problem.

Return JSON array:
[{{
  "hook": str (max 8 words),
  "concept": str (2 sentences),
  "caption": str (punchy, under 10 words),
  "pain_point_solved": str,
  "expected_reaction": str (what people will comment/share)
}}]"""}],
            max_tokens=900,
            temperature=0.8,
        )
        clean = resp.choices[0].message.content.strip()
        clean = clean.replace('```json', '').replace('```', '').strip()
        return json.loads(clean)
    except Exception as e:
        print(f"Content idea error: {e}")
        return []
