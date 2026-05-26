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
from schemas.architecture import ArchOutput
from config import GROQ_API_KEY, TEMPERATURE_DESIGN, MAX_REPAIR_ATTEMPTS

client = Groq(api_key=GROQ_API_KEY)

ARCHITECTURE_PROMPT = """
You are an expert software architect. You will receive a structured app intent and must design the full application architecture.

RULES:
- Always respond with valid JSON only
- No extra text, no markdown, no code blocks
- Entity names must be in snake_case plural (e.g. "users", "contacts")
- Page names must be in snake_case (e.g. "dashboard", "contact_list")
- Relations must reference valid entity names
- Every role must have explicit permissions defined

RESPOND WITH THIS EXACT JSON STRUCTURE:
{
  "entities": ["string"],
  "relations": [
    {
      "from_entity": "string",
      "to_entity": "string",
      "type": "one_to_many|many_to_many|one_to_one",
      "through": null or "string"
    }
  ],
  "role_permissions": [
    {
      "role": "string",
      "can_create": ["string"],
      "can_read": ["string"],
      "can_update": ["string"],
      "can_delete": ["string"]
    }
  ],
  "flows": [
    {
      "name": "string",
      "steps": ["string"],
      "involves_payment": true or false
    }
  ],
  "business_rules": ["string"],
  "page_list": ["string"]
}

APP INTENT:
"""


def clean_json_response(text: str) -> str:
    text = text.strip()
    text = re.sub(r'^```json\s*', '', text)
    text = re.sub(r'^```\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    return text.strip()


def design_architecture(intent: IntentOutput) -> ArchOutput:
    attempts = 0
    last_error = None

    intent_summary = f"""
App Name: {intent.app_name}
Description: {intent.app_description}
Entities: {[e.name for e in intent.entities]}
Roles: {intent.roles}
Features: {[f.name for f in intent.features]}
Auth Required: {intent.auth_required}
Payment Required: {intent.payment_required}
Multi Tenant: {intent.multi_tenant}
Assumptions: {intent.assumptions}
"""

    while attempts < MAX_REPAIR_ATTEMPTS:
        try:
            print(f"Stage 2 — Designing architecture (attempt {attempts + 1})...")

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert software architect. Always respond with valid JSON only. No markdown, no code blocks, no extra text."
                    },
                    {
                        "role": "user",
                        "content": ARCHITECTURE_PROMPT + intent_summary
                    }
                ],
                temperature=TEMPERATURE_DESIGN,
                max_tokens=4096,
                response_format={"type": "json_object"}
            )

            raw_text = response.choices[0].message.content
            cleaned = clean_json_response(raw_text)
            data = json.loads(cleaned)
            result = ArchOutput(**data)

            print("Stage 2 — Architecture designed successfully!")
            return result

        except json.JSONDecodeError as e:
            last_error = f"Invalid JSON: {e}"
            print(f"Stage 2 — JSON error, retrying... ({last_error})")
            attempts += 1
            time.sleep(5)

        except Exception as e:
            last_error = f"Validation error: {e}"
            print(f"Stage 2 — Validation error, retrying... ({last_error})")
            attempts += 1
            time.sleep(5)

    raise Exception(f"Stage 2 failed after {MAX_REPAIR_ATTEMPTS} attempts. Last error: {last_error}")