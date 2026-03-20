import json
import os
from datetime import datetime

try:
    from supabase import create_client
    SUPABASE_AVAILABLE = True
except Exception:
    SUPABASE_AVAILABLE = False

from config import SUPABASE_URL, SUPABASE_KEY, SLACK_WEBHOOK_URL
import requests


def save_report(report, summary_md):
    """Save report to disk and optionally Supabase + Slack"""

    # Always save locally
    os.makedirs('reports', exist_ok=True)
    timestamp = report['generated_at']

    json_path = f"reports/intelligence_{timestamp}.json"
    md_path = f"reports/intelligence_{timestamp}.md"

    with open(json_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)

    with open(md_path, 'w') as f:
        f.write(summary_md)

    print(f"Report saved: {json_path}")
    print(f"Summary saved: {md_path}")

    # Save to Supabase if configured
    if SUPABASE_AVAILABLE and SUPABASE_URL and SUPABASE_KEY:
        try:
            client = create_client(SUPABASE_URL, SUPABASE_KEY)
            client.table('intelligence_reports').insert({
                'week': report['week'],
                'generated_at': report['generated_at'],
                'summary': report['summary'],
                'report_json': json.dumps(report, default=str),
                'report_markdown': summary_md,
            }).execute()
            print("Report saved to Supabase")
        except Exception as e:
            print(f"Supabase save error: {e}")

    # Send Slack notification if configured
    if SLACK_WEBHOOK_URL:
        try:
            s = report['summary']
            slack_msg = {
                'text': (
                    f"*Skeletal PT Intelligence Report — {report['week']}*\n"
                    f"- {s['pain_points_found']} pain points\n"
                    f"- {s['reddit_opportunities']} reply opportunities\n"
                    f"- {s['content_pieces_planned']} content pieces planned\n"
                    f"- {s['feature_ideas']} feature ideas\n"
                    f"- {s['creator_leads']} creator leads\n"
                    f"- {s['brand_mentions']} brand mentions"
                )
            }
            requests.post(SLACK_WEBHOOK_URL, json=slack_msg, timeout=10)
            print("Slack notification sent")
        except Exception as e:
            print(f"Slack notification error: {e}")
