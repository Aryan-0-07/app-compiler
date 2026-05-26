import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
MODEL = "llama-3.3-70b-versatile"
MAX_TOKENS = 4096
TEMPERATURE_SCHEMA = 0.0
TEMPERATURE_DESIGN = 0.3
MAX_REPAIR_ATTEMPTS = 3