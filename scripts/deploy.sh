#!/bin/bash
# scripts/deploy.sh
# Deployment script for Shopping Trend Radar Agent

set -e

echo "🚀 Deploying Shopping Trend Radar Agent..."

# Variables
AWS_REGION=${AWS_REGION:-us-east-1}
ECR_REPOSITORY="shopping-trend-radar"
ECS_CLUSTER="trend-radar-cluster"
ECS_SERVICE="trend-radar-service"

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Build Docker image
echo "🔨 Building Docker image..."
docker build -t ${ECR_REPOSITORY}:latest -f backend/Dockerfile backend/

# Tag for ECR
echo "🏷️  Tagging image..."
docker tag ${ECR_REPOSITORY}:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY}:latest

# Login to ECR
echo "🔐 Logging in to ECR..."
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# Push to ECR
echo "📤 Pushing image to ECR..."
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY}:latest

# Update ECS service
echo "🔄 Updating ECS service..."
aws ecs update-service \
    --cluster ${ECS_CLUSTER} \
    --service ${ECS_SERVICE} \
    --force-new-deployment \
    --region ${AWS_REGION}

# Deploy Lambda functions
echo "☁️  Deploying Lambda functions..."
cd backend/lambda_functions

# Dashboard Generator
zip -r dashboard_generator.zip dashboard_generator.py
aws lambda update-function-code \
    --function-name trend-radar-dashboard-generator \
    --zip-file fileb://dashboard_generator.zip \
    --region ${AWS_REGION}

# Trend Analyzer
zip -r trend_analyzer.zip trend_analyzer.py
aws lambda update-function-code \
    --function-name trend-radar-analyzer \
    --zip-file fileb://trend_analyzer.zip \
    --region ${AWS_REGION}

# Alert Notifier
zip -r alert_notifier.zip alert_notifier.py
aws lambda update-function-code \
    --function-name trend-radar-alert-notifier \
    --zip-file fileb://alert_notifier.zip \
    --region ${AWS_REGION}

cd ../..

echo "✅ Deployment complete!"
echo "Monitor deployment: aws ecs describe-services --cluster ${ECS_CLUSTER} --services ${ECS_SERVICE}"
