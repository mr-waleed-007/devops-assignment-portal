# Assignment Submission Portal (DevOps Lab Mid)

A Flask assignment-submission portal with input validation, automated Pytest tests, GitHub Actions CI, a local JSON report receiver, and an optional GitHub Pages static demo.

## 1. Requirements

- Python 3.10 or newer
- VS Code
- Git
- A GitHub account
- For automatic local report delivery: Cloudflare Tunnel (`cloudflared`)

## 2. Run the project in VS Code (Windows PowerShell)

Open this project folder in VS Code. Open **Terminal > New Terminal**, then run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000 in your browser. Enter the four fields and submit. Valid submissions are stored in `instance/submissions.json` and shown below the form.

If PowerShell blocks activation, run this once in the current terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## 3. Run the automated tests locally

Stop the Flask server with Ctrl+C, then run:

```powershell
pytest -v
```

Expected result: **3 passed**. To create the same JSON report format locally:

```powershell
pytest -v --junitxml=junit.xml
python scripts/create_report.py junit.xml
```

The report is written to `test-report.json`.

## 4. Create the GitHub repository and push the project

1. Sign in at https://github.com.
2. Click **New repository**.
3. Repository name: `devops-assignment-portal`.
4. Choose **Public** (recommended for the Pages bonus) or Private.
5. Do not add a README, `.gitignore`, or license on GitHub because these are already in this project.
6. Click **Create repository**.
7. In VS Code, make sure the terminal is inside this project folder and run:

```powershell
git init
git add .
git commit -m "Initial assignment portal with CI pipeline"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/devops-assignment-portal.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your GitHub username. If Git asks you to sign in, complete the browser authentication prompt. GitHub no longer accepts account passwords for HTTPS Git operations; use the browser sign-in or a Personal Access Token if prompted.

After pushing, open the repository on GitHub and select **Actions**. The workflow named **Assignment Portal CI** should start automatically.

For later updates:

```powershell
git add .
git commit -m "Describe your change"
git push
```

Every push triggers the workflow.

## 5. Configure automatic delivery of test-report.json to your computer

This step is essential for requirement 4. A GitHub-hosted runner's `localhost` is not your laptop, so expose the local receiver through a temporary tunnel.

### A. Start the local receiver

Open a second VS Code terminal in the project folder and run:

```powershell
python receiver.py
```

Keep this terminal open. The receiver listens on port `8001` and writes the latest report to the project root as `test-report.json`.

### B. Start a Cloudflare quick tunnel

Install `cloudflared` on Windows (if it is not installed):

```powershell
winget install --id Cloudflare.cloudflared
```

Close and reopen the terminal after installation, then run:

```powershell
cloudflared tunnel --url http://localhost:8001
```

Cloudflare prints a public URL similar to `https://random-words.trycloudflare.com`. Copy the actual URL printed in your terminal. Keep the tunnel terminal open too.

### C. Add the URL as a GitHub Actions secret

1. Open your GitHub repository.
2. Go to **Settings > Secrets and variables > Actions**.
3. Select **New repository secret**.
4. Name: `REPORT_RECEIVER_URL`
5. Secret value: paste the tunnel URL only, for example `https://random-words.trycloudflare.com` (do not add `/report`).
6. Click **Add secret**.

Optional receiver protection:
- In PowerShell, before starting `receiver.py`, set a token:

```powershell
$env:REPORT_RECEIVER_TOKEN = "choose-a-long-random-token"
python receiver.py
```

- Add another repository secret named `REPORT_RECEIVER_TOKEN` with exactly the same token value.
- If you do not configure a token, the tunnel URL itself is the only access barrier. Use a fresh quick-tunnel URL for your demonstration and stop it afterwards.

### D. Verify automatic report delivery

With both the receiver and tunnel running, make a small change and push:

```powershell
git add .
git commit -m "Verify automatic CI report delivery"
git push
```

