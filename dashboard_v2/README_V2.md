# Co Audit Reviewer Dashboard (version 2)

Streamlit dashboard for the Co Audit backend, with a reviewer sign-in screen, a home screen, a progress tracker, a stats strip, a review queue, a scorecard with charts, and the append-only audit log.

## Run

```
pip install -r requirements.txt
streamlit run app.py
```

Run it from inside this folder so the blue theme in `.streamlit/config.toml` is loaded.

## Connect to the backend

Start the backend, then point the dashboard at it. Use the backend laptop's IPv4 address from `ipconfig`:

```
$env:CO_AUDIT_API_URL = "http://192.168.1.71:8000"
streamlit run app.py
```

You can also type the address into the FastAPI URL box in the sidebar. To try the screens without a backend, choose Sample Data in the sidebar, or start with:

```
$env:CO_AUDIT_MODE = "sample"
streamlit run app.py
```

## Screens

- Sign-in: a demo gate. No password is collected. The reviewer ID is written to the audit log with every decision. Use Switch reviewer in the sidebar for two-person approvals.
- Home: summary of the current thresholds and a grid of companies to audit.
- Overview: metrics table with status, confidence bars and validation checks.
- Review queue: flagged values, ranked by risk, with approve, edit and reject.
- Scorecard: escalation curve, how values were handled, and accuracy against SEC data.
- Audit log: append-only decisions and workpaper exports.

## Files

- `app.py`: the screens.
- `landing.py`: the sign-in screen.
- `helpers.py`: formatting, tables, charts data and exports.
- `styles.py`: the look.
- `api_client.py`, `models.py`, `mock_client.py`: the backend client, data shapes and sample data.
- `.streamlit/config.toml`: theme settings.

## Notes

- The two-person limit applies to values of 150 billion dollars or more. Those need two different reviewer IDs.
- The fault switch simulates a corrupted value. A banner shows while it is on.
