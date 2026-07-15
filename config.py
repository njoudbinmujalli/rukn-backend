import os
from google import genai

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
DB_PATH = "rukn.db"
GEMINI_MODEL = "gemini-2.5-flash"

client = genai.Client(api_key=GEMINI_API_KEY)git add config.py
git commit -m "Fix Gemini config"
git push origin main