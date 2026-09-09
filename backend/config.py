import os
from openai import OpenAI

# تنظیمات اصلی
APP_VERSION = "1.0.0"
APP_NAME = "Eitaa AI Miniapp"

# مدل OpenAI
AI_MODEL = "gpt-4o-mini"
MAX_TOKENS = 1000
TEMPERATURE = 0.7
MAX_HISTORY = 10

# کلاینت OpenAI (سینتکس صحیح نسخه 1.x)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
