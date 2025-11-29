# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.13-slim

# Copy uv from the official image for fast dependency installation
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME

# Copy dependency definitions
COPY pyproject.toml uv.lock* ./

# Install production dependencies using uv.
# We use --system to install into the container's system python.
RUN uv pip install --system --no-cache -r pyproject.toml

# Copy the rest of the application code
COPY . ./

# Run the web service on container startup using gunicorn
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app