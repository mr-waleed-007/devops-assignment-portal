"""Local HTTP receiver. Saves the latest CI test report as test-report.json."""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

OUTPUT_FILE = Path(__file__).resolve().parent / "test-report.json"
TOKEN = None  # Optional: set REPORT_RECEIVER_TOKEN in the environment for protection.


class ReportHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/report":
            self.send_error(404, "Use POST /report")
            return

        import os
        expected = os.environ.get("REPORT_RECEIVER_TOKEN")
        if expected and self.headers.get("Authorization") != f"Bearer {expected}":
            self.send_error(401, "Unauthorized")
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 2_000_000:
                self.send_error(400, "Invalid report size")
                return
            report = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(report, dict) or "summary" not in report or "tests" not in report:
                self.send_error(400, "Invalid report structure")
                return
            OUTPUT_FILE.write_text(json.dumps(report, indent=2), encoding="utf-8")
            body = b"Report received and saved."
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            print(f"Saved report to {OUTPUT_FILE}")
        except (ValueError, UnicodeDecodeError, OSError) as exc:
            self.send_error(400, str(exc))

    def log_message(self, fmt, *args):
        print("%s - %s" % (self.address_string(), fmt % args))


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8001), ReportHandler)
    print("Report receiver listening on http://127.0.0.1:8001/report")
    print(f"Reports will be saved to: {OUTPUT_FILE}")
    server.serve_forever()
