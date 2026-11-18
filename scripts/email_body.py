"""Create email_body.txt from testreport.json."""
import json

r = json.load(open("testreport.json"))
s = r["summary"]
lines = [
    f"Overall result: {s['status'].upper()}",
    f"Repository: {r['repository']}  Branch: {r['branch']}",
    f"Commit: {r['commit_sha']}",
    f"Run: {r['pipeline']['run_id']}  Time: {r['timestamp']}",
    f"Total: {s['total']}  Passed: {s['passed']}  Failed: {s['failed']}",
    "", "Individual results:",
]
for t in r["tests"]:
    line = f" - [{t['result'].upper()}] {t['name']}"
    if t.get("failure_message"):
        line += f"\n     {t['failure_message'][:300]}"
    lines.append(line)
open("email_body.txt", "w", encoding="utf-8").write("\n".join(lines))
