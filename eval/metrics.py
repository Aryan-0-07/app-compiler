import json
import os
from collections import Counter

RESULTS_FILE = os.path.join(os.path.dirname(__file__), "results.json")


def load_results() -> list:
    if not os.path.exists(RESULTS_FILE):
        return []
    with open(RESULTS_FILE, "r") as f:
        return json.load(f)


def compute_metrics(results: list) -> dict:
    if not results:
        return {}

    total = len(results)
    passed = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]

    real_cases = [r for r in results if r["type"] == "real"]
    edge_cases = [r for r in results if r["type"] == "edge"]

    real_passed = [r for r in real_cases if r["success"]]
    edge_passed = [r for r in edge_cases if r["success"]]

    failure_types = Counter(r["failure_type"] for r in failed if r["failure_type"])

    latencies = [r["stage_latency"]["total"] for r in passed]
    avg_latency = round(sum(latencies) / len(latencies), 2) if latencies else 0
    max_latency = round(max(latencies), 2) if latencies else 0
    min_latency = round(min(latencies), 2) if latencies else 0

    stage_latencies = {}
    for stage in ["stage1", "stage2", "stage3", "stage4", "runtime"]:
        vals = [r["stage_latency"][stage] for r in passed if r["stage_latency"][stage] > 0]
        stage_latencies[stage] = round(sum(vals) / len(vals), 2) if vals else 0

    repairs = [r["repair_attempts"] for r in passed]
    avg_repairs = round(sum(repairs) / len(repairs), 2) if repairs else 0
    max_repairs = max(repairs) if repairs else 0

    runtime_passed = [r for r in passed if r["runtime_success"]]

    return {
        "summary": {
            "total_cases": total,
            "passed": len(passed),
            "failed": len(failed),
            "success_rate": round(len(passed) / total * 100, 1),
            "runtime_success_rate": round(len(runtime_passed) / total * 100, 1)
        },
        "by_type": {
            "real": {
                "total": len(real_cases),
                "passed": len(real_passed),
                "success_rate": round(len(real_passed) / len(real_cases) * 100, 1) if real_cases else 0
            },
            "edge": {
                "total": len(edge_cases),
                "passed": len(edge_passed),
                "success_rate": round(len(edge_passed) / len(edge_cases) * 100, 1) if edge_cases else 0
            }
        },
        "failures": {
            "total": len(failed),
            "by_type": dict(failure_types)
        },
        "latency": {
            "average_total": avg_latency,
            "min_total": min_latency,
            "max_total": max_latency,
            "by_stage": stage_latencies
        },
        "repairs": {
            "average": avg_repairs,
            "max": max_repairs,
            "total_repairs": sum(repairs)
        },
        "cases": results
    }


def get_metrics() -> dict:
    results = load_results()
    return compute_metrics(results)


def print_report():
    metrics = get_metrics()
    if not metrics:
        print("No results found. Run eval/runner.py first.")
        return

    s = metrics["summary"]
    print("\n" + "=" * 60)
    print("EVALUATION REPORT")
    print("=" * 60)
    print(f"Total Cases     : {s['total_cases']}")
    print(f"Passed          : {s['passed']}")
    print(f"Failed          : {s['failed']}")
    print(f"Success Rate    : {s['success_rate']}%")
    print(f"Runtime Success : {s['runtime_success_rate']}%")

    print("\nBy Type:")
    for t, v in metrics["by_type"].items():
        print(f"  {t.upper()}: {v['passed']}/{v['total']} ({v['success_rate']}%)")

    print("\nFailure Breakdown:")
    for k, v in metrics["failures"]["by_type"].items():
        print(f"  {k}: {v}")

    print("\nLatency (seconds):")
    print(f"  Average : {metrics['latency']['average_total']}s")
    print(f"  Min     : {metrics['latency']['min_total']}s")
    print(f"  Max     : {metrics['latency']['max_total']}s")
    print("\n  By Stage:")
    for stage, lat in metrics["latency"]["by_stage"].items():
        print(f"    {stage}: {lat}s")

    print("\nRepairs:")
    print(f"  Average per run : {metrics['repairs']['average']}")
    print(f"  Max in one run  : {metrics['repairs']['max']}")
    print(f"  Total repairs   : {metrics['repairs']['total_repairs']}")
    print("=" * 60)


if __name__ == "__main__":
    print_report()