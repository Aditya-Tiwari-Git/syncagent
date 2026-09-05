# SyncAgent Product Overview

## What Is SyncAgent?

SyncAgent is an AI-powered music pre-clearance assistant for filmmakers.

It helps a filmmaker answer an early post-production question:

> Which music tracks fit this scene creatively and satisfy the configured licensing constraints?

SyncAgent is not a legal clearance system. It evaluates catalog metadata and configured rights rules. Final licensing must be verified with the relevant rights holder.

## The Problem

Filmmakers often use temporary music while editing. A track may fit perfectly but later fail because it is over budget, unavailable in a territory, missing sync rights, or unavailable for commercial use.

SyncAgent surfaces those problems while the film is still being edited.

## What The User Does

1. Describes a film scene.
2. Enters a licensing budget.
3. Selects a territory.
4. Selects how many recommendations to display.
5. Runs the analysis.
6. Reviews scene analysis, recommendations, rejected candidates, and reasons.
7. Downloads a PDF pre-clearance report.

## What The System Does

```text
Scene description
      |
      v
Gemini scene understanding
      |
      v
Structured mood, tempo, energy, genre, instrumentation
      |
      v
ClickHouse catalog search
      |
      v
Deterministic rights validation
      |
      v
Creative compatibility ranking
      |
      v
Recommendations + rejected candidates + PDF report
```

## Technology

- **Frontend:** React, TypeScript, Vite, Tailwind CSS, Lucide icons.
- **API:** Python, FastAPI, Pydantic.
- **Agent:** Google ADK root agent with Gemini through Vertex AI.
- **Fast API mode:** One Gemini scene-analysis call followed by deterministic catalog processing.
- **Catalog:** ClickHouse Cloud.
- **Rules:** Python rights validation for budget, territory, sync, and commercial usage.
- **Reports:** ReportLab PDF generation.
- **Hosting:** Firebase Hosting for the frontend and Google Cloud Run for the API.
- **Secrets:** Google Secret Manager for the ClickHouse password.

## Agentic Design

The full ADK supervisor can analyze a scene, call catalog tools, validate rights, rank candidates, and format a response. For normal HTTP requests, the API uses a faster controlled path:

- Gemini understands unstructured creative intent.
- Python owns licensing decisions.
- ClickHouse owns catalog truth.
- Python owns final score calculation.
- The API returns only deterministic catalog-backed results.

This reduces model calls, cost, and latency while preserving the full ADK runner for demonstrations and experimentation.

## Catalog And Rights Model

Each track contains:

- Track ID
- Title
- Artist
- Genre
- Mood
- BPM
- Energy
- Duration
- Instrumentation
- Sync availability
- Commercial-use availability
- Territory
- License price
- License type

A candidate appears in recommendations only after it passes the configured rights checks. A high creative score does not override a failed licensing check.

Possible rejection reasons include:

- Sync rights unavailable.
- Commercial use unavailable.
- License price exceeds the budget.
- Requested territory unavailable.

## Ranking

The creative score considers:

- Mood
- BPM
- Genre
- Energy
- Instrumentation
- Duration

The score is transparent and bounded from 0 to 100. Rights validation is separate from creative ranking. A track can be creatively strong and still be rejected.

## User-Facing Safety Language

SyncAgent must never say:

- Legally cleared
- Copyright safe
- Rights guaranteed
- Guaranteed clearance

The application uses wording such as:

> The catalog indicates that this candidate passes the configured pre-clearance checks.

And always includes:

> Final licensing must be verified with the relevant rights holder.

## No-Match Behavior

When no track passes the configured constraints, SyncAgent does not fabricate a recommendation. It shows rejected candidates and explains whether the likely constraint was budget, territory, sync rights, commercial usage, or creative fit.

## Public Product URLs

API:

```text
https://syncagent-358847195192.us-central1.run.app
```

Frontend:

```text
Firebase Hosting URL printed by `firebase deploy --only hosting`
```

The frontend calls the API using the build-time `VITE_BACKEND_URL` value.

## Demo Story

Use the detective scenario:

> An exhausted detective walks through an empty Mumbai street at 2 AM after failing to solve a case.

Set:

- Budget: `$800`
- Territory: `Worldwide`
- Top tracks: `5`

Show:

1. Gemini extracts the scene’s emotional and musical profile.
2. ClickHouse returns candidate tracks.
3. Rights rules reject incompatible candidates.
4. Passing tracks are ranked transparently.
5. The user downloads the pre-clearance report.

Then demonstrate the no-match case with a `$50` budget.

## Limitations

- Catalog rights are only as accurate as the catalog data.
- The system does not discover copyright owners.
- It does not negotiate licenses or generate contracts.
- It does not guarantee exclusivity or legal clearance.
- Public API access should be protected with authentication and rate limiting before uncontrolled production use.

## Future Improvements

- User authentication and projects.
- Per-user request quotas.
- Persistent report history.
- Video scene input.
- Secret Manager references for all deployment configuration.
- Cloud Monitoring alerts and dashboards.
- More advanced catalog semantic search.
