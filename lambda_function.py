# lambda_function.py
import os
import json
from datetime import datetime, timezone

GIT_COMMIT_SHA = os.environ.get("GIT_COMMIT_SHA", "unknown")


def lambda_handler(event, context):
    log_json = {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Hello from Lambda!",
            "commit_sha": GIT_COMMIT_SHA,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    }

    print("Lambda function invoked. Response:")
    print(log_json)
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Hello from Lambda!",
            "commit_sha": GIT_COMMIT_SHA,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    }