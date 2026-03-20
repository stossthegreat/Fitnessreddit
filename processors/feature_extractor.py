import json
from openai import OpenAI
from config import *

openai_client = OpenAI(api_key=OPENAI_API_KEY)


def extract_feature_ideas(pain_points, competitor_data, youtube_insights):
    """Extract feature ideas from real user complaints across all sources"""

    reddit_complaints = '\n'.join([p['title'] for p in pain_points[:20]])

    competitor_complaints = '\n'.join([
        f"{c['app']}: " + ' | '.join([
            t.get('complaint', '') for t in c.get('themes', [])
        ])
        for c in competitor_data
    ])

    youtube_frustrations = '\n'.join([
        f.get('frustration', '')
        for i in youtube_insights
        for f in i.get('insights', {}).get('frustrations', [])
    ])

    try:
        resp = openai_client.chat.completions.create(
            model=GPT_MODEL,
            messages=[{'role': 'user', 'content':
                f"""Based on real user complaints identify 5 features Skeletal PT should build.

REDDIT COMPLAINTS:
{reddit_complaints}

COMPETITOR APP COMPLAINTS:
{competitor_complaints}

YOUTUBE VIEWER FRUSTRATIONS:
{youtube_frustrations}

For each feature return:
- feature_name: short name
- user_problem: exact problem in users' own language
- how_to_build: technical description
- viral_potential: how this creates shareable moments
- priority: High/Medium/Low based on complaint frequency
- source: which platform this came from most

Return JSON array only. No markdown."""}],
            max_tokens=900,
            temperature=0.5,
        )
        clean = resp.choices[0].message.content.strip()
        clean = clean.replace('```json', '').replace('```', '').strip()
        return json.loads(clean)
    except Exception as e:
        print(f"Feature extraction error: {e}")
        return []
