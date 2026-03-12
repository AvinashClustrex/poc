# Hello World API — CI/CD POC

A minimal FastAPI app for testing the GHES → CodePipeline → ECR → ECS pipeline.

## Project Structure

```
hello-api/
├── app.py                    # FastAPI application
├── requirements.txt          # Python dependencies
├── Dockerfile                # Multi-stage Docker build
├── buildspec.yml             # CodeBuild instructions
├── ecs-task-definition.json  # ECS Task Definition (register before first deploy)
└── README.md
```

## API Endpoints

| Endpoint  | Purpose                                              |
|-----------|------------------------------------------------------|
| GET /     | Hello World — returns message, commit SHA, timestamp |
| GET /health | ECS/ALB health check — must return 200             |
| GET /info | Full deployment info — env, SHA, hostname            |

## Before You Push to GHES

1. Replace placeholder values in `buildspec.yml`:
   - `AWS_DEFAULT_REGION` — your AWS region
   - `AWS_ACCOUNT_ID` — your 12-digit AWS account ID
   - `ECR_REPO_NAME` — your ECR repository name
   - `CONTAINER_NAME` — must match `name` in `ecs-task-definition.json`

2. Replace placeholder values in `ecs-task-definition.json`:
   - `123456789012` — your AWS account ID
   - `ap-southeast-1` — your region

## Register the Task Definition (one-time, before first pipeline run)

```bash
aws ecs register-task-definition \
  --cli-input-json file://ecs-task-definition.json \
  --region ap-southeast-1
```

## Create the ECS Service (one-time)

```bash
aws ecs create-service \
  --cluster your-ecs-cluster \
  --service-name hello-world-api \
  --task-definition hello-world-api \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxxx],securityGroups=[sg-xxxx],assignPublicIp=ENABLED}" \
  --region ap-southeast-1
```

## Test Locally (optional, before pushing)

```bash
# Build locally
docker build --build-arg GIT_COMMIT_SHA=local-test -t hello-world-api .

# Run locally
docker run -p 8000:8000 hello-world-api

# Test endpoints
curl http://localhost:8000/
curl http://localhost:8000/health
curl http://localhost:8000/info
```

## Verifying the Pipeline Worked

After a merge to prod triggers the pipeline and ECS deploys:

```bash
# Call the info endpoint — commit_sha should match your merged commit
curl http://<your-alb-or-task-ip>:8000/info

# Expected response:
# {
#   "app": "hello-world-api",
#   "commit_sha": "a1b2c3d4...",   <-- matches your git commit
#   "env": "production",
#   "hostname": "ip-10-0-1-23"     <-- ECS container hostname
# }
```
