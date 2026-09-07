# RailBlock AI — SIH26027

AI-assisted railway maintenance block planning using **FastAPI + SQLite + scikit-learn + OR-Tools CP-SAT + React/Vite**.

## Project structure

- `backend/railblock.db` — canonical application database
- `backend/ml_models/` — shipped demo ML artifacts
- `backend/app/` — API, services, optimizer and models
- `frontend/src/` — React dashboard

> The application deliberately uses `backend/railblock.db`. Do not copy a second SQLite database into the frontend or run the backend from a different project folder.

## Windows startup

### Terminal 1 — backend

```powershell
cd "C:\path\to\RAILBlock ai\backend"
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Check:

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/health/database`
- `http://127.0.0.1:8000/docs`

### Terminal 2 — frontend

```powershell
cd "C:\path\to\RAILBlock ai\frontend"
npm install
npm run dev -- --host 0.0.0.0
```

Open `http://localhost:5173`.

### Phone/tablet on the same Wi-Fi

1. Find the PC LAN IPv4 address with `ipconfig`.
2. Open `http://<PC-IP>:5173` on the phone.
3. The frontend automatically uses the same host on port `8000` for the API.
4. Windows Firewall must allow inbound TCP 5173 and 8000 on the private network.

Do **not** set `VITE_API_BASE_URL=http://localhost:8000` when testing from a phone; `localhost` would mean the phone itself.

## Database

The supplied demo database contains the operational entities used by the dashboard. To verify it directly:

```powershell
cd backend
python verify_database.py
```

The app also exposes `/health/database` with table counts.

## Optimization workflow

1. Load pending/overdue maintenance tasks.
2. Calculate AI priority, failure-risk and train-impact features.
3. Run OR-Tools CP-SAT against corridor windows, protected trains, resources, dependencies, safety and existing approved blocks.
4. Group compatible overlapping tasks into physical maintenance blocks.
5. Validate the resulting plan.
6. Compare it with a baseline heuristic.
7. Save the generated plan and blocks to SQLite.

`FEASIBLE` means CP-SAT found a constraint-satisfying solution. It does not by itself mean the mathematically optimal solution was proven.

## Important demo limitation

The included ML artifacts are **synthetic-demo models**. Their metrics must not be presented as real-world Indian Railways predictive accuracy. Human operational approval remains mandatory.

## Testing

```powershell
cd backend
pytest -q
```
