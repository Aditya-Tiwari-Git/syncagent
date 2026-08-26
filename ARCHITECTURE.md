# SyncAgent Architecture

## Runtime

`backend/agent_runner.py` is the supported local entry point. It creates an `InMemorySessionService`, constructs an ADK `Runner` with `root_agent`, sends a `Content` message, and prints the final event.

## Agent

`backend/agents/root_agent.py` defines the Google ADK `Agent`. Its instruction establishes the pre-clearance workflow and guardrails. The agent uses Gemini for reasoning and invokes four typed Python tools:

- `analyze_scene_tool`: converts scene text into `SceneRequirements`.
- `search_music_catalog_tool`: searches ClickHouse using the extracted BPM range.
- `validate_music_rights_tool`: applies deterministic sync, commercial-use, budget, and territory checks.
- `rank_music_candidates_tool`: calculates transparent creative match scores and explanations.

## Data Flow

```text
User message
  -> root_agent
  -> analyze_scene_tool
  -> search_music_catalog_tool
  -> validate_music_rights_tool
  -> rank_music_candidates_tool
  -> pre-clearance response
```

The agent is instructed to separate recommendations from rejected candidates and to explain failed checks. It must not present catalog results as legal clearance.

## Data Models

`SceneRequirements` validates mood, energy, BPM range, genre, instrumentation, pacing, and duration. `Track` represents a catalog record. `ValidatedTrack` stores deterministic rights results and rejection reasons. `TrackRecommendation` stores a ranked result and score breakdown.

## Service Boundaries

- `scene_analyzer.py`: Gemini structured-output request and Pydantic validation.
- `music_search.py`: parameterized ClickHouse BPM query and row conversion.
- `rights_validator.py`: deterministic catalog-policy checks.
- `matching.py`: component scores for mood, BPM, genre, energy, instrumentation, and duration.
- `recommendations.py`: thresholded ranking, alternatives, labels, and explanations.

The service modules are deliberately independent of the ADK runtime so they can be tested in isolation and reused by tools.

## Configuration

`backend/config.py` loads `.env` from the repository root. Required values are the Google Cloud project and location plus ClickHouse connection credentials. Secrets are excluded by `.gitignore`.

## Deployment Direction

The same root agent can be developed locally with the ADK CLI and deployed through a Google-managed Agent Runtime or a Cloud Run service. Keep ClickHouse credentials in Secret Manager for deployment. The local runner remains the simplest smoke test.

## Design Guardrail

This project performs automated pre-clearance assessment against catalog metadata. It does not verify copyright ownership, exclusivity, contract terms, or final legal rights.
