import time
from openai import OpenAI
from config import *

openai_client = OpenAI(api_key=OPENAI_API_KEY)


def mine_competitor_reviews():
    """Extract complaint themes from competitor app reviews"""
    results = []

    for app_name, package_id in COMPETITOR_APPS.items():
        try:
            from google_play_scraper import reviews, Sort
            result, _ = reviews(
                package_id,
                lang='en',
                country='us',
                sort=Sort.NEWEST,
                count=300,
            )

            # 1-3 star only
            bad = [r for r in result if r['score'] <= 3]
            texts = '\n'.join([r['content'][:200] for r in bad[:60]])

            themes = _extract_themes(app_name, texts)
            results.append({
                'app': app_name,
                'total_bad_reviews_sampled': len(bad),
                'themes': themes,
                'raw_samples': [r['content'] for r in bad[:5]],
            })
            time.sleep(3)

        except Exception as e:
            print(f"Competitor mine error {app_name}: {e}")

    return results


def _extract_themes(app_name, reviews_text):
    try:
        resp = openai_client.chat.completions.create(
            model=GPT_MODEL,
            messages=[{'role': 'user', 'content':
                f"""These are 1-3 star reviews for {app_name} fitness app.

{reviews_text}

Extract the top 5 complaint themes. For each return JSON with:
- complaint: what users hate
- frequency: how common (high/medium/low)
- skeletal_pt_solution: exactly how Skeletal PT solves this
- content_hook: TikTok hook line using this frustration (max 8 words)
- content_caption: follow-up caption (1 sentence)

Return a JSON array only. No markdown. No explanation."""}],
            max_tokens=800,
            temperature=0.4,
        )
        import json
        clean = resp.choices[0].message.content.strip()
        clean = clean.replace('```json', '').replace('```', '').strip()
        return json.loads(clean)
    except Exception as e:
        print(f"Theme extraction error: {e}")
        return []
