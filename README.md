# product-manual-support

Aim is to generate product manuals.


## Local Development

### Backend

```bash
cd backend
uv sync

# Run server
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Devops

#### docker run

```bash
docker build -t product-manual-support .
docker run -p 8080:8080 -e PORT=8080 product-manual-support
```

#### deploy

```bash
gcloud run deploy product-manual-support \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

## or build and then deploy

```bash
gcloud builds submit --tag us-central1-docker.pkg.dev/product-manual-support/product-manual-repo/product-manual-support:latest .

gcloud run deploy product-manual-support \
  --image us-central1-docker.pkg.dev/product-manual-support/product-manual-repo/product-manual-support:latest \
  --region us-central1 \
  --allow-unauthenticated
```