Open **GitHub > Actions > Assignment Portal CI** and inspect the run. After the run, check `test-report.json` in your project folder. It should contain repository, branch, commit SHA, pipeline run ID, timestamp, each test result, and summary counts.

The workflow sends the report after both passing and failing test runs. The final test step still fails the CI job when any test fails. The Pages deployment job only runs after the test job succeeds on `main`.

**Important:** Keep both the receiver and tunnel running during each push and during the instructor's demonstration. A temporary Cloudflare quick-tunnel URL changes when you start a new tunnel; update the GitHub secret if it changes.

## 6. Demonstrate pass, fail, and corrected pass

### Demonstration 1: all tests pass

Run `pytest -v`, then commit and push the working project. Show the green workflow run and the received `test-report.json` with 3 passed and 0 failed.

### Demonstration 2: intentionally introduce a defect

In `app.py`, find this line inside `valid_submission_url`:

```python
return parsed.scheme in ("http", "https") and bool(parsed.netloc) and "." in parsed.netloc
```

Temporarily replace it with:

```python
return False
```

Now run:

```powershell
pytest -v
```

The valid-submission test should fail because valid URLs are rejected. Push the defect:

```powershell
git add app.py
git commit -m "Demonstrate failing CI test"
git push
```

Show the red test workflow and the automatically received JSON report showing failed tests. The receiver step is configured to run even when tests fail.

### Demonstration 3: fix the defect

Restore the original `return` line shown above. Run `pytest -v`, then push:

```powershell
git add app.py
git commit -m "Fix URL validation"
git push
```

Show the green workflow and updated JSON report with all tests passing.

## 7. Bonus: GitHub Pages deployment

The workflow deploys the static demo in the `docs` folder only after the test job passes on the `main` branch.

1. In GitHub, open **Settings > Pages**.
2. Under **Build and deployment > Source**, choose **GitHub Actions**.
3. Push to `main` with passing tests.
4. Open **Actions** and wait for the `deploy-pages` job to complete.
5. Your URL will be:
   `https://YOUR-USERNAME.github.io/devops-assignment-portal/`

Replace `YOUR-USERNAME` with your GitHub username. The exact URL is also shown in the deployment job.

The Pages version is a static demonstration. It saves demo entries in the visitor's browser (`localStorage`); the full Flask app is the version that saves submissions on the server.

## 8. Project structure

```text
devops_assignment_portal/
├── .github/
│   └── workflows/
│       └── ci.yml
├── docs/
│   └── index.html
├── scripts/
│   └── create_report.py
├── templates/
│   └── index.html
├── tests/
│   └── test_app.py
├── app.py
├── receiver.py
├── requirements.txt
├── .gitignore
└── README.md
```

## 9. What to explain in the viva

- **Flask:** runs the assignment portal and handles browser requests.
- **Validation:** required fields must not be empty; the URL must use HTTP or HTTPS and have a host.
- **JSON storage:** valid submissions are saved in a local JSON file.
- **Pytest:** executes the three required test cases.
- **GitHub Actions:** automatically checks out the pushed code, installs dependencies, and runs tests.
- **JUnit XML:** records the actual test case outcomes produced by Pytest.
- **Report generator:** converts those executed results into the required JSON structure and adds GitHub metadata.
- **Local receiver:** accepts the report over HTTP and writes `test-report.json` on your computer.
- **Cloudflare Tunnel:** provides a route from the GitHub-hosted runner to your local receiver.
- **Conditional deployment:** the Pages job depends on the successful test job, so a failed test run does not publish a new version.

## 10. Submission checklist

- [ ] GitHub repository URL
- [ ] Portal runs locally in VS Code
- [ ] Three automated tests pass
- [ ] GitHub Actions runs after every push
- [ ] Local `test-report.json` receives passing-run results
- [ ] Local `test-report.json` receives failing-run results
- [ ] Defect is fixed and final run passes
- [ ] Receiver and tunnel are kept running during demonstration
- [ ] GitHub Pages URL (bonus)
