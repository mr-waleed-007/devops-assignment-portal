"""Convert pytest JUnit XML into testreport.json (with CI metadata)."""
import argparse
import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timezone


def parse(junit_path):
    tests = []
    if not os.path.exists(junit_path):
        return [{"name": "pytest (no results produced)", "result": "failed",
                 "failure_message": "junit.xml not found - tests did not run"}]
    for case in ET.parse(junit_path).getroot().iter("testcase"):
        name = f"{case.get('classname', '')}::{case.get('name')}".lstrip(":")
        entry = {"name": name, "result": "passed", "failure_message": None}
        for tag, result in (("failure", "failed"), ("error", "failed"), ("skipped", "skipped")):
            node = case.find(tag)
            if node is not None:
                entry["result"] = result
                entry["failure_message"] = (node.get("message") or node.text or "").strip()[:1000]
                break
        tests.append(entry)
    return tests


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--junit", default="junit.xml")
    ap.add_argument("--out", default="testreport.json")
    a = ap.parse_args()
    tests = parse(a.junit)
    passed = sum(t["result"] == "passed" for t in tests)
    failed = sum(t["result"] == "failed" for t in tests)
    status = "passed" if failed == 0 and passed > 0 else "failed"
    report = {
        "repository": os.environ.get("GITHUB_REPOSITORY", "local/repo"),
        "branch": os.environ.get("GITHUB_REF_NAME", "local"),
        "commit_sha": os.environ.get("GITHUB_SHA", "local"),
        "pipeline": {"run_id": os.environ.get("GITHUB_RUN_ID", "local"),
                     "run_number": os.environ.get("GITHUB_RUN_NUMBER", "0")},
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tests": tests,
        "summary": {"total": len(tests), "passed": passed, "failed": failed, "status": status},
    }
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"Report written: {a.out} ({passed}/{len(tests)} passed, status={status})")
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"status={status}\n")


if __name__ == "__main__":
    main()
