
from google import genai


GEMINI_API_KEY = "YOUR_API_KEY_HERE"

DB_PATH = "rukn.db"
GEMINI_MODEL = "gemini-2.5-flash"

client = genai.Client(api_key=GEMINI_API_KEY)
