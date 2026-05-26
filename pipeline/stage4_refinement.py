import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from schemas.bundle import SchemaBundle
from validators.cross_layer import run_all_validations
from repair.engine import run_repair
from config import MAX_REPAIR_ATTEMPTS


def refine_bundle(bundle: SchemaBundle) -> SchemaBundle:
    """Validate and repair the bundle until clean or max attempts reached"""
    print("\n" + "=" * 50)
    print("Stage 4 — Validation + Repair Engine")
    print("=" * 50)

    for attempt in range(MAX_REPAIR_ATTEMPTS):
        print(f"\nValidation round {attempt + 1}...")
        bundle = run_all_validations(bundle)

        if bundle.is_valid:
            print(f"\n✅ Bundle is valid after {attempt + 1} round(s)!")
            return bundle

        error_count = len([i for i in bundle.validation_issues if i.severity == "error"])
        print(f"\n⚠️  Found {error_count} error(s) — running repair...")
        bundle = run_repair(bundle)

    print(f"\n⚠️  Max repair attempts reached. Running final validation...")
    bundle = run_all_validations(bundle)
    return bundle