from googleapiclient.discovery import build
from openai import OpenAI
import json
from config import *

openai_client = OpenAI(api_key=OPENAI_API_KEY)


def mine_youtube_comments():
    """Mine top fitness YouTube comments for pain points and questions"""
    if not YOUTUBE_API_KEY:
        print("No YouTube API key — skipping YouTube stream")
        return []

    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    all_insights = []

    for channel_name, channel_id in YOUTUBE_CHANNELS.items():
        try:
            # Get latest 5 videos from channel
            videos_resp = youtube.search().list(
                channelId=channel_id,
                part='snippet',
                order='date',
                maxResults=5,
                type='video',
            ).execute()

            for video in videos_resp.get('items', []):
                video_id = video['id']['videoId']
                video_title = video['snippet']['title']

                # Get top comments
                comments_resp = youtube.commentThreads().list(
                    videoId=video_id,
                    part='snippet',
                    order='relevance',
                    maxResults=100,
                ).execute()

                top_comments = []
                for item in comments_resp.get('items', []):
                    comment = item['snippet']['topLevelComment']['snippet']
                    likes = comment.get('likeCount', 0)
                    text = comment.get('textDisplay', '')
                    if likes >= 10 or '?' in text:
                        top_comments.append({
                            'text': text[:300],
                            'likes': likes,
                        })

                if top_comments:
                    insights = _extract_comment_insights(
                        channel_name, video_title, top_comments[:30])
                    all_insights.append({
                        'channel': channel_name,
                        'video': video_title,
                        'video_id': video_id,
                        'insights': insights,
                    })

        except Exception as e:
            print(f"YouTube error {channel_name}: {e}")

    return all_insights


def _extract_comment_insights(channel, video_title, comments):
    comments_text = '\n'.join([
        f"[{c['likes']} likes] {c['text']}" for c in comments
    ])

    try:
        resp = openai_client.chat.completions.create(
            model=GPT_MODEL,
            messages=[{'role': 'user', 'content':
                f"""These are top comments from a fitness YouTube video.
Channel: {channel}
Video: {video_title}

Comments:
{comments_text}

Extract:
1. Top 3 questions people are asking (that Skeletal PT could answer or solve)
2. Top 3 frustrations or pain points mentioned
3. 2 content ideas for Skeletal PT based on what people want

Return JSON only:
{{
  "questions": [{{"question": str, "skeletal_pt_angle": str}}],
  "frustrations": [{{"frustration": str, "frequency": str}}],
  "content_ideas": [{{"hook": str, "concept": str}}]
}}"""}],
            max_tokens=600,
            temperature=0.5,
        )
        clean = resp.choices[0].message.content.strip()
        clean = clean.replace('```json', '').replace('```', '').strip()
        return json.loads(clean)
    except Exception as e:
        print(f"Comment insight error: {e}")
        return {}
