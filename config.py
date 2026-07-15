import os
from google import genai

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6LzYuT5Dvkx51wIZxERZbWc55vZG_cbor3o5YTfTnZ88w")
DB_PATH = "rukn.db"
GEMINI_MODEL = "gemini-2.5-flash"

client = genai.Client(api_key=GEMINI_API_KEY)