# SyncAgent Demo Script

## Setup

1. Start the backend: `uvicorn backend.api:app --reload`
2. Start the frontend: `cd frontend; npm install; npm run dev`
3. Open `http://localhost:5173`.

## Demo Story

Use this scene:

> An exhausted detective walks through an empty Mumbai street at 2 AM after failing to solve a case. It is raining and he feels isolated, exhausted, and hopeless.

Set budget to `$800`, territory to `Worldwide`, and top tracks to `5`.

Show the audience:

1. Gemini extracts mood, energy, tempo, genres, instrumentation, and pacing.
2. ClickHouse searches the approved catalog.
3. Deterministic Python checks reject over-budget, territory-incompatible, and unavailable-rights tracks.
4. Only passed candidates appear in recommendations.
5. Rejected candidates retain their creative score and exact configured reason.
6. The PDF report repeats the disclaimer and never claims legal clearance.

## No-Match Demo

Set the budget to `$50`. The UI should show a useful no-match state with rejected candidates and suggestions rather than inventing a recommendation.

## Judge Positioning

SyncAgent is an AI-powered music pre-clearance workflow assistant. Gemini understands creative intent, ClickHouse searches the catalog, Python validates configured rights rules, and ADK orchestrates the workflow. Final licensing must be verified with the relevant rights holder.
