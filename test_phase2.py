import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from pipeline.stage1_intent import extract_intent
from pipeline.stage2_architecture import design_architecture
import json

prompt = "Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics."

print("=" * 50)
print("STEP 1 — Extracting Intent...")
print("=" * 50)
intent = extract_intent(prompt)
print(f"App: {intent.app_name}")
print(f"Entities: {[e.name for e in intent.entities]}")

print("\n" + "=" * 50)
print("STEP 2 — Designing Architecture...")
print("=" * 50)
arch = design_architecture(intent)

print("\nARCHITECTURE OUTPUT:")
print(json.dumps(arch.model_dump(), indent=2))

print("\n--- SUMMARY ---")
print(f"Entities: {arch.entities}")
print(f"Pages: {arch.page_list}")
print(f"Business Rules: {arch.business_rules}")
print(f"Relations: {[(r.from_entity, r.type, r.to_entity) for r in arch.relations]}")