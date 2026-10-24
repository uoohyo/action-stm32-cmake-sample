#!/usr/bin/env python3
"""Record and collect configuration-specific, run-bound test evidence."""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

CONFIGS = ("Debug", "Release")

def utcnow():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def summarize(version, run, records, repository):
    """Never reuse prior evidence or combine different attempts/commits."""
    valid = {}
    for record in records:
        config = record.get("configuration")
        if (record.get("schema_version") == 2 and record.get("version") == version
                and config in CONFIGS and record.get("head_sha") == run["headSha"]
                and str(record.get("run_id")) == str(run["databaseId"])
                and str(record.get("run_attempt")) == str(run["attempt"])
                and record.get("branch") == "main"
                and record.get("status") in ("success", "failure")):
            if config in valid:
                raise ValueError("Duplicate configuration evidence")
            valid[config] = record["status"]
    complete = set(valid) == set(CONFIGS)
    status = ("success" if complete and all(v == "success" for v in valid.values())
              and run["conclusion"] == "success" else "failure" if complete else "missing")
    return {"schema_version": 2, "version": version, "status": status,
            "collection_status": "complete" if complete else "missing-or-incompatible",
            "configurations": valid, "head_sha": run["headSha"], "branch": "main",
            "run_id": str(run["databaseId"]), "run_attempt": run["attempt"],
            "timestamp": run["updatedAt"], "collected_at": utcnow(),
            "log_url": f"https://github.com/{repository}/actions/runs/{run['databaseId']}",
            "workflow_conclusion": run["conclusion"]}

def gh(*args):
    return subprocess.check_output(["gh", *args], text=True)

def collect(prefix):
    repository = os.environ["GITHUB_REPOSITORY"]
    destination = Path(".github/test-results")
    destination.mkdir(exist_ok=True)
    degraded = 0
    for workflow in sorted(Path(".github/workflows").glob(f"test-{prefix}-v*.yml")):
        version = workflow.stem.split("-v", 1)[1]
        if not re.fullmatch(r"[0-9]+(?:\.[0-9]+){2,3}", version):
            raise ValueError("Invalid workflow version")
        result = {"schema_version": 2, "version": version, "status": "missing",
                  "collection_status": "missing", "configurations": {}, "collected_at": utcnow()}
        try:
            runs = json.loads(gh("run", "list", "--workflow", workflow.name,
                                 "--branch", "main", "--status", "completed", "--limit", "1",
                                 "--json", "databaseId,headSha,headBranch,conclusion,updatedAt,event"))
            if runs:
                run = runs[0]
                detail = json.loads(gh("api", f"repos/{repository}/actions/runs/{run['databaseId']}"))
                run["attempt"] = detail["run_attempt"]
                if (run["headBranch"] != "main" or detail.get("head_branch") != "main"
                        or run["event"] not in ("push", "workflow_dispatch")
                        or detail.get("event") != run["event"]
                        or detail.get("head_sha") != run["headSha"]):
                    raise ValueError("Unexpected result branch")
                records = []
                with tempfile.TemporaryDirectory() as directory:
                    proc = subprocess.run(["gh", "run", "download", str(run["databaseId"]),
                                           "--pattern", f"test-result-{version}-*", "--dir", directory],
                                          capture_output=True, text=True)
                    if proc.returncode == 0:
                        for file in Path(directory).rglob("*.json"):
                            records.append(json.loads(file.read_text()))
                    result = summarize(version, run, records, repository)
            else:
                result["collection_status"] = "not-run"
        except (subprocess.CalledProcessError, ValueError, KeyError, OSError) as exc:
            print(f"::warning::Cannot collect {version}: {type(exc).__name__}")
            result["status"] = "missing"
            result["collection_status"] = "collection-error"
        if result["collection_status"] != "complete":
            degraded += 1
        (destination / f"{version}.json").write_text(json.dumps(result, indent=2) + "\n")
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as output:
            output.write(f"degraded={degraded}\n")
    print(f"Collected results; {degraded} versions have missing/incompatible evidence.")

def save(version, config, status):
    result = {"schema_version": 2, "version": version, "configuration": config,
              "status": status, "timestamp": utcnow(), "branch": os.environ["GITHUB_REF_NAME"],
              "head_sha": os.environ["GITHUB_SHA"], "run_id": os.environ["GITHUB_RUN_ID"],
              "run_attempt": os.environ["GITHUB_RUN_ATTEMPT"]}
    destination = Path(".github/test-results")
    destination.mkdir(exist_ok=True)
    (destination / f"{version}-{config}.json").write_text(json.dumps(result, indent=2) + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    collect_parser = commands.add_parser("collect")
    collect_parser.add_argument("prefix", choices=("ccs", "stm32"))
    save_parser = commands.add_parser("save")
    save_parser.add_argument("version")
    save_parser.add_argument("configuration", choices=CONFIGS)
    save_parser.add_argument("status", choices=("success", "failure"))
    args = parser.parse_args()
    if args.command == "collect":
        collect(args.prefix)
    else:
        save(args.version, args.configuration, args.status)
