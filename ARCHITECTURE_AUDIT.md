# Architecture Audit — RailBlock AI

## Implementation Status (Phase 0 Audit)

| Component | Status | Notes |
|---|---|---|
| **Architecture** | PARTIAL | Backend and frontend shells initialized. Dependencies resolved. |
| **Database** | PARTIAL | 8 core domain models present. SQLite tested. Foreign keys missing from some models; enums being standardized. |
| **API** | PARTIAL | Route structure defined. Need to harden endpoints and ensure AI inference is connected properly. |
| **Synthetic Data** | DONE | Generates 100+ assets, 250+ tasks, corridors, trains. Seed script successfully seeds SQLite database. |
| **AI** | DONE | Models built, feature engineering implemented. Model manager defined. Training script runs and outputs valid .joblib models. |
| **CP-SAT** | PARTIAL | 10 constraints structure created. Needs extensive validation to ensure OR-Tools constraints correctly map to actual integers, limits, and real dependencies. |
| **Validation** | PARTIAL | Structure created. ValidationService must implement deterministic hard verification independent of CP-SAT output. |
| **Baseline** | PARTIAL | BaselineService skeleton exists. Needs real deterministic heuristics (Earliest Due Date). |
| **Planning** | PARTIAL | generate_plan pipeline implemented but relies on integrations and robust CP-SAT/Baseline functionality. |
| **Frontend** | PARTIAL | React + Vite shell initialized with dependencies. Pages and components created but need to be tied together, verified for API integration, and styled properly. |
| **Testing** | PARTIAL | Test stubs/skeletons written. Need to refine tests to genuinely test constraints. |

## Next Steps
1. Ensure API AI routes utilize proper dynamic inference rather than mock stubs.
2. Verify the CP-SAT Optimizer mathematically enforces all 10 hard constraints.
3. Finalize deterministic Baseline generator and Validator.
4. Connect React frontend to actual FastAPI endpoints.

## FINAL HARDENING AND VERIFICATION REPORT (SIH26027)

### 1. What is Implemented
* **Backend Database & API**: SQLite database, SQLAlchemy models, Pydantic serialization, and FastAPI routing for all core services (Assets, Maintenance, Trains, Corridors, Blocks, Analytics).
* **AI & Machine Learning**: Synthetic data generation, scikit-learn models (Priority, Risk, Impact), and automated .joblib artifact management. Models serve real predictions.
* **CP-SAT Optimizer**: Implements 10 core constraints, including overlapping trains, overlapping blocks on corridors, required resources, dependent tasks, corridor availability windows, department compatibility, and max 8-hour block durations.
* **Independent Schedule Validation**: ValidationService mathematically verifies that the CP-SAT output (blocks) respects time durations, max durations, corridor overlap, and train conflicts using plain Python logic, acting as a failsafe against optimizer bugs.
* **Frontend Application**: React + Vite UI with charts (Recharts) and data tables, fully wired to the backend API via Axios.

### 2. What is Partially Implemented
* **User Authentication**: This is a hackathon prototype, so identity/auth is currently mock/bypassed.
* **Real-time Streaming**: WebSocket updates for Gantt chart live tracking are mocked/absent.

### 3. What Remains
* Hardware deployment mapping.
* Productionizing the database (e.g. migrating to PostgreSQL).

### 4. Test Results
* **Test Suite**: 20/20 Passing (pytest tests/ -v).
* **E2E Pipeline**: Verified end-to-end (AI -> CP-SAT -> Validation -> FastAPI -> React). 

### 5. How to Start Backend
`ash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
`

### 6. How to Start Frontend
`ash
cd frontend
npm run dev
`

### 7. How to Seed Demo Data
`ash
cd backend
set PYTHONPATH=.
python scripts/seed_demo_data.py
`
*(This script is fully idempotent and safely wipes old test data before reseeding).*

### 8. How to Generate a Planning Result
Using the Frontend:
1. Navigate to http://localhost:5173/plan/generate
2. Select "Weekly" or "Monthly" horizon.
3. Click "Generate Plan" and review the AI and CP-SAT results, along with the validation report, before clicking "Approve".

Using the API directly:
`ash
Invoke-RestMethod -Uri "http://localhost:8000/api/planning/generate?horizon=weekly" -Method Post
`

### 9. Known Limitations
* The AI dataset is synthetically generated via programmatic rules rather than real historical railway telemetry.
* Large multi-month horizons may hit the 30-second CP-SAT optimizer time limit and fall back to the Baseline heuristics if it cannot find a feasible block schedule in time.
