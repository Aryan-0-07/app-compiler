import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from pipeline.stage1_intent import extract_intent
from pipeline.stage2_architecture import design_architecture
from pipeline.stage3_schemas import generate_schemas
import json

prompt = "Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics."

print("=" * 50)
print("STEP 1 — Extracting Intent...")
print("=" * 50)
intent = extract_intent(prompt)
print(f"App: {intent.app_name}")

print("\n" + "=" * 50)
print("STEP 2 — Designing Architecture...")
print("=" * 50)
arch = design_architecture(intent)
print(f"Entities: {arch.entities}")

print("\n" + "=" * 50)
print("STEP 3 — Generating Schemas...")
print("=" * 50)
bundle = generate_schemas(intent, arch)

print("\n--- DB TABLES ---")
for table in bundle.db.tables:
    cols = [c.name for c in table.columns]
    print(f"{table.name}: {cols}")

print("\n--- API ENDPOINTS ---")
for ep in bundle.api.endpoints:
    print(f"{ep.method} {ep.path} — {ep.name}")

print("\n--- UI PAGES ---")
for page in bundle.ui.pages:
    print(f"{page.path} — {page.name}")

print("\n--- AUTH ROLES ---")
for role in bundle.auth.roles:
    print(f"{role.name} — {len(role.permissions)} permissions")

print("\n✅ Phase 3 Complete! SchemaBundle generated successfully!")