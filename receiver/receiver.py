"""Local HTTP receiver: saves the posted test report as testreport.json.

Run:  python receiver/receiver.py            (listens on 0.0.0.0:5001)
Env:  RECEIVER_TOKEN  optional shared secret (must match CI secret)
      PORT            optional port (default 5001)
"""
import json
import os
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

TOKEN = os.environ.get("RECEIVER_TOKEN", "")
PORT = int(os.environ.get("PORT", "5001"))
OUT = Path(os.environ.get("REPORT_FILE", "testreport.json"))
HISTORY = Path("reports_history")


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body):
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        self._send(200, {"status": "receiver running", "saves_to": str(OUT.resolve())})

    def do_POST(self):
        if self.path.rstrip("/") != "/report":
            return self._send(404, {"error": "use POST /report"})
        if TOKEN and self.headers.get("X-Token") != TOKEN:
            return self._send(401, {"error": "bad token"})
        try:
            length = int(self.headers.get("Content-Length", 0))
            report = json.loads(self.rfile.read(length))
        except (ValueError, json.JSONDecodeError):
            return self._send(400, {"error": "invalid JSON"})
        OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
        HISTORY.mkdir(exist_ok=True)
        run = report.get("pipeline", {}).get("run_id", "unknown")
        (HISTORY / f"testreport_run{run}_{datetime.now():%H%M%S}.json").write_text(
            json.dumps(report, indent=2), encoding="utf-8")
        summary = report.get("summary", {})
        print(f"[{datetime.now():%H:%M:%S}] Saved {OUT} -> status={summary.get('status')} "
              f"{summary.get('passed')}/{summary.get('total')} passed", flush=True)
        self._send(200, {"saved": str(OUT)})

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    print(f"Receiver listening on http://0.0.0.0:{PORT}/report  (saving to {OUT.resolve()})")
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
