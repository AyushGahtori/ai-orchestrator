# AI Orchestrator — README & Developer Reference

This README is a single-stop reference describing the repository, what each file does, the full API surface and where it is implemented, and the exact locations where agent containers and the runner will be attached later.

Contents

- Project overview
- Quick start (local / docker)
- File map — what each important file/folder does (exact paths)
- Complete API reference (endpoint → file path)
- Placeholder & integration locations (exact files and spots to edit to integrate containers / Cloud Run)
- Environment variables
- Tests
- Next steps and recommended production changes

---

Project overview

AI Orchestrator is a demo orchestration interface that centralizes messages and file exchange between three agents: Generator, Coder, and Evaluator. The backend is FastAPI and the frontend is a React app (Tailwind). The backend stores tasks, code versions, messages, results and simulated container records in SQLite and the storage/ folder.

Quick start (development)

1) Backend (PowerShell)

```powershell
python -m pip install -r backend/requirements.txt
# ensure .env exists (we provide a default .env in the repo)
python -m backend.app
```

The API will run at http://localhost:8000 (or the PORT set in `.env`).

2) Frontend (PowerShell)

```powershell
cd frontend
npm install
npm start
```

The React dev server runs at http://localhost:3000 and uses `frontend/.env.development` values at runtime.

Run with Docker (both services)

```powershell
docker-compose up --build
```

---

File map — primary files & purpose (exact paths)

Backend (FastAPI)
- `backend/app.py` — application entrypoint; loads environment variables and registers all routers. Modify CORS and startup hooks here.
- `backend/database.py` — SQLite connection utilities and `init_db()` which creates tables: `tasks`, `code`, `results`, `messages`, `containers`.
- `backend/models.py` — Pydantic schemas for incoming requests and payload validation.
- `backend/requirements.txt` — Python dependencies (fastapi, uvicorn, pydantic, python-dotenv, ...).

Routes (each router is in `backend/routes/`):
- `backend/routes/tasks.py` — Task management endpoints (create/list/get/update).
- `backend/routes/code.py` — Code upload/list/delete and the `GET /download_code/{task_id}/{version}` endpoint.
- `backend/routes/logs.py` — Upload results, get results, messages, `GET /get_logs/{task_id}` and `GET /download_log/{task_id}/{filename}`.
- `backend/routes/feedback.py` — Feedback endpoints (`/upload_feedback`, `/get_feedback/{task_id}`).
- `backend/routes/containers.py` — Container placeholder endpoints and the simulated job queue (`/spawn_container`, `/container_status/{id}`, `/container/{id}`); contains the simulation timer that marks jobs complete after 10s.
- `backend/routes/admin.py` — Health and `/stats` (extended to include counts, avg accuracy, avg runtime, active containers).

Utilities
- `backend/utils/auth.py` — Simple API key enforcement via `X-API-KEY`. Reads `DEMO_API_KEY` from `.env`.
- `backend/utils/file_manager.py` — Helpers to save code files and logs under `storage/`.

Frontend (React)
- `frontend/src/services/api.js` — Axios wrapper (reads `REACT_APP_API_BASE` and `REACT_APP_API_KEY` from `frontend/.env.development`).
- `frontend/src/components/Dashboard.js` — Top-level dashboard; includes summary cards that call `/stats`.
- `frontend/src/components/TaskDetail.js` — Task detail view with tabs; includes polling (every 10s) and a Logs tab that uses `/get_logs` and `/download_log`.
- `frontend/src/components/CodeViewer.js` — Code versions list and a modal that fetches `/download_code/{task_id}/{version}` and shows the code (syntax highlighted) with a Copy button.
- `frontend/src/components/AgentChat.js` — Message timeline and `POST /upload_message`.
- `frontend/src/components/LiveMonitor.js`, `MetricsGraph.js` — mock visualizers for live runs and metrics.
- `frontend/package.json` — scripts and dependencies (includes `react-syntax-highlighter` and a `format` script using Prettier).

