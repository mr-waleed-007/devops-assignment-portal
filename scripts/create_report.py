"""Convert pytest JUnit XML into the JSON report required by the lab."""
import json
import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path


def main():
    xml_path = Path(sys.argv[1] if len(sys.argv) > 1 else "junit.xml")
    tests = []
    if xml_path.exists():
        root = ET.parse(xml_path).getroot()
        cases = root.iter("testcase") if root.tag != "testsuite" else root.findall(".//testcase")
        for case in cases:
            failure = case.find("failure")
            error = case.find("error")
            problem = failure if failure is not None else error
            tests.append({
                "name": f"{case.get('classname', '')}::{case.get('name', 'unnamed')}".strip(":"),
                "result": "failed" if problem is not None else "passed",
                "failure_message": (
                    (problem.get("message") or (problem.text or "").strip())
                    if problem is not None else None
                ),
            })

    total = len(tests)
    failed = sum(item["result"] == "failed" for item in tests)
    passed = total - failed
    report = {
        "repository": os.getenv("GITHUB_REPOSITORY", "local-run"),
        "branch": os.getenv("GITHUB_REF_NAME", "local"),
        "commit_sha": os.getenv("GITHUB_SHA", "local"),
        "pipeline_run_id": os.getenv("GITHUB_RUN_ID", "local"),
        "execution_timestamp": datetime.now(timezone.utc).isoformat(),
        "tests": tests,
        "summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "overall_status": "failed" if failed or total == 0 else "passed",
        },
    }
    Path("test-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
