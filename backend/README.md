Backend for Personalized Multi-Agent Financial Advisor

Quick start

1. Create a Python virtual environment and activate it.
2. Copy `.env.example` to `.env` and set `OPENROUTER_API_KEY`.
3. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

4. Run the app:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Endpoints (examples):
- `POST /ingest/upload_csv` - upload user CSV financial data
- `POST /analyze/debt` - run debt analyzer
- `POST /analyze/savings` - run savings strategy
- `POST /analyze/budget` - actionable budget advice
- `POST /analyze/debt_payoff` - optimized payoff plan

See `app/` for implementation details.

Running tests

From the `backend` folder run:

```bash
pip install -r requirements.txt
pytest -q
```

Tests use a mocked LLM path so they run without an `OPENROUTER_API_KEY`.

CI and Badges

You can enable the included GitHub Actions workflow to run tests automatically. Example badge (replace `OWNER/REPO` with your repository):

```markdown
[![CI](https://github.com/OWNER/REPO/actions/workflows/ci.yml/badge.svg)](https://github.com/OWNER/REPO/actions/workflows/ci.yml)
```

Branch protection suggestion:
- Protect `main`/`master` and require the CI checks (`CI / backend-tests`) to pass before merging pull requests.

