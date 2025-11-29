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
