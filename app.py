import os
from fastapi import FastAPI
from datetime import datetime, timezone

app = FastAPI(title="Hello World API", version="1.0.0")

# Injected at Docker build time via ARG → ENV in Dockerfile
GIT_COMMIT_SHA = os.environ.get("GIT_COMMIT_SHA", "unknown")
print(f"GIT Commit SHA: {GIT_COMMIT_SHA}")
APP_ENV = os.environ.get("APP_ENV", "production")


@app.get("/")
def root():
    """Basic hello world endpoint."""
    return {
        "message": "Hello, World!!",
        "env": APP_ENV,
        "commit_sha": GIT_COMMIT_SHA,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/health")
def health():
    """
    ECS health check endpoint.
    ECS and ALB target groups call this to determine if the container is healthy.
    Must return HTTP 200 for the container to be marked as healthy.
    """
    return {
        "status": "healthy",
        "commit_sha": GIT_COMMIT_SHA,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/info")
def info():
    """Returns deployment info — useful for verifying which build is running."""
    return {
        "app": "hello-world-api",
        "version": "1.0.0",
        "commit_sha": GIT_COMMIT_SHA,
        "env": APP_ENV,
        "python_version": os.popen("python3 --version").read().strip(),
        "hostname": os.uname().nodename,  # Shows the ECS container ID
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
