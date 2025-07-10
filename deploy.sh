#!/bin/bash
set -e

# Load env vars from .env.deploy
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
else
  echo ".env not found. Aborting."
  exit 1
fi

echo "Building Docker image and submitting to Cloud Build..."
gcloud builds submit \
  --tag "gcr.io/${GCP_PROJECT_ID}/${SERVICE_NAME}" \
  --project="${GCP_PROJECT_ID}"

echo "Deploying to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
  --image "gcr.io/${GCP_PROJECT_ID}/${SERVICE_NAME}" \
  --platform managed \
  --region "${REGION}" \
  --allow-unauthenticated \
  --service-account="${SERVICE_ACCOUNT}" \
  --set-env-vars="GCP_PROJECT_ID=${GCP_PROJECT_ID},GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID},GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}"

echo "✅ Deployment complete."


