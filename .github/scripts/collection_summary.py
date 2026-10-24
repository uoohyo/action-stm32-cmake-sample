#!/usr/bin/env python3
"""Report collection counts and exact run targets without changing build inputs."""
import json
import os
from pathlib import Path
import sys

def collection_summary(records):
    """Describe collection outcomes and the exact target runs in one summary."""
    counts = {status: sum(record.get("status") == status for record in records)
              for status in ("success", "failure", "missing")}
    lines = ["## Sample result collection", "",
             f"Success: {counts['success']} | Failure: {counts['failure']} | Missing: {counts['missing']}", "",
             "| Version | Status | Main commit | Target run |", "|---|---|---|---|"]
    for record in records:
        sha = record.get("head_sha", "-")[:12]
        target = f"[Run {record['run_id']}]({record['log_url']})" if record.get("run_id") else "No completed target run"
        lines.append(f"| {record['version']} | {record['status']} | {sha} | {target} |")
    return "\n".join(lines) + "\n"

if __name__ == "__main__":
    prefix = sys.argv[1]
    if prefix not in ("ccs", "stm32"):
        raise ValueError("Unknown workflow prefix")
    versions = sorted(p.stem.split("-v", 1)[1] for p in Path(".github/workflows").glob(f"test-{prefix}-v*.yml"))
    records = [json.loads((Path(".github/test-results") / f"{version}.json").read_text()) for version in versions]
    summary = collection_summary(records)
    print(summary)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as output:
            output.write(summary)
