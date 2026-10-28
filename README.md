# FlorizAI API

Backend for a plant care app: plant management, photo uploads with async thumbnail
generation, automated watering reminders, Redis caching, and an **AI assistant (RAG)**
that answers plant-care questions grounded in a document base.

Mobile app (Expo / React Native): [florizai](https://github.com/cairomedeiros/florizai).

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

## RAG: design decisions

**ChromaDB with its built-in embedder, not pgvector (yet).** Zero infra: no extra server, no
embedding API key, the vector store is a folder on disk. That keeps the retrieval → prompt → LLM
flow small and easy to inspect. Postgres is already in the stack, so pgvector is the natural next
step once the corpus or the number of services grows; before that it would be cost without benefit.

**Fixed-size chunks (1000 chars, 200 overlap).** Simplest thing that works on two PDFs. The overlap
keeps sentences that cross a boundary retrievable from either side.

**Top-8 instead of top-3.** The corpus is small (63 chunks), so pulling more neighbours is almost
free and catches relevant chunks whose embedding got noisy from table-heavy PDF text. With a bigger
corpus this should become re-ranking, not a bigger `n_results`.

**`confidence` is a heuristic.** It is `1 - distance` of the best chunk, a rough signal for the UI
("low confidence → warn the user"), not a calibrated probability.

**Evaluate retrieval before tuning the prompt.** If the right chunk never reaches the LLM, no prompt
fixes it. So `scripts/eval.py` measures retrieval on its own (Hit@k and MRR) and runs in seconds,
with no LLM call.

## RAG: current results

| Metric | Value |
|--------|-------|
| Hit@3 | 2/4 |
| Hit@8 | 2/4 |
| MRR | 0.50 |

The eval set is small (4 questions), so treat this as a baseline, not a benchmark.

**What the misses show:** both failures are light questions ("low light", "bright light"). The top
results are chunks about the *physics* of light (PPFD, spectrum, grow lamps) from the more technical
PDF, while the care-guide chunks that actually answer the question rank lower. The default
embedder matches the topic ("light") but not the intent ("which plants / how much").

## RAG: known limitations and next steps

- **Grounding isn't guaranteed.** The prompt says "answer using ONLY the context", but the model
  sometimes adds plants that aren't in the retrieved chunks. Next: ask for per-chunk citations and
  check them against `sources`.
- **The eval set is too small** to compare changes reliably. Next: ~20 paraphrased questions.
- **English-only embedder.** Questions in Portuguese against English docs retrieve worse. Next: a
  multilingual embedding model.
- **Noisy PDF extraction.** `pypdf` flattens tables and columns. Next: `pymupdf`/`pdfplumber` if the
  corpus keeps table-heavy PDFs.
- **Then:** move to pgvector, re-run the eval, and compare.

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
