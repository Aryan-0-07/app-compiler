# App Compiler 🚀

An AI-powered multi-stage pipeline that works like a compiler —
takes a natural language prompt and outputs a complete, validated,
executable app configuration.

## What it does

**Input:**
"Build a CRM with login, contacts, dashboard, role-based access, and payments"

**Output:**
Complete validated JSON config with UI + API + DB + Auth schemas
that is proven executable via runtime checks.

## Pipeline Architecture

    Natural Language
          ↓
    Stage 1 — Intent Extraction
    Parses entities, roles, features, assumptions
          ↓
    Stage 2 — Architecture Design
    Entity relationships, flows, page structure
          ↓
    Stage 3 — Schema Generation (4 parallel)
    DB Schema · API Schema · UI Schema · Auth Schema
          ↓
    Stage 4 — Validation + Repair Engine
    5 cross-layer checks · Surgical repair (not brute retry)
          ↓
    Runtime Executor
    SQLite in-memory · API endpoint validation

## Key Features

- **Multi-stage pipeline** — not a single prompt
- **Surgical repair engine** — detects which layer failed and fixes only that layer
- **Cross-layer validation** — UI fields map to API endpoints which map to DB columns
- **Runtime execution proof** — DB schema runs in SQLite, API endpoints validated
- **Evaluation framework** — 20 test cases with real metrics

## Eval Results

| Metric | Result |
|--------|--------|
| Real prompts (10/10) | 100% success |
| Edge cases (5/10) | 50% success |
| Runtime success | 70% |
| Avg latency | 93s |
| Total repairs | 11 |

## Tech Stack

- **Backend** — Python, FastAPI, Pydantic v2
- **Frontend** — React, Vite
- **AI Model** — Groq API (llama-3.1-8b-instant)
- **Runtime** — SQLite in-memory
- **Validation** — Pydantic v2 cross-layer consistency checks

## Project Structure

    app-compiler/
    ├── pipeline/
    │   ├── stage1_intent.py        # Intent extraction
    │   ├── stage2_architecture.py  # Architecture design
    │   ├── stage3_schemas.py       # Schema generation
    │   └── stage4_refinement.py    # Validation + repair
    ├── schemas/                    # Pydantic contracts
    ├── validators/                 # Cross-layer checks
    ├── repair/                     # Targeted repair engine
    ├── runtime/                    # Execution simulator
    ├── eval/                       # Evaluation framework
    ├── api/                        # FastAPI backend
    └── ui/                         # React frontend

## How to Run Locally

**Backend**

```bash
git clone https://github.com/Aryan-0-07/app-compiler
cd app-compiler
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
echo GROQ_API_KEY=your_key_here > .env
uvicorn api.main:app --reload --port 8000
```

**Frontend**

```bash
cd ui
npm install
npm run dev
```

Open http://localhost:5173

## How it Works

1. Type a natural language prompt describing your app
2. Click **Generate App Config**
3. The 4-stage pipeline runs automatically
4. Results show in tabbed UI — Summary, DB, API, UI, Auth, Log
5. Log tab shows runtime execution proof

## Evaluation

Run the full evaluation framework:

```bash
python eval/runner.py
```

View results at http://localhost:8000/eval/results