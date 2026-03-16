# ─────────────────────────────────────────────
# Stage 1: Build dependencies
# ─────────────────────────────────────────────
FROM public.ecr.aws/docker/library/python:3.12-slim AS builder

WORKDIR /app

# Install dependencies into a separate location so they can be copied cleanly
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ─────────────────────────────────────────────
# Stage 2: Runtime image
# ─────────────────────────────────────────────
FROM public.ecr.aws/docker/library/python:3.12-slim AS runtime

# Non-root user — ECS best practice; avoids running as root inside container
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY app.py .

# ── Git Commit SHA ──────────────────────────
# Passed in by buildspec.yml as a Docker build arg:
#   docker build --build-arg GIT_COMMIT_SHA=$COMMIT_SHA
# Falls back to "unknown" if built locally without the arg.
ARG GIT_COMMIT_SHA=unknown
ENV GIT_COMMIT_SHA=${GIT_COMMIT_SHA}

# ── App environment ─────────────────────────
# Override via ECS Task Definition environment variables if needed
ENV APP_ENV=production

# ── Runtime config ───────────────────────────
# Unbuffered output ensures logs appear immediately in CloudWatch
ENV PYTHONUNBUFFERED=1

# Switch to non-root user
USER appuser

# ECS will map this port via the Task Definition portMappings
EXPOSE 8000

# Start the API server
# - host 0.0.0.0 required so ECS can route traffic to the container
# - workers=1 is correct for Fargate (scale via ECS service desired count, not workers)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
