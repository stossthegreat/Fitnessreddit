"""
SKELETAL PT INTELLIGENCE ENGINE
Runs permanently on Railway.
Full report every Monday 7am.
Daily brand monitor every day 9am.
Health check endpoint on PORT.
"""

import os
import json
import threading
import schedule
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

from streams.reddit_stream import scan_pain_points
from streams.competitor_stream import mine_competitor_reviews
from streams.youtube_stream import mine_youtube_comments
from streams.trend_stream import get_trending_topics
from streams.brand_monitor import monitor_brand_mentions
from processors.content_generator import (
    generate_weekly_calendar,
    generate_content_ideas_from_pain,
)
from processors.feature_extractor import extract_feature_ideas
from processors.influencer_finder import (
    find_creator_opportunities,
    generate_outreach_messages,
)
from processors.report_builder import build_master_report, build_readable_summary
from storage.report_store import save_report
from config import PORT

# ═══════════════════════════════
# HEALTH CHECK SERVER
# ═══════════════════════════════

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'status': 'healthy',
                'service': 'skeletal-pt-intelligence-engine',
                'timestamp': datetime.now().isoformat(),
            }).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress access logs


def run_health_server():
    server = HTTPServer(('0.0.0.0', PORT), HealthHandler)
    print(f"Health check running on port {PORT}")
    server.serve_forever()


# ═══════════════════════════════
# FULL WEEKLY REPORT
# ═══════════════════════════════

def run_full_report():
    print(f"\n{'='*60}")
    print(f"SKELETAL PT INTELLIGENCE ENGINE — FULL REPORT")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}\n")

    try:
        print("Stream 1/5: Scanning Reddit for pain points...")
        pain_points, opportunities = scan_pain_points(hours_back=72)
        print(f"  Found {len(pain_points)} pain points, "
              f"{len(opportunities)} opportunities")

        print("Stream 2/5: Mining competitor reviews...")
        competitor_data = mine_competitor_reviews()
        print(f"  Mined {len(competitor_data)} competitor apps")

        print("Stream 3/5: Mining YouTube comments...")
        youtube_insights = mine_youtube_comments()
        print(f"  Mined {len(youtube_insights)} videos")

        print("Stream 4/5: Identifying trending topics...")
        trending_topics = get_trending_topics()
        print(f"  Found {len(trending_topics)} trends")

        print("Stream 5/5: Brand monitoring...")
        brand_mentions = monitor_brand_mentions()
        print(f"  Found {len(brand_mentions)} mentions")

        print("\nProcessing: Generating content calendar...")
        content_calendar = generate_weekly_calendar(
            pain_points, competitor_data, youtube_insights, trending_topics)

        print("Processing: Extracting content ideas...")
        content_ideas = generate_content_ideas_from_pain(pain_points)

        print("Processing: Extracting feature ideas...")
        feature_ideas = extract_feature_ideas(
            pain_points, competitor_data, youtube_insights)

        print("Processing: Finding creator opportunities...")
        raw_leads = find_creator_opportunities()
        creator_leads = generate_outreach_messages(raw_leads)
        print(f"  Found {len(creator_leads)} creator leads")

        print("\nBuilding master report...")
        report = build_master_report(
            pain_points=pain_points,
            opportunities=opportunities,
            competitor_data=competitor_data,
            youtube_insights=youtube_insights,
            trending_topics=trending_topics,
            brand_mentions=brand_mentions,
            content_calendar=content_calendar,
            content_ideas=content_ideas,
            feature_ideas=feature_ideas,
            creator_opportunities=creator_leads,
        )

        summary_md = build_readable_summary(report)
        save_report(report, summary_md)

        print(f"\nFULL REPORT COMPLETE")
        print(f"{'='*60}\n")

    except Exception as e:
        print(f"Full report error: {e}")
        import traceback
        traceback.print_exc()


# ═══════════════════════════════
# DAILY MONITOR (lighter check)
# ═══════════════════════════════

def run_daily_monitor():
    print(f"\nDaily monitor — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    try:
        mentions = monitor_brand_mentions()
        pain_points, opportunities = scan_pain_points(hours_back=26)

        print(f"Brand mentions today: {len(mentions)}")
        print(f"New pain points: {len(pain_points)}")
        print(f"Reply opportunities: {len(opportunities)}")

        if mentions:
            print("\nBRAND MENTIONS:")
            for m in mentions:
                print(f"  - {m['title'][:70]}")
                print(f"    {m['url']}")

        if opportunities:
            print("\nTOP OPPORTUNITIES:")
            top = sorted(opportunities,
                         key=lambda x: x.get('opportunity_score', 0),
                         reverse=True)[:3]
            for opp in top:
                print(f"  [{opp['opportunity_score']}/10] {opp['title'][:60]}")
                print(f"    {opp['url']}")
                if opp.get('suggested_reply'):
                    print(f"    Reply: {opp['suggested_reply'][:100]}...")

    except Exception as e:
        print(f"Daily monitor error: {e}")


# ═══════════════════════════════
# SCHEDULER + ENTRY POINT
# ═══════════════════════════════

if __name__ == '__main__':
    print("SKELETAL PT INTELLIGENCE ENGINE STARTING")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    # Start health check server in background thread
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()

    # Run full report immediately on first start
    print("Running initial full report on startup...")
    run_full_report()

    # Schedule weekly full report — Monday 7am
    schedule.every().monday.at("07:00").do(run_full_report)

    # Schedule daily monitor — every day 9am
    schedule.every().day.at("09:00").do(run_daily_monitor)

    # Additional mid-week competitor scan — Thursday 7am
    schedule.every().thursday.at("07:00").do(mine_competitor_reviews)

    print("\nScheduler running:")
    print("  - Full report: Every Monday at 07:00")
    print("  - Daily monitor: Every day at 09:00")
    print("  - Competitor scan: Every Thursday at 07:00")
    print(f"  - Health check: http://0.0.0.0:{PORT}/health")
    print("\nPress Ctrl+C to stop.\n")

    while True:
        schedule.run_pending()
        time.sleep(30)
