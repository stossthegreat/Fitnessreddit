import json
from datetime import datetime
from openai import OpenAI
from config import *

openai_client = OpenAI(api_key=OPENAI_API_KEY)


def build_master_report(pain_points, opportunities, competitor_data,
                        youtube_insights, trending_topics, brand_mentions,
                        content_calendar, content_ideas, feature_ideas,
                        creator_opportunities):
    """Build the complete weekly intelligence report"""

    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')

    report = {
        'generated_at': timestamp,
        'week': datetime.now().strftime('%Y-W%U'),
        'summary': {
            'pain_points_found': len(pain_points),
            'reddit_opportunities': len(opportunities),
            'competitor_apps_mined': len(competitor_data),
            'youtube_channels_mined': len(youtube_insights),
            'brand_mentions': len(brand_mentions),
            'content_pieces_planned': len(content_calendar),
            'feature_ideas': len(feature_ideas),
            'creator_leads': len(creator_opportunities),
        },
        'top_opportunities': sorted(
            opportunities,
            key=lambda x: x.get('opportunity_score', 0),
            reverse=True
        )[:8],
        'top_pain_points': sorted(
            pain_points,
            key=lambda x: x.get('score', 0),
            reverse=True
        )[:10],
        'trending_topics': trending_topics,
        'content_calendar': content_calendar,
        'content_ideas': content_ideas,
        'competitor_intelligence': competitor_data,
        'youtube_insights': youtube_insights,
        'feature_ideas': feature_ideas,
        'creator_leads': creator_opportunities,
        'brand_mentions': brand_mentions,
    }

    return report


def build_readable_summary(report):
    """Build a human-readable markdown summary"""
    lines = []
    lines.append(f"# SKELETAL PT INTELLIGENCE REPORT")
    lines.append(f"**Generated:** {report['generated_at']}")
    lines.append(f"**Week:** {report['week']}\n")

    s = report['summary']
    lines.append("## THIS WEEK AT A GLANCE")
    lines.append(f"- Reddit pain points found: **{s['pain_points_found']}**")
    lines.append(f"- Reply opportunities: **{s['reddit_opportunities']}**")
    lines.append(f"- Brand mentions: **{s['brand_mentions']}**")
    lines.append(f"- Content pieces planned: **{s['content_pieces_planned']}**")
    lines.append(f"- Feature ideas extracted: **{s['feature_ideas']}**")
    lines.append(f"- Creator leads: **{s['creator_leads']}**\n")

    lines.append("## TOP REPLY OPPORTUNITIES (Post these today)")
    for opp in report['top_opportunities'][:5]:
        lines.append(
            f"\n**[{opp['opportunity_score']}/10]** r/{opp['subreddit']}")
        lines.append(f"Post: _{opp['title']}_")
        lines.append(f"URL: {opp['url']}")
        lines.append(f"Reply: {opp.get('suggested_reply', 'N/A')}")

    lines.append("\n## TOP PAIN POINTS THIS WEEK")
    for p in report['top_pain_points'][:8]:
        lines.append(
            f"- **r/{p['subreddit']}** ({p['score']} upvotes): {p['title']}")

    lines.append("\n## THIS WEEK'S CONTENT CALENDAR")
    for day in report.get('content_calendar', []):
        lines.append(f"\n### {day.get('day')} — {day.get('platform')}")
        lines.append(f"**HOOK:** {day.get('hook')}")
        lines.append(f"**CONCEPT:** {day.get('concept')}")
        lines.append(f"**CAPTION:** {day.get('caption')}")
        lines.append(f"**HASHTAGS:** {' '.join(day.get('hashtags', []))}")
        lines.append(f"**PAIN SOLVED:** {day.get('pain_point_solved')}")
        lines.append(f"**VIRAL MECHANIC:** {day.get('viral_mechanic')}")

    lines.append("\n## COMPETITOR INTELLIGENCE")
    for comp in report.get('competitor_intelligence', []):
        lines.append(f"\n### {comp['app']}")
        for theme in comp.get('themes', [])[:3]:
            lines.append(f"- **{theme.get('complaint')}**"
                         f" [{theme.get('frequency')}]")
            lines.append(f"  -> Solution: {theme.get('skeletal_pt_solution')}")
            lines.append(
                f"  -> Hook: \"{theme.get('content_hook')}\"")

    lines.append("\n## FEATURE IDEAS FROM USER PAIN")
    for feat in report.get('feature_ideas', []):
        lines.append(
            f"\n### {feat.get('feature_name')} — {feat.get('priority')} Priority")
        lines.append(f"**Problem:** {feat.get('user_problem')}")
        lines.append(f"**Viral potential:** {feat.get('viral_potential')}")
        lines.append(f"**Source:** {feat.get('source')}")

    lines.append("\n## CREATOR LEADS THIS WEEK")
    for lead in report.get('creator_leads', [])[:8]:
        lines.append(f"\n**u/{lead.get('username')}** "
                     f"— Score: {lead.get('creator_score')}/10")
        lines.append(f"Post: {lead.get('post_title')}")
        lines.append(f"URL: {lead.get('url')}")
        if lead.get('outreach_message'):
            lines.append(f"DM: {lead.get('outreach_message')}")

    lines.append("\n## BRAND MENTIONS")
    if report.get('brand_mentions'):
        for mention in report['brand_mentions']:
            lines.append(
                f"- **{mention['platform']}** r/{mention.get('subreddit', '')}:"
                f" {mention['title'][:80]}")
            lines.append(f"  {mention['url']}")
    else:
        lines.append("No brand mentions found this week.")

    return '\n'.join(lines)
