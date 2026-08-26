# SyncAgent

SyncAgent is a Google ADK agent that helps filmmakers find music candidates that fit a scene while satisfying configured pre-clearance checks for budget, territory, sync rights, and commercial use.

It is a pre-clearance workflow assistant, not a legal clearance system. Final licensing must be verified with the relevant rights holder.

## Workflow

```text
Filmmaker scene description
        |
        v
Gemini scene analysis -> structured requirements
        |
        v
ClickHouse catalog search
        |
        v
Deterministic rights validation
        |
        v
Transparent creative ranking
        |
        v
Recommendations and rejection explanations
```

Gemini handles scene understanding. ClickHouse provides catalog search. Python tools apply deterministic rights rules. Google ADK orchestrates the workflow.

## Project Structure

```text
syncagent/
|-- backend/
|   |-- agent_runner.py       # Local ADK Runner entry point
|   |-- agents/root_agent.py  # Root Google ADK Agent
|   |-- tools/                # ADK-callable scene, search, rights, ranking tools
|   |-- models/               # Pydantic schemas
|   `-- services/             # Gemini, ClickHouse, matching, and rights logic
|-- database/                 # ClickHouse schema and demo catalog scripts
|-- tests/                    # Automated tests
|-- archive/legacy/           # Retained non-ADK scripts from earlier iterations
|-- .env.example              # Configuration template
|-- requirements.txt          # Runtime dependencies
`-- requirements-dev.txt      # Runtime plus test dependencies
```

## Setup

Requirements: Python 3.11+, Google Cloud credentials, a ClickHouse catalog, and access to Gemini through Vertex AI.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Set these values in `.env`:

```text
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
CLICKHOUSE_HOST=your-clickhouse-host
CLICKHOUSE_USER=your-clickhouse-user
CLICKHOUSE_PASSWORD=your-clickhouse-password
```

Authenticate locally with Google Cloud before running the agent, for example with Application Default Credentials. Never commit `.env` or credentials.

## Run The Agent

The supported local entry point is:

```powershell
python -m backend.agent_runner
```

The runner creates an in-memory ADK session, invokes `root_agent`, and prints the final response. The sample prompt in `backend/agent_runner.py` demonstrates the intended workflow.

For ADK development tools, you can also use the ADK CLI from the repository root when installed:

```powershell
adk web backend
```

## Agent Contract

The root agent must:

1. Analyze the scene before recommending music.
2. Search the approved catalog with the search tool.
3. Validate candidates with deterministic rights rules.
4. Rank candidates by creative compatibility.
5. Explain rejected candidates.
6. Never claim that a track is legally cleared.
7. State that final licensing requires rights-holder verification.

## Data And Rights

The catalog is demo data unless explicitly connected to a verified rights source. Passing the configured checks means only that the catalog record satisfies the configured pre-clearance rules. It does not establish ownership, exclusivity, or legal clearance.

## Tests

Install development dependencies and run the focused automated suite:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m compileall -q backend database tests
```

The database connectivity test is an integration check and requires valid ClickHouse credentials. The agent runner requires working Google Cloud and ClickHouse access.

## Configuration Notes

Configuration is loaded from `.env` in the repository root. The active code intentionally has no application logging layer; the agent output is printed by `agent_runner.py` and errors are raised to the caller.

## Scope

Included: text scene analysis, structured requirements, ClickHouse search, deterministic rights checks, creative ranking, rejection explanations, and ADK orchestration.

Deferred: legal contracting, rights-holder discovery, negotiations, full video upload processing, audio fingerprinting, and music generation.

## License

See [LICENSE](LICENSE).
