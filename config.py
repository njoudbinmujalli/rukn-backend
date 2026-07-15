import os
from google import genai

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.5-flash"
client = genai.Client(api_key=GEMINI_API_KEY)
