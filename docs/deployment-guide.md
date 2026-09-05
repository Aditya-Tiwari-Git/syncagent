# SyncAgent Deployment Guide

This guide documents the verified deployment of SyncAgent's FastAPI backend to Google Cloud Run and the exact steps to publish the Vite frontend publicly with Firebase Hosting.

## 1. Deployed Architecture

```text
Public browser
    |
    v
Firebase Hosting (React/Vite frontend)
    |
    v
Cloud Run HTTPS API (FastAPI)
    |
    +--> Vertex AI / Gemini through Cloud Run service identity
    |
    +--> ClickHouse Cloud through Secret Manager credentials
    |
    +--> ReportLab PDF generation
```

The API is currently public through Cloud Run `allUsers` invoker access. The frontend contains only the public API URL; no credentials are shipped to the browser.

## 2. Google Cloud Values

```powershell
$PROJECT_ID = "syncagent-506417"
$REGION = "us-central1"
$API_SERVICE = "syncagent"
$RUNTIME_SERVICE_ACCOUNT = "syncagent-runtime@$PROJECT_ID.iam.gserviceaccount.com"
$API_URL = "https://syncagent-358847195192.us-central1.run.app"
```

Do not put passwords, API keys, service-account JSON files, or access tokens in source control or frontend files.

## 3. API Deployment Summary

The backend was deployed with:

- Python 3.11 slim container.
- FastAPI served by Uvicorn on `0.0.0.0:$PORT`.
- Google ADK and Gemini through Vertex AI.
- Cloud Run runtime service account: `syncagent-runtime`.
- Vertex role: `roles/aiplatform.user`.
- ClickHouse password injected from Secret Manager.
- ClickHouse MCP disabled for the fast API path.
- `SYNCAGENT_API_MODE=fast` enabled.

The fast API path makes one Gemini scene-analysis call, then performs catalog search, rights validation, and ranking deterministically. The full ADK runner remains available through `backend/agent_runner.py`.

## 4. Required APIs

These APIs are enabled for the project:

```powershell
gcloud services enable `
  run.googleapis.com `
  cloudbuild.googleapis.com `
  artifactregistry.googleapis.com `
  aiplatform.googleapis.com `
  secretmanager.googleapis.com `
  iamcredentials.googleapis.com `
  --project=$PROJECT_ID
```

## 5. Runtime Identity

The Cloud Run service uses:

```text
syncagent-runtime@syncagent-506417.iam.gserviceaccount.com
```

Required IAM:

```text
roles/aiplatform.user
roles/secretmanager.secretAccessor on syncagent-clickhouse-password
```

No service-account JSON key is needed. Cloud Run uses its service identity and Application Default Credentials.

## 6. Secret Manager

The ClickHouse password is stored as:

```text
syncagent-clickhouse-password
```

Check metadata without revealing the value:

```powershell
gcloud secrets describe syncagent-clickhouse-password `
  --project=$PROJECT_ID
```

List versions without printing secret contents:

```powershell
gcloud secrets versions list syncagent-clickhouse-password `
  --project=$PROJECT_ID
```

## 7. Deploy Or Update the API

Use a temporary environment YAML file. It contains no password:

```powershell
$CLICKHOUSE_HOST = ((Get-Content .env | Where-Object { $_ -match '^CLICKHOUSE_HOST=' }) -replace '^CLICKHOUSE_HOST=', '')
$CLICKHOUSE_USER = ((Get-Content .env | Where-Object { $_ -match '^CLICKHOUSE_USER=' }) -replace '^CLICKHOUSE_USER=', '')
$ENV_FILE = Join-Path $env:TEMP "syncagent-cloudrun-env.yaml"

