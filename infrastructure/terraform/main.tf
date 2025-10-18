# infrastructure/terraform/main.tf
# Terraform configuration for Shopping Trend Radar

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    bucket = "trend-radar-terraform-state"
    key    = "terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "trend-radar-vpc"
  }
}

# Subnets
resource "aws_subnet" "public_1" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "${var.aws_region}a"

  tags = {
    Name = "trend-radar-public-1"
  }
}

resource "aws_subnet" "public_2" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "${var.aws_region}b"

  tags = {
    Name = "trend-radar-public-2"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "trend-radar-igw"
  }
}

# Route Table
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "trend-radar-public-rt"
  }
}

# S3 Bucket
resource "aws_s3_bucket" "data" {
  bucket = var.s3_bucket_name

  tags = {
    Name = "trend-radar-data"
  }
}

# ECR Repository
resource "aws_ecr_repository" "app" {
  name                 = "shopping-trend-radar"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "trend-radar-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# Lambda Functions
resource "aws_lambda_function" "dashboard_generator" {
  filename      = "../lambda_functions/dashboard_generator.zip"
  function_name = "trend-radar-dashboard-generator"
  role          = aws_iam_role.lambda_role.arn
  handler       = "dashboard_generator.lambda_handler"
  runtime       = "python3.11"
  timeout       = 300

  environment {
    variables = {
      S3_BUCKET_NAME = var.s3_bucket_name
    }
  }
}

resource "aws_lambda_function" "trend_analyzer" {
  filename      = "../lambda_functions/trend_analyzer.zip"
  function_name = "trend-radar-analyzer"
  role          = aws_iam_role.lambda_role.arn
  handler       = "trend_analyzer.lambda_handler"
  runtime       = "python3.11"
  timeout       = 300
}

# IAM Role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "trend-radar-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# EventBridge Rule
resource "aws_cloudwatch_event_rule" "hourly_dashboard" {
  name                = "trend-radar-hourly-dashboard"
  schedule_expression = "rate(1 hour)"
}

resource "aws_cloudwatch_event_target" "dashboard_lambda" {
  rule      = aws_cloudwatch_event_rule.hourly_dashboard.name
  target_id = "DashboardGenerator"
  arn       = aws_lambda_function.dashboard_generator.arn
}

# DynamoDB Tables
resource "aws_dynamodb_table" "products" {
  name           = "TrendRadarProducts"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"

  attribute {
    name = "id"
    type = "S"
  }

  tags = {
    Name = "trend-radar-products"
  }
}

resource "aws_dynamodb_table" "alerts" {
  name           = "TrendRadarAlerts"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"

  attribute {
    name = "id"
    type = "S"
  }

  attribute {
    name = "user_id"
    type = "S"
  }

  global_secondary_index {
    name            = "UserIdIndex"
    hash_key        = "user_id"
    projection_type = "ALL"
  }

  tags = {
    Name = "trend-radar-alerts"
  }
}
