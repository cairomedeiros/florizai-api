# LeafChat API

Backend for a plant care app: plant management, photo uploads with async thumbnail
generation, automated watering reminders, Redis caching, and an **AI assistant (RAG)**
that answers plant-care questions grounded in a document base.

## Tech stack

| Area | Tech |
|------|------|
| Language | Python 3.13 |
| Package manager | uv |
| Web framework | FastAPI (`fastapi[standard]`) |
| Database / ORM | PostgreSQL (Supabase) + SQLAlchemy 2.0 + Alembic |
| Cache | Redis |
| Background jobs | APScheduler (watering reminders) |
| Images | Pillow (thumbnails) |
| AI / RAG | ChromaDB (vector store) + Groq (LLM inference) + pypdf |

---

## Prerequisites

- **Python 3.13** installed.
- **uv** installed globally:
  ```bash
  pip install uv
  ```

## Setup

1. **Install dependencies** (creates `.venv` and installs everything from `pyproject.toml`/`uv.lock`):
   ```bash
   uv sync
   ```

2. **Create a `.env`** at the project root (see [Environment variables](#environment-variables)).

3. **Run database migrations**:
   ```bash
   uv run alembic upgrade head
   ```

## Running the API

```bash
fastapi dev main.py
```

The server starts at `http://127.0.0.1:8000`. Interactive docs (Swagger) at `http://127.0.0.1:8000/docs`.

---

## Environment variables

The app reads these from `.env` (see `config/settings.py`). All are **required**:

```env
SUPABASE_URL=...
SUPABASE_PUBLISHABLE_KEY=...
SUPABASE_SECRET_KEY=...
DATABASE_URL=postgresql://user:password@host:port/dbname
GROQ_API_KEY=...            # free at https://console.groq.com (this is Groq, NOT Grok/xAI)
```

> `.env` is gitignored — never commit it.

---

## AI assistant (RAG) — setup

The `/ai/ask` endpoint retrieves relevant chunks from a local vector store and uses Groq to
answer based on them. Two extra steps are needed before it works:

### 1. Add documents

Drop the source documents into `docs/` (supported: `.pdf`, `.md`, `.txt`).

> `docs/*.pdf` and `chroma/` are gitignored (third-party content / generated artifact), so a
> fresh clone needs its own docs added before ingestion.

### 2. Build the vector store

```bash
uv run python scripts/ingest.py
```

This reads every doc in `docs/`, splits it into ~1000-char chunks, embeds each chunk, and
persists them to `./chroma`. Prints `X chunks from N docs`. **Re-run whenever `docs/` changes.**

> **Why ChromaDB with no embedder config?** Chroma ships with a built-in default embedder
> (`all-MiniLM-L6-v2`) that runs locally on CPU — no extra API key, no embedding service, works
> offline. The vector store is just the `./chroma` folder on disk. This keeps the setup
> dependency-free for an MVP; a production version would likely move to pgvector (Postgres is
> already in the stack) or a dedicated vector DB.

### 3. (Optional) Evaluate retrieval quality

```bash
uv run python scripts/eval.py
```

Runs a fixed set of test questions and reports **Hit Rate@k** — how often the expected chunk is
retrieved in the top-k. Useful to compare retrieval quality after tuning chunk size / `n_results`.

### Try it

```http
POST /ai/ask
{ "question": "what plants are good for shade?" }
```

Returns `{ answer, sources[], confidence }`.

---

## Project structure

```
main.py                 # app entrypoint, router registration, lifespan (scheduler)
config/                 # settings, database, supabase clients
routers/                # API routes (user, plant, chat, message, plant_pictures, watering_events, ai)
services/               # business logic (scheduler, etc.)
models/                 # SQLAlchemy models
schemas/                # Pydantic schemas
enums/                  # shared enums
auth/                   # auth
alembic/                # database migrations
scripts/                # ingest.py (build vector store), eval.py (retrieval eval)
docs/                   # RAG source documents (gitignored)
chroma/                 # generated vector store (gitignored)
```