@"
GOOGLE_CLOUD_PROJECT: "$PROJECT_ID"
GOOGLE_CLOUD_LOCATION: "us-central1"
GOOGLE_GENAI_USE_VERTEXAI: "TRUE"
CLICKHOUSE_HOST: "$CLICKHOUSE_HOST"
CLICKHOUSE_PORT: "8443"
CLICKHOUSE_DATABASE: "default"
CLICKHOUSE_USER: "$CLICKHOUSE_USER"
CORS_ORIGINS: "https://YOUR-FRONTEND-DOMAIN.web.app"
CLICKHOUSE_MCP_ENABLED: "false"
SYNCAGENT_API_MODE: "fast"
"@ | Set-Content -Path $ENV_FILE -Encoding utf8
```

Deploy:

```powershell
gcloud run deploy $API_SERVICE `
  --source . `
  --project=$PROJECT_ID `
  --region=$REGION `
  --service-account=$RUNTIME_SERVICE_ACCOUNT `
  --env-vars-file=$ENV_FILE `
  --set-secrets="CLICKHOUSE_PASSWORD=syncagent-clickhouse-password:latest"

Remove-Item $ENV_FILE -Force
```

For local frontend development, use both localhost origins instead:

```text
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

## 8. Make the API Public

Public Cloud Run access is configured with:

```powershell
gcloud run services add-iam-policy-binding $API_SERVICE `
  --project=$PROJECT_ID `
  --region=$REGION `
  --member="allUsers" `
  --role="roles/run.invoker"
```

Verify:

```powershell
gcloud run services get-iam-policy $API_SERVICE `
  --project=$PROJECT_ID `
  --region=$REGION
```

Public access means anyone can submit requests and cause Vertex AI, ClickHouse, Cloud Run, and PDF work. Add authentication and rate limiting before exposing this to an uncontrolled production audience.

## 9. Deploy the Frontend Publicly

The frontend is a Vite React application. Firebase Hosting is the simplest static hosting option because the built files are static and it does not require a second always-running server.

### Install Firebase CLI

```powershell
npm install --global firebase-tools
firebase --version
firebase login
```

### Build against the public API

From the repository root:

```powershell
Set-Location frontend
$env:VITE_BACKEND_URL = "https://syncagent-358847195192.us-central1.run.app"
npm ci
npm run build
```

The API URL is compiled into the frontend bundle. It is public by design; it is not a secret.

### Select the Firebase project

```powershell
firebase use --add syncagent-506417
```

Choose the project when prompted. This creates a local `.firebaserc` file. It is safe to commit because it contains only the project identifier, not credentials.

### Publish

```powershell
firebase deploy --only hosting
```

Firebase will print a public URL similar to:

```text
https://syncagent-506417.web.app
https://syncagent-506417.firebaseapp.com
```

Use the actual URL printed by Firebase in the Cloud Run CORS configuration.

## 10. Configure Production CORS

After receiving the Firebase URL:

```powershell
$FRONTEND_URL = "https://syncagent-506417.web.app"

$ENV_FILE = Join-Path $env:TEMP "syncagent-cloudrun-env.yaml"
@"
GOOGLE_CLOUD_PROJECT: "$PROJECT_ID"
GOOGLE_CLOUD_LOCATION: "us-central1"
GOOGLE_GENAI_USE_VERTEXAI: "TRUE"
CLICKHOUSE_HOST: "$CLICKHOUSE_HOST"
CLICKHOUSE_PORT: "8443"
CLICKHOUSE_DATABASE: "default"
CLICKHOUSE_USER: "$CLICKHOUSE_USER"
CORS_ORIGINS: "$FRONTEND_URL"
CLICKHOUSE_MCP_ENABLED: "false"
SYNCAGENT_API_MODE: "fast"
"@ | Set-Content -Path $ENV_FILE -Encoding utf8

gcloud run services update $API_SERVICE `
  --project=$PROJECT_ID `
  --region=$REGION `
  --env-vars-file=$ENV_FILE `
  --update-secrets="CLICKHOUSE_PASSWORD=syncagent-clickhouse-password:latest"

Remove-Item $ENV_FILE -Force
```

Keep localhost in the list only if local frontend development still needs to call the deployed API:

