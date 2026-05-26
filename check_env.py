import os
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("GOOGLE_API_KEY", "NOT FOUND")
print(f"API Key loaded: {key[:10]}...")