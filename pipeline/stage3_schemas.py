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
from schemas.ui_schema import UISchema
from schemas.api_schema import APISchema
from schemas.db_schema import DBSchema
from schemas.auth_schema import AuthSchema
from schemas.bundle import SchemaBundle, ValidationIssue
from config import GROQ_API_KEY, TEMPERATURE_SCHEMA, MAX_REPAIR_ATTEMPTS

client = Groq(api_key=GROQ_API_KEY)


def clean_json_response(text: str) -> str:
    text = text.strip()
    text = re.sub(r'^```json\s*', '', text)
    text = re.sub(r'^```\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    return text.strip()


def call_groq(system_prompt: str, user_prompt: str) -> dict:
    attempts = 0
    while attempts < MAX_REPAIR_ATTEMPTS:
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=TEMPERATURE_SCHEMA,
                max_tokens=4096,
                response_format={"type": "json_object"}
            )
            raw = response.choices[0].message.content
            cleaned = clean_json_response(raw)
            time.sleep(3)
            return json.loads(cleaned)
        except Exception as e:
            print(f"Groq call failed: {e}, retrying...")
            attempts += 1
            time.sleep(5)
    raise Exception("Groq call failed after max attempts")


# ─── DB SCHEMA ───────────────────────────────────────────────────────────────

DB_PROMPT = """
You are a database architect. Generate a complete database schema based on the app architecture.

RULES:
- Always respond with valid JSON only
- Every table must have an id column (uuid, primary_key: true)
- Every table must have created_at and updated_at timestamps
- Foreign keys must reference real tables using format "table_name.id"
- Use snake_case for all table and column names
- Tables must be plural (users, contacts, etc.)

RESPOND WITH THIS EXACT STRUCTURE:
{
  "tables": [
    {
      "name": "string",
      "columns": [
        {
          "name": "string",
          "type": "uuid|text|integer|boolean|timestamp|decimal",
          "primary_key": true or false,
          "nullable": true or false,
          "default": null or "string",
          "foreign_key": null or "table.id",
          "unique": true or false
        }
      ],
      "indexes": ["column_name"]
    }
  ]
}

APP ARCHITECTURE:
"""


def generate_db_schema(arch: ArchOutput) -> DBSchema:
    print("Stage 3 — Generating DB schema...")
    arch_summary = f"""
Entities: {arch.entities}
Relations: {[(r.from_entity, r.type, r.to_entity, r.through) for r in arch.relations]}
Business Rules: {arch.business_rules}
"""
    data = call_groq(
        "You are a database architect. Always respond with valid JSON only.",
        DB_PROMPT + arch_summary
    )
    result = DBSchema(**data)
    print("Stage 3 — DB schema generated!")
    return result


# ─── AUTH SCHEMA ─────────────────────────────────────────────────────────────

AUTH_PROMPT = """
You are a security architect. Generate a complete auth schema based on the app architecture.

RULES:
- Always respond with valid JSON only
- Every role must have explicit permissions
- Resources must match entity names from the architecture
- Actions must be from: read, create, update, delete
- One role must have is_default: true

RESPOND WITH THIS EXACT STRUCTURE:
{
  "roles": [
    {
      "name": "string",
      "description": "string",
      "is_default": true or false,
      "permissions": [
        {
          "resource": "string",
          "actions": ["read", "create", "update", "delete"]
        }
      ]
    }
  ],
  "jwt_enabled": true,
  "session_expiry_hours": 24,
  "password_min_length": 8
}

APP ARCHITECTURE:
"""


def generate_auth_schema(arch: ArchOutput) -> AuthSchema:
    print("Stage 3 — Generating Auth schema...")
    arch_summary = f"""
Roles: {arch.role_permissions}
Business Rules: {arch.business_rules}
Entities: {arch.entities}
"""
    data = call_groq(
        "You are a security architect. Always respond with valid JSON only.",
        AUTH_PROMPT + arch_summary
    )
    result = AuthSchema(**data)
    print("Stage 3 — Auth schema generated!")
    return result