```text
CORS_ORIGINS=https://syncagent-506417.web.app,http://localhost:5173,http://127.0.0.1:5173
```

## 11. Verify the Public System

API root:

```powershell
Invoke-RestMethod "$API_URL/"
Invoke-RestMethod "$API_URL/health"
```

Analyze request:

```powershell
$BODY = @{
  scene_description = "An exhausted detective walks through an empty Mumbai street at 2 AM after failing to solve a case."
  budget = 800
  territory = "Worldwide"
  top_k = 5
} | ConvertTo-Json

Invoke-RestMethod "$API_URL/api/analyze" `
  -Method Post `
  -ContentType "application/json" `
  -Body $BODY
```

PDF:

```powershell
Invoke-WebRequest "$API_URL/api/report" `
  -Method Post `
  -ContentType "application/json" `
  -Body $BODY `
  -OutFile syncagent-report.pdf
```

Frontend verification:

1. Open the Firebase Hosting URL.
2. Enter a scene and budget.
3. Click Analyze Scene.
4. Confirm scene analysis, recommendations, and rejected tracks appear.
5. Click Download report.
6. Confirm a PDF downloads.

## 12. Stop Cloud Run Costs When Not Needed

Cloud Run normally scales to zero when idle, so an idle service generally does not consume request compute. Cloud Build, Artifact Registry storage, Vertex AI usage, ClickHouse, and logs may still incur charges.

### Immediate pause: remove public access

This keeps the service deployed but blocks anonymous requests:

```powershell
gcloud run services remove-iam-policy-binding $API_SERVICE `
  --project=$PROJECT_ID `
  --region=$REGION `
  --member="allUsers" `
  --role="roles/run.invoker"
```

Authenticated callers can still access it if they have permission.

### Full stop: delete the Cloud Run service

This stops the API service and removes its revisions:

```powershell
gcloud run services delete $API_SERVICE `
  --project=$PROJECT_ID `
  --region=$REGION
```

The source code, Secret Manager secret, Artifact Registry images, and Firebase Hosting site are separate resources. Delete them only if you intentionally want to remove them.

Restore later with:

```powershell
gcloud run deploy $API_SERVICE `
  --source . `
  --project=$PROJECT_ID `
  --region=$REGION `
  --service-account=$RUNTIME_SERVICE_ACCOUNT `
  --env-vars-file=$ENV_FILE `
  --set-secrets="CLICKHOUSE_PASSWORD=syncagent-clickhouse-password:latest"
```

### Stop frontend hosting

Firebase Hosting has no running VM to stop. To remove the hosted site:

```powershell
firebase hosting:disable
```

This is destructive for the hosted site but does not delete your local frontend code.

### Check active Cloud Run services

```powershell
gcloud run services list --project=$PROJECT_ID --region=$REGION
```

### Check billing reports

Use Google Cloud Console:

```text
Billing -> Reports
Billing -> Cost table
Billing -> Budgets & alerts
```

Filter by project `syncagent-506417`, service, and date range. Vertex AI model usage is billed to the configured Google Cloud project when using Vertex AI credentials.

## 13. Rollback

List revisions:

```powershell
gcloud run revisions list `
  --service=$API_SERVICE `
  --project=$PROJECT_ID `
  --region=$REGION
```

Route traffic to a previous revision:

```powershell
gcloud run services update-traffic $API_SERVICE `
  --project=$PROJECT_ID `
  --region=$REGION `
  --to-revisions=REVISION_NAME=100
```

## 14. Security Checklist

- Never commit `.env`.
- Never put ClickHouse passwords in frontend environment variables.
- Never put service-account JSON files in the repository.
- Keep `GOOGLE_API_KEY` out of Vertex AI production configuration.
- Store ClickHouse credentials in Secret Manager.
- Use a dedicated Cloud Run service account.
- Restrict CORS to the real frontend origin.
- Add authentication/rate limiting before broad public use.
- Rotate credentials that have been exposed.
