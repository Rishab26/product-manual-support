# product-manual-support

Aim is to generate product manuals.


## Devops



#### docker run

docker build -t product-manual-support .
docker run -p 8080:8080 -e PORT=8080 product-manual-support

#### deploy

gcloud run deploy product-manual-support \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \

## or build and then deploy

gcloud builds submit --tag us-central1-docker.pkg.dev/product-manual-support/product-manual-repo/product-manual-support:latest .

gcloud run deploy product-manual-support \
  --image us-central1-docker.pkg.dev/product-manual-support/product-manual-repo/product-manual-support:latest \
  --region us-central1 \
  --allow-unauthenticated
