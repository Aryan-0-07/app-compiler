import json
import re
import os
import sys
import time
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from groq import Groq
from schemas.bundle import SchemaBundle, ValidationIssue
from schemas.api_schema import APISchema
from schemas.ui_schema import UISchema
from schemas.db_schema import DBSchema
from config import GROQ_API_KEY, TEMPERATURE_SCHEMA, MAX_REPAIR_ATTEMPTS

client = Groq(api_key=GROQ_API_KEY)


def clean_json_response(text: str) -> str:
    text = text.strip()
    text = re.sub(r'^```json\s*', '', text)
    text = re.sub(r'^```\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    return text.strip()


def repair_api_schema(bundle: SchemaBundle, issues: list[ValidationIssue]) -> APISchema:
    """Repair only the API schema based on issues found"""
    print("  Repairing API schema...")

    issue_descriptions = [i.message for i in issues]
    db_tables = {t.name: [c.name for c in t.columns] for t in bundle.db.tables}
    auth_roles = bundle.auth.get_role_names()

    prompt = f"""
You are an API architect. Fix the following API schema issues and return a corrected API schema.

ISSUES TO FIX:
{json.dumps(issue_descriptions, indent=2)}

CURRENT API SCHEMA:
{json.dumps(bundle.api.model_dump(), indent=2)}

VALID DB TABLES AND COLUMNS:
{json.dumps(db_tables, indent=2)}

VALID AUTH ROLES:
{json.dumps(auth_roles, indent=2)}

Return ONLY the fixed API schema JSON. Same structure, all issues resolved.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are an API architect. Return valid JSON only."},
            {"role": "user", "content": prompt}
        ],
        temperature=TEMPERATURE_SCHEMA,
        max_tokens=4096,
        response_format={"type": "json_object"}
    )

    raw = response.choices[0].message.content
    cleaned = clean_json_response(raw)
    data = json.loads(cleaned)
    return APISchema(**data)


def repair_ui_schema(bundle: SchemaBundle, issues: list[ValidationIssue]) -> UISchema:
    """Repair only the UI schema based on issues found"""
    print("  Repairing UI schema...")

    issue_descriptions = [i.message for i in issues]
    endpoint_names = [e.name for e in bundle.api.endpoints]
    auth_roles = bundle.auth.get_role_names()

    prompt = f"""
You are a frontend architect. Fix the following UI schema issues and return a corrected UI schema.

ISSUES TO FIX:
{json.dumps(issue_descriptions, indent=2)}

CURRENT UI SCHEMA:
{json.dumps(bundle.ui.model_dump(), indent=2)}

VALID API ENDPOINTS:
{json.dumps(endpoint_names, indent=2)}

VALID AUTH ROLES:
{json.dumps(auth_roles, indent=2)}

Return ONLY the fixed UI schema JSON. Same structure, all issues resolved.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a frontend architect. Return valid JSON only."},
            {"role": "user", "content": prompt}
        ],
        temperature=TEMPERATURE_SCHEMA,
        max_tokens=4096,
        response_format={"type": "json_object"}
    )

    raw = response.choices[0].message.content
    cleaned = clean_json_response(raw)
    data = json.loads(cleaned)
    return UISchema(**data)


def repair_db_schema(bundle: SchemaBundle, issues: list[ValidationIssue]) -> DBSchema:
    """Repair only the DB schema based on issues found"""
    print("  Repairing DB schema...")

    issue_descriptions = [i.message for i in issues]

    prompt = f"""
You are a database architect. Fix the following DB schema issues and return a corrected DB schema.

ISSUES TO FIX:
{json.dumps(issue_descriptions, indent=2)}

CURRENT DB SCHEMA:
{json.dumps(bundle.db.model_dump(), indent=2)}

Return ONLY the fixed DB schema JSON. Same structure, all issues resolved.
Every table must have id (uuid), created_at (timestamp), updated_at (timestamp).
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a database architect. Return valid JSON only."},
            {"role": "user", "content": prompt}
        ],
        temperature=TEMPERATURE_SCHEMA,
        max_tokens=4096,
        response_format={"type": "json_object"}
    )

    raw = response.choices[0].message.content
    cleaned = clean_json_response(raw)
    data = json.loads(cleaned)
    return DBSchema(**data)


def run_repair(bundle: SchemaBundle) -> SchemaBundle:
    """Surgically repair only the layers that have issues"""
    print("\nStarting repair engine...")

    api_issues = [i for i in bundle.validation_issues if i.layer == "api"]
    ui_issues = [i for i in bundle.validation_issues if i.layer == "ui"]
    db_issues = [i for i in bundle.validation_issues if i.layer == "db"]

    if db_issues:
        print(f"  Found {len(db_issues)} DB issues — repairing...")
        bundle.db = repair_db_schema(bundle, db_issues)

    if api_issues:
        print(f"  Found {len(api_issues)} API issues — repairing...")
        bundle.api = repair_api_schema(bundle, api_issues)

    if ui_issues:
        print(f"  Found {len(ui_issues)} UI issues — repairing...")
        bundle.ui = repair_ui_schema(bundle, ui_issues)

    bundle.repair_attempts += 1
    print(f"  Repair attempt {bundle.repair_attempts} complete!")
    return bundle