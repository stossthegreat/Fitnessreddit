import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')
PORT = int(os.getenv('PORT', 8080))

# Reddit config
SUBREDDITS = [
    'fitness',
    'weightlifting',
    'bodybuilding',
    'xxfitness',
    'bodyweightfitness',
    'homegym',
    'powerlifting',
    'beginnerfitness',
    'loseit',
    'gainit',
]

PAIN_POINT_KEYWORDS = [
    'form check', 'is my form', 'check my form', 'rate my form',
    'why am i not', 'not progressing', 'stuck at', 'plateau',
    'losing count', 'forgot my reps', 'lost count',
    'app sucks', 'hevy', 'strong app', 'fitbod', 'myfitnesspal',
    'cant tell', 'dont know if', 'how do i know',
    'squat depth', 'hip hinge', 'proper form', 'bad form',
    'am i doing this right', 'without a trainer', 'train alone',
    'no spotter', 'counting reps', 'rep counter',
]

COMPETITOR_APPS = {
    'Hevy': 'com.hevy.app',
    'Strong': 'me.strong.app',
    'Fitbod': 'fitbod.me.app',
}

# YouTube channels to mine
YOUTUBE_CHANNELS = {
    'Jeff Nippard': 'UC68TLK0mAEzUyHx5x5k-S1Q',
    'Alan Thrall': 'UCe0TLA0EsQbE-MjuHXevran',
    'Athlean-X': 'UCe0TLA0EsQbE-MjuHXevran',
    'Renaissance Periodization': 'UCfQgsKhHjSyRLOp9mnffqVg',
}

BRAND_SEARCH_TERMS = [
    'Skeletal PT',
    'SkeletalPT',
    'skeleton fitness app',
    'skeleton rep counter',
    'AI skeleton workout',
]

# OpenAI model
GPT_MODEL = 'gpt-4o-mini'
