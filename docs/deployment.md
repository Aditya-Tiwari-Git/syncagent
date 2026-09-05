# Google Cloud Run Deployment

SyncAgent runs as a FastAPI container on Cloud Run. Vertex AI is accessed through the Cloud Run service identity and ClickHouse remains an external managed catalog.

## Required APIs

```powershell
gcloud auth login
gcloud config set project PROJECT_ID
gcloud services enable run.googleapis.com cloudbuild.googleapis.com aiplatform.googleapis.com artifactregistry.googleapis.com
```

The Cloud Run runtime service account needs the least-privilege `roles/aiplatform.user` role on the project. Do not commit service-account JSON keys. Cloud Run provides Application Default Credentials through its service identity.

## Source deployment

From the repository root:

```powershell
gcloud run deploy syncagent --source . --region us-central1
```

Set runtime configuration through the Cloud Run console, `--set-env-vars`, or Secret Manager. Required values are listed in `.env.example`. For production, store ClickHouse password in Secret Manager and attach it as a Cloud Run secret instead of passing it as plain deployment metadata.

The included `deploy.sh` validates the minimum variables and wraps source deployment. It does not make the service public unless you explicitly add the relevant Cloud Run flag.

## Container deployment

```powershell
docker build -t syncagent .
docker run --rm -p 8080:8080 --env-file .env -e PORT=8080 syncagent
```

Cloud Run supplies `PORT`; the Dockerfile binds Uvicorn to `0.0.0.0`.

## Private versus public access

Private service:

```powershell
gcloud run deploy syncagent --source . --region us-central1 --no-allow-unauthenticated
```

Public service for a demo:

```powershell
gcloud run deploy syncagent --source . --region us-central1 --allow-unauthenticated
```

Public access means anyone with the URL can call the API. Keep credentials server-side, add authentication/rate limiting before real production use, and never put ClickHouse or Vertex credentials in frontend variables. Remove public access with `--no-allow-unauthenticated` or the Cloud Run IAM console.

## Verification

```powershell
$url = gcloud run services describe syncagent --region us-central1 --format='value(status.url)'
Invoke-RestMethod "$url/health"
```

Cloud Run, Vertex AI, ClickHouse, and model usage can each incur charges. PDF generation is local application work, but it still consumes Cloud Run CPU time.
