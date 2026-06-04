#!/usr/bin/env bash
# Deploy LifeAgent to AWS ECS + Fargate
# Usage: ./infra/deploy.sh <aws-region> <aws-account-id>
set -euo pipefail

REGION="${1:-eu-west-2}"
ACCOUNT_ID="${2?Must supply AWS account ID}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
ECR_REPO="$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/lifeagent"

echo "==> Logging in to ECR"
aws ecr get-login-password --region "$REGION" | \
  docker login --username AWS --password-stdin "$ECR_REPO"

echo "==> Building image"
docker build -t lifeagent:$IMAGE_TAG .

echo "==> Tagging and pushing"
docker tag lifeagent:$IMAGE_TAG "$ECR_REPO:$IMAGE_TAG"
docker push "$ECR_REPO:$IMAGE_TAG"

echo "==> Registering task definition"
sed "s/ACCOUNT_ID/$ACCOUNT_ID/g; s/REGION/$REGION/g" \
  infra/ecs-task-definition.json > /tmp/ecs-task.json
aws ecs register-task-definition --cli-input-json file:///tmp/ecs-task.json \
  --region "$REGION"

echo "==> Updating ECS service"
aws ecs update-service \
  --cluster lifeagent-cluster \
  --service lifeagent-service \
  --force-new-deployment \
  --region "$REGION"

echo "==> Done. Deployment triggered."
