import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from pipeline.stage1_intent import extract_intent
from pipeline.stage2_architecture import design_architecture
from pipeline.stage3_schemas import generate_schemas
from pipeline.stage4_refinement import refine_bundle
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

print("\n" + "=" * 50)
print("STEP 4 — Validating + Repairing...")
print("=" * 50)
bundle = refine_bundle(bundle)

print("\n--- FINAL RESULTS ---")
print(f"Is Valid: {bundle.is_valid}")
print(f"Repair Attempts: {bundle.repair_attempts}")
print(f"Total Issues: {len(bundle.validation_issues)}")

if bundle.validation_issues:
    print("\nRemaining Issues:")
    for issue in bundle.validation_issues:
        print(f"  [{issue.severity.upper()}] {issue.layer}: {issue.message}")

print("\n✅ Phase 4 Complete!")