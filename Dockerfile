# Stage 1: Build the frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Setup the backend
FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

ENV PYTHONUNBUFFERED=True
ENV PORT=8080

WORKDIR /app

# Copy backend dependencies
COPY backend/pyproject.toml backend/uv.lock ./

# Install dependencies
RUN uv pip install --system --no-cache -r pyproject.toml

# Copy backend code
COPY backend/ ./

# Copy built frontend assets to static directory
COPY --from=frontend-builder /app/frontend/dist ./static

# Run the application
CMD exec uvicorn main:app --host 0.0.0.0 --port $PORT