Storage / DB
- `storage/` — top-level folder for persisted files
  - `storage/code/{task_id}/{version}/` — uploaded code files
  - `storage/logs/{task_id}/{run_id}/` — stored logs
- `database/orchestrator.db` — SQLite DB (created automatically by `init_db()` on startup)

---

API reference (endpoint → file path)

All endpoints require the header `X-API-KEY: <key>` (default demo key is `demo_key`, set via `.env`).

Task Management
- POST `/upload_task` — create a task (file: `backend/routes/tasks.py`)
- GET `/get_tasks` — list tasks (file: `backend/routes/tasks.py`)
- GET `/get_task/{id}` — get task details (file: `backend/routes/tasks.py`)
- PUT `/update_task/{id}` — update task status (file: `backend/routes/tasks.py`)

Code Handling
- POST `/upload_code` — upload code (multipart/form-data or `file_content` in form) (file: `backend/routes/code.py`)
- GET `/get_code/{task_id}` — list versions (file: `backend/routes/code.py`)
- GET `/get_code/{task_id}/{version}` — get metadata for specific version (file: `backend/routes/code.py`)
- GET `/download_code/{task_id}/{version}` — download the actual code file as plain text/attachment (file: `backend/routes/code.py`)
- DELETE `/delete_code/{id}` — delete code record (file: `backend/routes/code.py`)

Logs & Results
- POST `/upload_results` — upload run results and raw logs (file: `backend/routes/logs.py`)
- GET `/get_results/{task_id}` — get all past run results (file: `backend/routes/logs.py`)
- GET `/get_latest_results/{task_id}` — get the most recent metrics (file: `backend/routes/logs.py`)

Agent Communication
- POST `/upload_feedback` — evaluator posts feedback (file: `backend/routes/feedback.py`)
- GET `/get_feedback/{task_id}` — coder fetches feedback (file: `backend/routes/feedback.py`)
- POST `/upload_message` — append a general message to the timeline (file: `backend/routes/logs.py`)
- GET `/get_messages/{task_id}` — retrieve chronological message log (file: `backend/routes/logs.py`)

Logs / Files
- GET `/get_logs/{task_id}` — aggregates all stored logs for a task and returns JSON list with `filename`, `modified` timestamp, and a `preview` (first ~50 lines). (file: `backend/routes/logs.py`)
- GET `/download_log/{task_id}/{filename}` — returns an existing log file as a downloadable text response (file: `backend/routes/logs.py`)

Container / Runner (simulated)
- POST `/spawn_container` — create a simulated container job (file: `backend/routes/containers.py`). The current implementation inserts a row into the `containers` table with `status='running'` and then marks the job `completed` after 10 seconds using `threading.Timer`. Replace this function to actually call Cloud Run or a job runner.
- GET `/container_status/{container_id}` — returns the DB record for a container (file: `backend/routes/containers.py`)
- DELETE `/container/{container_id}` — delete container record (file: `backend/routes/containers.py`)

Admin / Utility
- GET `/healthcheck` — quick API health check (file: `backend/routes/admin.py`)
- GET `/stats` — system stats: `total_tasks`, `completed_tasks`, `avg_accuracy`, `avg_runtime`, `active_containers` (file: `backend/routes/admin.py`)

---

Where to plug in Agents and container-runner (exact locations)

These are the exact code locations and suggested change points so you or another developer can quickly integrate each agent or a runner service:

- Generator Agent
  - Integration point: create tasks by calling `POST /upload_task`.
  - Example place to reference in code/README: `backend/routes/tasks.py`.
  - Suggested container-side behavior: after task creation the Generator can upload a starting message via `POST /upload_message`.

- Coder Agent
  - Responsible for writing code and uploading it via `POST /upload_code`.
  - To fetch evaluator feedback, Coder should poll `GET /get_feedback/{task_id}`.
  - Integration hooks (where to modify or call from a container):
    - Upload code: `backend/routes/code.py`
    - Read feedback: `backend/routes/feedback.py`

