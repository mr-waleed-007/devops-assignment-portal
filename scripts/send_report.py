"""POST testreport.json to the local receiver (via tunnel). Env: RECEIVER_URL, RECEIVER_TOKEN."""
import os
import sys
import time
import urllib.error
import urllib.request

url = os.environ.get("RECEIVER_URL", "").strip()
if not url:
    sys.exit("RECEIVER_URL secret is not set")
if not url.rstrip("/").endswith("/report"):
    url = url.rstrip("/") + "/report"
body = open(sys.argv[1] if len(sys.argv) > 1 else "testreport.json", "rb").read()
headers = {"Content-Type": "application/json", "X-Token": os.environ.get("RECEIVER_TOKEN", ""),
           "ngrok-skip-browser-warning": "true", "User-Agent": "ci-report-sender"}
for attempt in range(1, 4):
    try:
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=20) as r:
            print("Receiver responded:", r.status, r.read().decode())
            sys.exit(0)
    except (urllib.error.URLError, TimeoutError) as e:
        print(f"Attempt {attempt} failed: {e}")
        time.sleep(3)
sys.exit("Could not deliver report - is the receiver AND tunnel running?")
