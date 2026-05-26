import json
import re
import os
import sys
import time
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from groq import Groq
from schemas.intent import IntentOutput
from config import GROQ_API_KEY, TEMPERATURE_SCHEMA, MAX_REPAIR_ATTEMPTS

client = Groq(api_key=GROQ_API_KEY)

INTENT_PROMPT = """
You are an expert software architect. A user will describe an app they want to build.
Your job is to extract their intent into a strict JSON format.

RULES:
- Always respond with valid JSON only
- No extra text, no markdown, no code blocks
- If the prompt is too vague, set clarification_needed with questions
- Make reasonable assumptions and document them in assumptions list
- Identify all entities, roles, and features from the prompt

RESPOND WITH THIS EXACT JSON STRUCTURE:
{
  "app_name": "string",
  "app_description": "string",
  "entities": [
    {
      "name": "string",
      "description": "string",
      "is_primary": true or false,
      "has_ownership": true or false
    }
  ],
  "roles": ["string"],
  "features": [
    {
      "name": "string",
      "category": "auth|crud|dashboard|payments|notifications|search|analytics|file_upload|other",
      "description": "string",
      "requires_auth": true or false
    }
  ],
  "auth_required": true or false,
  "payment_required": true or false,
  "multi_tenant": true or false,
  "assumptions": ["string"],
  "clarification_needed": null or {
    "questions": ["string"],
    "reason": "string"
  }
}

USER PROMPT:
"""


def clean_json_response(text: str) -> str:
    text = text.strip()
    text = re.sub(r'^```json\s*', '', text)
    text = re.sub(r'^```\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    return text.strip()


def extract_intent(user_prompt: str) -> IntentOutput:
    attempts = 0
    last_error = None

    while attempts < MAX_REPAIR_ATTEMPTS:
        try:
            print(f"Stage 1 — Extracting intent (attempt {attempts + 1})...")

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert software architect. Always respond with valid JSON only. No markdown, no code blocks, no extra text."
                    },
                    {
                        "role": "user",
                        "content": INTENT_PROMPT + user_prompt
                    }
                ],
                temperature=TEMPERATURE_SCHEMA,
                max_tokens=4096,
                response_format={"type": "json_object"}
            )

            raw_text = response.choices[0].message.content
            cleaned = clean_json_response(raw_text)
            data = json.loads(cleaned)
            result = IntentOutput(**data)

            print("Stage 1 — Intent extracted successfully!")
            return result

        except json.JSONDecodeError as e:
            last_error = f"Invalid JSON: {e}"
            print(f"Stage 1 — JSON error, retrying... ({last_error})")
            attempts += 1
            time.sleep(5)

        except Exception as e:
            last_error = f"Validation error: {e}"
            print(f"Stage 1 — Validation error, retrying... ({last_error})")
            attempts += 1
            time.sleep(5)

    raise Exception(f"Stage 1 failed after {MAX_REPAIR_ATTEMPTS} attempts. Last error: {last_error}")