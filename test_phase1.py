import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from pipeline.stage1_intent import extract_intent
import json

prompt = "Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics."

print("=" * 50)
print("USER PROMPT:")
print(prompt)
print("=" * 50)

result = extract_intent(prompt)

print("\nEXTRACTED INTENT:")
print(json.dumps(result.model_dump(), indent=2))

print("\n--- SUMMARY ---")
print(f"App Name: {result.app_name}")
print(f"Entities: {[e.name for e in result.entities]}")
print(f"Roles: {result.roles}")
print(f"Features: {[f.name for f in result.features]}")
print(f"Auth Required: {result.auth_required}")
print(f"Payment Required: {result.payment_required}")
print(f"Assumptions: {result.assumptions}")