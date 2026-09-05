"""Run predefined SyncAgent API scenarios.

Examples:
    python tests/run_scenarios.py --scenario "Late Night Detective"
    python tests/run_scenarios.py --all
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

from scenarios import SCENARIOS, SCENARIO_NAMES


def request_analysis(base_url: str, scenario: dict) -> dict:
    payload = json.dumps({key: scenario[key] for key in ("scene_description", "budget", "territory", "top_k")}).encode()
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/api/analyze",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=180) as response:
        return json.loads(response.read().decode())


def print_result(scenario: dict, result: dict) -> None:
    recommendations = result.get("recommendations", [])
    rejected = result.get("rejected_candidates", [])
    print("=" * 60)
    print(f"SCENARIO: {scenario['name']}")
    print("=" * 60)
    print(f"Budget: ${scenario['budget']}")
    print(f"Territory: {scenario['territory']}")
    print(f"Recommendations: {len(recommendations)}")
    print(f"Rejected: {len(rejected)}")
    if recommendations:
        top = recommendations[0]
        print(f"Top recommendation: {top.get('title', 'Unknown')}")
        print(f"Match: {top.get('match_score', 'N/A')}%")
        print(f"License: ${top.get('license_cost', 'N/A')}")
        print(f"Status: {top.get('pre_clearance_status', 'N/A')}")
    for item in rejected[:5]:
        print(f"Rejected: {item.get('title', 'Unknown')} - {item.get('reason', 'Constraint failed.')}")
    print("PASS: response contract received")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true", help="Run every scenario")
    group.add_argument("--scenario", choices=SCENARIO_NAMES, help="Run one named scenario")
    parser.add_argument("--base-url", default=os.getenv("BACKEND_URL", "http://127.0.0.1:8000"))
    args = parser.parse_args()
    selected = SCENARIOS if args.all else [next(item for item in SCENARIOS if item["name"] == args.scenario)]
    for scenario in selected:
        try:
            print_result(scenario, request_analysis(args.base_url, scenario))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
            print(f"FAIL: {scenario['name']}: {error}", file=sys.stderr)
            raise SystemExit(1) from error


if __name__ == "__main__":
    main()
