import argparse
import json
import sys
from pathlib import Path

# Add src to sys.path to allow running from root without PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent / "src"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics", default="reports/metrics.json")
    parser.add_argument("--out", default="reports/final_report.md")
    args = parser.parse_args()
    metrics = json.loads(Path(args.metrics).read_text())
    lines = [
        "# Day 10 Reliability Final Report",
        "",
        "## 1. Architecture summary",
        "",
        "The system is a high-availability gateway that protects LLM agents using a multi-layered reliability strategy.",
        "",
        "```",
        "User Request",
        "    |",
        "    v",
        "[Gateway] ---> [Shared Redis Cache] --------> HIT? return cached",
        "    |                                            |",
        "    v                                            v MISS",
        "[Circuit Breaker: Primary] ------------------> Provider A (GPT-4)",
        "    |  (OPEN? skip to fallback)",
        "    v",
        "[Circuit Breaker: Backup] -------------------> Provider B (Claude)",
        "    |  (OPEN? skip to fallback)",
        "    v",
        "[Static fallback message] (Degraded state)",
        "```",
        "",
        "## 2. Configuration",
        "",
        "| Setting | Value | Reason |",
        "|---|---:|---|",
        "| failure_threshold | 3 | Balances fast failure detection with tolerance for jitter. |",
        "| reset_timeout_seconds | 2 | Allows time for provider recovery before probing. |",
        "| success_threshold | 1 | A single successful probe restores confidence. |",
        "| cache TTL | 300 | 5-minute freshness for frequently asked queries. |",
        "| similarity_threshold | 0.92 | High accuracy for semantic matching. |",
        "| load_test requests | 200 | Significant load for P95/P99 measurements. |",
        "",
        "## 3. Metrics Summary",
        "",
        "| Metric | Value |",
        "|---|---:|",
    ]
    for key, value in metrics.items():
        if key == "scenarios":
            continue
        lines.append(f"| {key} | {value} |")
    
    lines += [
        "",
        "## 4. Redis Shared Cache",
        "",
        "### Why shared cache matters",
        "In production, we scale horizontally. An in-memory cache is local to each instance, leading to redundant provider calls. **Shared Redis Cache** ensures all instances benefit from cached results simultaneously.",
        "",
        "## 5. Chaos Scenarios",
        "",
        "| Scenario | Status |",
        "|---|---|",
    ]
    for key, value in metrics.get("scenarios", {}).items():
        lines.append(f"| {key} | {value} |")
        
    lines += [
        "",
        "## 6. Failure analysis",
        "",
        "**Remaining Weakness**: Circuit Breaker state (counters) is still local to each instance.",
        "**The Fix**: Store circuit breaker states in Redis. If one instance detects a provider is down, the circuit will open globally instantly.",
        "",
        "## 7. Next steps",
        "",
        "1. **Global Circuit State**: Move failure counters to Redis.",
        "2. **Semantic Search**: Use vector embeddings for advanced similarity matching.",
        "3. **Adaptive TTL**: Dynamically adjust TTL based on query popularity.",
    ]
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text("\n".join(lines))
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