- Evaluator Agent
  - Responsible for evaluating runs and posting results and feedback.
  - Upload run outputs and logs via `POST /upload_results` (`backend/routes/logs.py`).
  - Post textual feedback via `POST /upload_feedback` (`backend/routes/feedback.py`).

- Runner Service (the component that actually executes uploaded code inside a container)
  - Current simulated entry: `backend/routes/containers.py` — `POST /spawn_container`.
  - Replace the simulation in `backend/routes/containers.py` with code that:
    1. Pulls the code file path from the `code` table (stored_path) or the storage path `storage/code/{task_id}/{version}` (see `backend/utils/file_manager.py`).
    2. Builds a container or starts a Cloud Run Job / Cloud Run service with mounted code (or downloads the script into the container at runtime).
    3. Streams logs to the `results` table or into `storage/logs/{task_id}/{run_id}` (use `backend/utils/file_manager.py::save_log_file`).
  - Exact place to modify: `backend/routes/containers.py` — search for `# simulate a job` and replace that block with GCP SDK calls or your runner API.

Exact file path references for the runner & placeholders
- Container spawn simulation & placeholder to replace: `backend/routes/containers.py` (function `spawn_container` and helper `complete_job_later`).
- Where code files are stored and how to locate them from the backend: `backend/utils/file_manager.py` (see `save_code_file`) — code files put under `storage/code/{task_id}/{version}`.
- Where logs are written when `POST /upload_results` is called: `backend/routes/logs.py` calls `backend/utils/file_manager.py::save_log_file` which writes into `storage/logs/{task_id}/{run_id}/`.

---

Environment variables (important)

- Repo root `.env` (backend) — values used by FastAPI app:
  - `DEMO_API_KEY` — the API key required in `X-API-KEY` header. Default in repo: `demo_key`.
  - `PORT` — backend listening port (default 8000).
  - `API_TITLE` — application title shown by FastAPI.
  - `CORS_ORIGINS` — origins allowed for CORS (default `*` for dev).

- Frontend `.env.development` (frontend) — values used by React dev server:
  - `REACT_APP_API_BASE` — base API URL (default `http://localhost:8000`).
  - `REACT_APP_API_KEY` — API key used by the frontend axios client.

---

Tests

- Basic tests are provided under `backend/tests/test_endpoints.py` using FastAPI `TestClient`. They exercise `upload_task`, `upload_results`, and `upload_code` (via form data). Run with `pytest`.

Example:

```powershell
pip install pytest
pytest -q
```

---

Practical integration checklist (how to wire a Runner/Cloud Run)

1. Make a copy of `backend/routes/containers.py` and implement the real `spawn_container` function to call Cloud Run or your orchestrator API.
   - Use GCP's Python SDK or call the REST API.
   - Use a Service Account with proper permissions (Cloud Run Admin, IAM).
2. Before starting the container, fetch the code path for `task_id/version` from the `code` table (or rely on `storage/code/{task_id}/{version}`) and make it available to the runner (mount, download, or bake into image).
3. Stream logs to a persistent store: call `backend/utils/file_manager.save_log_file` to persist run logs and insert any metric rows into `results` table.
4. Update `spawn_container` to report real container IDs and keep the `/container_status/{container_id}` implementation to reconcile and report real-time status.

---

Notes & caveats

- This project is a demo/hackathon scaffold — containers are simulated. Replace the simulation code in `backend/routes/containers.py` with real orchestration when you are ready to deploy.
- Replace `DEMO_API_KEY` with a proper secret store (GCP Secret Manager) and migrate to OAuth/JWT for user-level auth in production.
- The frontend uses Tailwind but minimal PostCSS/Tailwind build wiring is included; you might need to initialize Tailwind in your CRA setup for full styling.

If you want, I can next:

- Implement Cloud Run calls inside `backend/routes/containers.py` (I will prepare the Cloud Run SDK code — you will need to provide project and service account details).
- Add a small suite of frontend E2E tests to exercise the dashboard flows.
- Add a raw JSON endpoint to fetch code content (instead of FileResponse) for simpler AJAX usage.

