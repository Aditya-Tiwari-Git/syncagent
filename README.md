<div align="center">

# 🎬 SyncAgent

**Intelligent AI Music Pre-Clearance Assistant for Filmmakers**

*Bridge the gap between cinematic creative intent and deterministic licensing reality.*

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg?logo=react&logoColor=black)](https://react.dev/)
[![Google ADK & Vertex AI](https://img.shields.io/badge/Google_Cloud-Vertex_AI_%7C_ADK-4285F4.svg?logo=googlecloud&logoColor=white)](https://cloud.google.com/vertex-ai)
[![ClickHouse](https://img.shields.io/badge/ClickHouse-Cloud-FFCC01.svg?logo=clickhouse&logoColor=black)](https://clickhouse.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

---

> **⚠️ Legal Notice:** SyncAgent is an automated pre-clearance workflow tool evaluating catalog metadata against explicit rules. It **does not** establish copyright ownership, execute licensing agreements, or replace definitive verification with rights holders.

---

## 💡 Overview

Filmmakers often cut scenes to temp tracks that sound pitch-perfect in the edit suite—only to encounter dealbreaking legal barriers downstream: prohibitive sync fees, blocked commercial clearance, or territorial exclusions.

**SyncAgent solves this early.** It pairs **Gemini's contextual scene understanding** with **deterministic, code-level licensing guardrails**. Creative exploration is unbounded; clearance validation is absolute.

---

## ⚡ Architecture & Workflow

SyncAgent splits responsibilities strictly: **creative interpretation is handled by an LLM, while rights evaluation is entirely deterministic.**

```text
Filmmaker Scene Description + Licensing Parameters (Budget, Territory, Commercial Scope)
                                │
                                ▼
         [ Gemini via Vertex AI / Google ADK Supervisor ]
         Extracts mood, tempo (BPM), energy, genre, instrumentation
                                │
                                ▼
               [ ClickHouse Cloud Catalog Search ]
               Filters matching candidate tracks at scale
                                │
                                ▼
             [ Deterministic Rights Validation Engine ]
             Enforces hard boundaries: budget, territory, sync, commercial use
                                │
                                ▼
               [ Transparent Compatibility Scoring ]
               Ranks rights-passing tracks across 6 musical dimensions (0-100)
                                │
                                ▼
         Recommendations + Transparent Rejections + Exportable PDF
```

### Operational Modes
* **Fast API Mode (`SYNCAGENT_API_MODE=fast`, Default):** Executes a single Gemini call for scene analysis, offloading search, rights logic, and ranking to deterministic Python and ClickHouse routines for lower latency and token efficiency.
* **Agentic ADK Mode (`SYNCAGENT_API_MODE=adk`):** Invokes the complete multi-step Google ADK supervisor conversation and tool loop—ideal for deep agentic inspection and debugging.

---

## 🧰 Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Agent Orchestration** | Google Agent Development Kit (ADK), Vertex AI Gemini |
| **Backend API** | Python 3.11, FastAPI, Pydantic, ReportLab (PDF Engine) |
| **Catalog Database** | ClickHouse Cloud (Direct TCP or optional MCP server) |
| **Frontend UI** | React, TypeScript, Vite, Tailwind CSS, Lucide Icons |
| **Infrastructure** | Google Cloud Run (API), Firebase Hosting (Frontend), Google Secret Manager |

---

## 📁 Repository Structure

```text
syncagent/
├── backend/
│   ├── agent_runner.py          # Local Google ADK CLI runner
│   ├── api.py                   # FastAPI service endpoints
│   ├── agents/
│   │   └── root_agent.py        # ADK Root Supervisor Agent definition
│   ├── models/                  # Pydantic schemas (requests, track entities, analysis)
│   ├── services/                # Gemini client, ClickHouse driver, rights & ranking engines
│   └── tools/                   # ADK-compatible tool interfaces
├── frontend/                    # React / Vite / Tailwind UI application
├── database/
│   ├── schema.sql               # ClickHouse catalog DDL
│   └── seed_catalog.py          # Deterministic demo & synthetic seeding script
├── docs/                        # Deployment runbooks and demonstration scripts
├── tests/
│   ├── scenarios.py             # 20 predefined deterministic API test cases
│   └── run_scenarios.py         # Test runner for live backend instances
├── Dockerfile                   # Production container definition for Cloud Run
└── requirements.txt             # Core Python runtime dependencies
```

---

## 🚀 Quickstart

### Prerequisites
* Python 3.11+
* Node.js 18+ & npm
* Active Google Cloud project with Vertex AI enabled
* Configured ClickHouse Cloud instance

### 1. Environment Configuration

Clone the repository and prepare local environment files:

```bash
git clone [https://github.com/your-org/syncagent.git](https://github.com/your-org/syncagent.git)
cd syncagent
cp .env.example .env
```

Populate `.env` with your project parameters:

```ini
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=true
CLICKHOUSE_HOST=your-clickhouse-host.clickhouse.cloud
CLICKHOUSE_PORT=8443
CLICKHOUSE_DATABASE=default
CLICKHOUSE_USER=your-clickhouse-user
CLICKHOUSE_PASSWORD=your-clickhouse-password
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000
CORS_ORIGINS=http://localhost:5173,[http://127.0.0.1:5173](http://127.0.0.1:5173)
```

Authenticate your local environment to Google Cloud via Application Default Credentials (ADC):

```bash
gcloud auth application-default login
```

### 2. Backend Setup & Seeding

Create a virtual environment and seed the ClickHouse catalog:

```bash
python -m venv .venv
# On Linux/macOS:
source .venv/bin/activate
# On Windows (PowerShell):
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt -r requirements-dev.txt

# Seed catalog with baseline deterministic tracks and synthetic pool
python database/seed_catalog.py --count 200 --seed 42
```

Start the local API:

```bash
uvicorn backend.api:app --reload --port 8000
```
* Interactive API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)

### 3. Frontend Setup

In a separate terminal:

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```
* Web Dashboard: [http://localhost:5173](http://localhost:5173)

---

<!-- ## 🧪 Testing & ADK CLI

Run the test suite and verify static compilation:

```bash
pytest -q
python -m compileall -q backend database tests
```

Execute the **20 real-world automated scenarios** against the running backend:

```bash
# Run a specific scenario
python tests/run_scenarios.py --scenario "Late Night Detective"

# Run the complete test suite
python tests/run_scenarios.py --all
```

To run the local ADK in-memory supervisor session directly in CLI:

```bash
python -m backend.agent_runner
```

--- -->

## 📡 API Reference

### Analyze Scene & Match Tracks

`POST /api/analyze`

**Request Body:**
```json
{
  "scene_description": "An exhausted detective walks through an empty Mumbai street at 2 AM after failing to solve a case.",
  "budget": 800,
  "territory": "Worldwide",
  "top_k": 5
}
```

**Response Format:**
```json
{
  "scene_analysis": {
    "mood": "Melancholic / Brooding",
    "tempo_range": [65, 85],
    "energy_level": 0.3,
    "genres": ["Noir Jazz", "Dark Ambient", "Down-tempo"],
    "instrumentation": ["Muted Trumpet", "Upright Bass", "Subtle Rhodes"]
  },
  "recommendations": [
    {
      "track_id": "TRK-DEMO-003",
      "title": "Rain on Asphalt",
      "artist": "Midnight Trio",
      "score": 94.2,
      "price": 650.0,
      "territory": "Worldwide",
      "sync_cleared": true,
      "commercial_use": true
    }
  ],
  "rejected_candidates": [
    {
      "track_id": "TRK-DEMO-009",
      "title": "Neon Chase",
      "reason": "License price ($1,200) exceeds maximum budget ($800)"
    }
  ],
  "total_candidates": 24,
  "disclaimer": "This report is an automated pre-clearance assessment..."
}
```

### Export Clearance Report

`POST /api/report`

Takes the same JSON request payload as `/api/analyze` and returns a generated pre-clearance summary as a downloadable `syncagent-pre-clearance-report.pdf`.

---

## 🚢 Deployment

SyncAgent is engineered for containerized deployment on **Google Cloud Run**:

```bash
# Set active project
gcloud config set project YOUR_PROJECT_ID

# Enable requisite Google Cloud APIs
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  aiplatform.googleapis.com \
  secretmanager.googleapis.com

# Deploy API service from root context
gcloud run deploy syncagent \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

> For step-by-step secret wiring via Secret Manager, custom domain configuration, and Firebase deployment, refer to [docs/deployment.md](docs/deployment.md).

---

## ⚖️ Scope & Legal Boundaries

* **In Scope:** Natural-language scene parsing, musical attribute extraction, multi-dimensional score calculation, deterministic licensing boundary validation (territory, budget, commercial use, sync status), exportable audit reports.
* **Out of Scope:** Direct automated copyright owner tracking, PRO/CMO negotiation pipelines, legal contract compilation, audio generation, and audio fingerprinting.