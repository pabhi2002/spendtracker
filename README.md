# Spend Tracker — Mini Expense Tracking API + UI

A lightweight expense tracking service with a Python REST API (FastAPI + SQLite) and a minimal HTML/JS frontend.

## Quick Start

### Prerequisites

- Python 3.10+
- pip

### 1. Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Run the API server

```bash
cd backend
uvicorn app.main:app --reload
```

The API will be available at **http://localhost:8000**.  
Interactive API docs (Swagger): **http://localhost:8000/docs**

### 3. Open the frontend

The frontend is served by FastAPI itself. Once the server is running, open:

👉 **http://localhost:8000/ui/**

No separate server or file:// needed — the UI talks to the API on the same origin.

### 4. Run tests

```bash
cd backend
pytest -v
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/expenses` | Create an expense (`amount`, `category`, `note`, `date`) |
| `GET` | `/expenses` | List expenses — optional `?category=`, `?start_date=`, `?end_date=` |
| `GET` | `/summary` | Total spend, per-category breakdown, month-over-month change, alerts |
| `GET` | `/` | Health check |
| `GET` | `/ui/` | Frontend UI (served as static files) |

### Authentication (optional)

Pass `X-API-Key: dev-api-key-change-me` header. Configurable via `API_KEY` env var.  
Auth is non-mandatory in dev mode so the app works out of the box.

---

## Key Design Decisions

| Decision | Why |
|----------|-----|
| **FastAPI** | Automatic request validation via Pydantic, auto-generated OpenAPI docs, async support, and widely adopted in the Python ecosystem |
| **SQLAlchemy ORM** | Clean schema definition, portable across databases, easy to add migrations (Alembic) later |
| **SQLite** | Zero-config file-based DB — ideal for a take-home; trivial to swap to PostgreSQL for production |
| **Pydantic v2** | Tight FastAPI integration, fast validation, clear error messages |
| **API Key auth** | Simplest "real" auth pattern that demonstrates the middleware/dependency pattern without over-engineering |
| **In-memory SQLite for tests** | Fast, fully isolated tests — no cleanup needed between runs |
| **Plain HTML/JS frontend** | Requirements say "design won't be evaluated" — keeping it minimal avoids unnecessary complexity while proving end-to-end functionality |

### Bonus Features

- **Spend spike alerts**: The `/summary` endpoint flags any category where spending increased >20% compared to the previous month
- **API key authentication**: Simple `X-API-Key` header auth with configurable key

---

## What I'd Do Differently With More Time

1. **Pagination** — `GET /expenses` currently returns all results; would add `limit`/`offset` or cursor-based pagination
2. **Database migrations** — Use Alembic for schema versioning instead of `create_all()`
3. **Proper auth** — JWT tokens with user accounts instead of a shared API key
4. **Frontend framework** — React or Vue with proper state management, charts (Chart.js), and responsive design
5. **CI/CD** — GitHub Actions pipeline for lint, test, and deploy
6. **Deployment** — Dockerfile + deploy to Render/Railway with PostgreSQL
7. **Input sanitization** — More robust category normalization (aliases, typo correction)
8. **Budgets** — Let users set category budgets and alert when exceeded

---

## AI Tools Usage

This project was built with the assistance of an AI coding assistant (Google Antigravity / Gemini). The AI helped scaffold the project structure, generate boilerplate code, and draft tests. I reviewed all generated code for correctness, adjusted the summary computation logic (month-over-month calculation and alert thresholds), refined input validation rules, and ensured the test suite covers both happy paths and edge cases.

---

## Project Structure

```
spendtracker/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app entry point
│   │   ├── database.py      # SQLAlchemy engine + session
│   │   ├── models.py        # ORM models
│   │   ├── schemas.py       # Pydantic request/response schemas
│   │   ├── auth.py          # API key authentication
│   │   └── routers/
│   │       ├── expenses.py  # POST/GET /expenses
│   │       └── summary.py   # GET /summary
│   ├── tests/
│   │   ├── conftest.py      # Test fixtures
│   │   ├── test_expenses.py # Expense endpoint tests
│   │   └── test_summary.py  # Summary endpoint tests
│   └── requirements.txt
├── frontend/
│   └── index.html           # Minimal UI
└── README.md
```