Thank you — this README now contains exact file locations, complete endpoint mapping, and explicit integration points so you or any developer can integrate agent containers and the runner service quickly.
# AI Orchestrator

Central interface for coordinating three AI agents (Generator, Coder, Evaluator). This repo provides a FastAPI backend and a React + Tailwind frontend dashboard that demos agent orchestration flows. Container runner endpoints are placeholders to be integrated with Google Cloud Run later.

Structure

 - backend/: FastAPI backend with routes, auth, and file utilities
 - frontend/: React app (Tailwind) for dashboard and visualizations
 - storage/: File storage for tasks, code versions, logs
 - database/orchestrator.db: SQLite DB (created on startup)
 - Dockerfile.backend, Dockerfile.frontend, docker-compose.yml

Run locally (development)

1. Backend (Python)

   - Install dependencies

     python -m pip install -r backend/requirements.txt

   - Start server

     python -m backend.app

   The API will be available at http://localhost:8000

2. Frontend (React)

   - Install node deps

     cd frontend; npm install

   - Start dev server

     npm start

   The app will be available at http://localhost:3000 (configured to point to backend at :8000)

Run with Docker (demo)

  docker-compose up --build

API Overview

Authentication

 - Simple API Key: set X-API-KEY header to demo_key (see backend/utils/auth.py)

Task Management

 - POST /upload_task - Create new task
 - GET /get_tasks - List all tasks
 - GET /get_task/{id} - Get task details
 - PUT /update_task/{id} - Update task status

Code Handling

 - POST /upload_code - Upload code version (multipart/form-data or form with file_content)
 - GET /get_code/{task_id} - List code versions
 - GET /get_code/{task_id}/{version} - Get metadata for specific version
 - DELETE /delete_code/{id} - Delete code
 - GET /download_code/{task_id}/{version} - Download raw code file (attachment/plain text)

Logs & Metrics

 - POST /upload_results - Submit run results (accuracy, loss, raw_logs)
 - GET /get_results/{task_id} - Get all results
 - GET /get_latest_results/{task_id} - Get latest metrics
 - POST /upload_message - Log a message (chat/timeline)
 - GET /get_messages/{task_id} - Get chronological messages
 - GET /get_logs/{task_id} - Aggregate stored log files for a task (filename, modified, preview)
 - GET /download_log/{task_id}/{filename} - Download a stored log file

Agent Communication (integration points)

 - Generator: will call POST /upload_task to create tasks
   # --- Placeholder: attach Generator container here ---

 - Coder: will call POST /upload_code and periodically GET /get_feedback
   # --- Placeholder: attach Coder container here ---

 - Evaluator: will call POST /upload_feedback and POST /upload_results
   # --- Placeholder: attach Evaluator container here ---

Runner / Containers (placeholder)

 - POST /spawn_container - Simulate spawning a container for runs
 - GET /container_status/{id} - Simulate container status/logs
 - DELETE /container/{id} - Simulate container deletion
   # --- Placeholder: integrate with Google Cloud Run SDK here ---

Notes for Deployment to Cloud Run

 - Containerize backend and frontend (Dockerfiles included). Build and push images to Google Container Registry then deploy to Cloud Run.
 - For secure API keys use Secret Manager; replace demo key in backend/utils/auth.py.

Environment

 - Backend loads configuration from `.env` (DEMO_API_KEY, PORT, API_TITLE, CORS_ORIGINS). Update values before deploying.
 - Frontend reads `.env.development` for REACT_APP_API_BASE and REACT_APP_API_KEY used during development.

Running tests

 - Backend has simple tests using FastAPI TestClient in `backend/tests/test_endpoints.py`. Run with pytest (install dev deps).


Next steps / TODO for full integration

 - Implement agent containers and point them to API endpoints
 - Replace API key with OAuth/JWT or GCP IAM
 - Hook /spawn_container to GCP Cloud Run Admin API to start runs
 - Add user/auth frontend and role-based access
