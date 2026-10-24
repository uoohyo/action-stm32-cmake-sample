#!/usr/bin/env python3
"""Render a single-run result table without mixing branch badges and logs."""
import json
import os
from pathlib import Path
import re
import sys
prefix = sys.argv[1]
repo = os.environ.get("GITHUB_REPOSITORY", "uoohyo/action-" + ("ccstudio-ide" if prefix == "ccs" else "stm32-cmake") + "-sample")
versions = [p.stem.split("-v", 1)[1] for p in Path(".github/workflows").glob(f"test-{prefix}-v*.yml")]
versions.sort(key=lambda v: tuple(map(int, v.split("."))), reverse=True)
lines = ["<!-- TEST_RESULTS_START -->", "", "## Test Results", "",
         "Results below refer to the linked completed main-branch run, not a moving branch badge. Missing or legacy configuration evidence is not a passing result.", "",
         "| Version | Recorded status | Debug / Release | Commit | Run updated (UTC) | Details |",
         "|---|---|---|---|---|---|"]
for version in versions:
    file = Path(".github/test-results") / f"{version}.json"
    result = json.loads(file.read_text()) if file.exists() else {}
    current = result.get("schema_version") == 2
    status = result.get("status", "missing") if current else "legacy / unverified"
    states = result.get("configurations", {}) if current else {}
    config = " / ".join(states.get(c, "missing") for c in ("Debug", "Release"))
    sha = result.get("head_sha", "-")[:12] if current else "-"
    timestamp = result.get("timestamp", "-") if current else "-"
    url = result.get("log_url") if current else None
    details = f"[Run]({url})" if url else f"[Workflow](https://github.com/{repo}/actions/workflows/test-{prefix}-v{version}.yml)"
    lines.append(f"| v{version} | {status} | {config} | {sha} | {timestamp} | {details} |")
lines += ["", "<!-- TEST_RESULTS_END -->"]
readme = Path("README.md")
text = readme.read_text()
section = "\n".join(lines)
pattern = r"<!-- TEST_RESULTS_START -->.*?<!-- TEST_RESULTS_END -->"
text = re.sub(pattern, lambda _: section, text, flags=re.S) if re.search(pattern, text, re.S) else text + "\n" + section + "\n"
readme.write_text(text)
