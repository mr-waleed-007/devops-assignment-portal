import json
import os
from pathlib import Path
from urllib.parse import urlparse

from flask import Flask, flash, redirect, render_template, request, url_for


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-change-this"),
        SUBMISSIONS_FILE=os.environ.get(
            "SUBMISSIONS_FILE", str(Path(app.instance_path) / "submissions.json")
        ),
    )
    if test_config:
        app.config.update(test_config)

    Path(app.config["SUBMISSIONS_FILE"]).parent.mkdir(parents=True, exist_ok=True)

    def load_submissions():
        path = Path(app.config["SUBMISSIONS_FILE"])
        if not path.exists():
            return []
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []

    def save_submissions(items):
        path = Path(app.config["SUBMISSIONS_FILE"])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(items, indent=2), encoding="utf-8")

    def valid_submission_url(value):
        try:
            parsed = urlparse(value.strip())
            return parsed.scheme in ("http", "https") and bool(parsed.netloc) and "." in parsed.netloc
        except (ValueError, AttributeError):
            return False

    @app.get("/")
    def index():
        return render_template("index.html", submissions=load_submissions())

    @app.post("/submit")
    def submit():
        name = request.form.get("name", "").strip()
        registration_number = request.form.get("registration_number", "").strip()
        assignment_title = request.form.get("assignment_title", "").strip()
        submission_url = request.form.get("submission_url", "").strip()

        if not all((name, registration_number, assignment_title, submission_url)):
            flash("All fields are required.", "error")
            return redirect(url_for("index"))

        if not valid_submission_url(submission_url):
            flash("Please enter a valid HTTP or HTTPS submission URL.", "error")
            return redirect(url_for("index"))

        submissions = load_submissions()
        submissions.append({
            "name": name,
            "registration_number": registration_number,
            "assignment_title": assignment_title,
            "submission_url": submission_url,
        })
        save_submissions(submissions)
        flash("Assignment submitted successfully.", "success")
        return redirect(url_for("index"))

    # Exposed for focused unit tests; normal users submit through /submit.
    app.config["VALIDATE_SUBMISSION_URL"] = valid_submission_url
    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
