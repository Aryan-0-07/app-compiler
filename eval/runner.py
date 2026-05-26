import time
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pipeline.stage1_intent import extract_intent
from pipeline.stage2_architecture import design_architecture
from pipeline.stage3_schemas import generate_schemas
from pipeline.stage4_refinement import refine_bundle
from runtime.executor import run_runtime_checks
from eval.test_cases import TEST_CASES

RESULTS_FILE = os.path.join(os.path.dirname(__file__), "results.json")


def run_single(test_case: dict) -> dict:
    result = {
        "id": test_case["id"],
        "type": test_case["type"],
        "category": test_case.get("category", "normal"),
        "prompt": test_case["prompt"],
        "success": False,
        "failure_type": None,
        "repair_attempts": 0,
        "total_issues": 0,
        "is_valid": False,
        "runtime_success": False,
        "tables_created": 0,
        "endpoints_validated": 0,
        "stage_latency": {
            "stage1": 0,
            "stage2": 0,
            "stage3": 0,
            "stage4": 0,
            "runtime": 0,
            "total": 0
        },
        "error": None,
        "app_name": None
    }

    total_start = time.time()

    try:
        # Stage 1
        t = time.time()
        intent = extract_intent(test_case["prompt"])
        result["stage_latency"]["stage1"] = round(time.time() - t, 2)
        result["app_name"] = intent.app_name

        # Stage 2
        t = time.time()
        arch = design_architecture(intent)
        result["stage_latency"]["stage2"] = round(time.time() - t, 2)

        # Stage 3
        t = time.time()
        bundle = generate_schemas(intent, arch)
        result["stage_latency"]["stage3"] = round(time.time() - t, 2)

        # Stage 4
        t = time.time()
        bundle = refine_bundle(bundle)
        result["stage_latency"]["stage4"] = round(time.time() - t, 2)
        result["repair_attempts"] = bundle.repair_attempts
        result["total_issues"] = len(bundle.validation_issues)
        result["is_valid"] = bundle.is_valid

        # Runtime
        t = time.time()
        runtime = run_runtime_checks(bundle)
        result["stage_latency"]["runtime"] = round(time.time() - t, 2)
        result["runtime_success"] = runtime["success"]
        result["tables_created"] = len(runtime["db"]["tables_created"])
        result["endpoints_validated"] = len(runtime["api"]["endpoints_validated"])

        result["success"] = True

    except Exception as e:
        result["success"] = False
        error_msg = str(e)
        result["error"] = error_msg

        if "validation error" in error_msg.lower():
            result["failure_type"] = "schema_validation"
        elif "json" in error_msg.lower():
            result["failure_type"] = "invalid_json"
        elif "timeout" in error_msg.lower():
            result["failure_type"] = "timeout"
        elif "rate limit" in error_msg.lower():
            result["failure_type"] = "rate_limit"
        else:
            result["failure_type"] = "pipeline_error"

    result["stage_latency"]["total"] = round(time.time() - total_start, 2)
    return result


def run_all(save: bool = True) -> list:
    print("\n" + "=" * 60)
    print("EVALUATION FRAMEWORK — Running 20 test cases")
    print("=" * 60)

    results = []

    for i, test_case in enumerate(TEST_CASES):
        print(f"\n[{i+1}/20] {test_case['id']} ({test_case['type']}) — {test_case['prompt'][:60]}...")
        result = run_single(test_case)

        status = "✅ PASS" if result["success"] else f"❌ FAIL ({result['failure_type']})"
        print(f"  Status: {status}")
        print(f"  Latency: {result['stage_latency']['total']}s")
        if result["success"]:
            print(f"  Tables: {result['tables_created']} | Endpoints: {result['endpoints_validated']} | Repairs: {result['repair_attempts']}")

        results.append(result)

        # Small delay to avoid rate limiting
        time.sleep(2)

    if save:
        with open(RESULTS_FILE, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n✅ Results saved to {RESULTS_FILE}")

    return results


if __name__ == "__main__":
    run_all()