# ─── API SCHEMA ──────────────────────────────────────────────────────────────

API_PROMPT = """
You are a backend API architect. Generate a REST API schema.

RULES:
- Always respond with valid JSON only
- Only generate 5-8 most important endpoints (not all CRUD)
- endpoint name must be snake_case
- paths must start with /api/
- Keep response_fields to maximum 3 fields per endpoint
- allowed_roles must match roles from architecture

RESPOND WITH THIS EXACT STRUCTURE:
{
  "endpoints": [
    {
      "name": "string",
      "method": "GET|POST|PUT|PATCH|DELETE",
      "path": "string",
      "description": "string",
      "requires_auth": true or false,
      "allowed_roles": ["string"],
      "request_fields": [],
      "response_fields": [
        {
          "name": "string",
          "type": "string|integer|boolean|uuid",
          "required": true,
          "maps_to_db_column": "string"
        }
      ],
      "db_table": "string"
    }
  ],
  "base_path": "/api",
  "auth_endpoint": "/api/auth/login"
}

APP ARCHITECTURE:

"""


def generate_api_schema(arch: ArchOutput, db: DBSchema) -> APISchema:
    print("Stage 3 — Generating API schema...")
    arch_summary = f"""
Entities: {arch.entities}
Pages: {arch.page_list}
Roles: {[r.role for r in arch.role_permissions]}
DB Tables: {[t.name for t in db.tables]}
DB Columns: { {t.name: [c.name for c in t.columns] for t in db.tables} }
"""
    data = call_groq(
        "You are a backend API architect. Always respond with valid JSON only.",
        API_PROMPT + arch_summary
    )
    result = APISchema(**data)
    print("Stage 3 — API schema generated!")
    return result


# ─── UI SCHEMA ───────────────────────────────────────────────────────────────

UI_PROMPT = """
You are a frontend architect. Generate a UI schema for the app.

RULES:
- Always respond with valid JSON only
- Only generate 4-5 most important pages
- api_calls must reference real endpoint names
- Keep fields to maximum 3 per page
- layout must be: sidebar, topnav, or minimal
- component must be: table, form, card, chart, navbar, sidebar, button, input, or modal

RESPOND WITH THIS EXACT STRUCTURE:
{
  "pages": [
    {
      "name": "string",
      "path": "string",
      "requires_auth": true or false,
      "allowed_roles": [],
      "components": ["table"],
      "fields": [
        {
          "name": "string",
          "label": "string",
          "component": "input",
          "required": true,
          "visible_to_roles": []
        }
      ],
      "api_calls": ["string"]
    }
  ],
  "layout": "sidebar",
  "theme": "light"
}

APP ARCHITECTURE:
"""


def generate_ui_schema(arch: ArchOutput, api: APISchema) -> UISchema:
    print("Stage 3 — Generating UI schema...")
    arch_summary = f"""
Pages: {arch.page_list}
Roles: {[r.role for r in arch.role_permissions]}
API Endpoints: {[e.name for e in api.endpoints]}
API Response Fields: { {e.name: [f.name for f in e.response_fields] for e in api.endpoints} }
"""
    data = call_groq(
        "You are a frontend architect. Always respond with valid JSON only.",
        UI_PROMPT + arch_summary
    )
    result = UISchema(**data)
    print("Stage 3 — UI schema generated!")
    return result


# ─── MAIN FUNCTION ────────────────────────────────────────────────────────────

def generate_schemas(intent: IntentOutput, arch: ArchOutput) -> SchemaBundle:
    print("\n" + "=" * 50)
    print("Stage 3 — Generating all schemas...")
    print("=" * 50)

    db = generate_db_schema(arch)
    auth = generate_auth_schema(arch)
    api = generate_api_schema(arch, db)
    ui = generate_ui_schema(arch, api)

    bundle = SchemaBundle(
        ui=ui,
        api=api,
        db=db,
        auth=auth,
        is_valid=True
    )

    print("\nStage 3 — All schemas generated successfully!")
    return bundle