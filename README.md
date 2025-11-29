# product-manual-support

Aim is to generate product manuals.


## Devops



#### docker run

docker build -t product-manual-support .
docker run -p 8080:8080 -e PORT=8080 flask-app

#### deploy

gcloud run deploy product-manual-support \
  --source . \
  --region us-central1 \
  --allow-unauthenticated

## or build and then deploy

gcloud builds submit --tag us-central1-docker.pkg.dev/product-manual-support/flask-app-repo/flask-app:latest .

gcloud run deploy flask-app \
  --image us-central1-docker.pkg.dev/product-manual-support/flask-app-repo/flask-app:latest \
  --region us-central1 \
  --allow-unauthenticated
