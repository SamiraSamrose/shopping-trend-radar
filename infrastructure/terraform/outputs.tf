# infrastructure/terraform/outputs.tf

output "ecr_repository_url" {
  description = "ECR repository URL"
  value       = aws_ecr_repository.app.repository_url
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = aws_ecs_cluster.main.name
}

output "s3_bucket_name" {
  description = "S3 bucket name"
  value       = aws_s3_bucket.data.bucket
}

output "lambda_dashboard_arn" {
  description = "Dashboard generator Lambda ARN"
  value       = aws_lambda_function.dashboard_generator.arn
}

output "lambda_analyzer_arn" {
  description = "Trend analyzer Lambda ARN"
  value       = aws_lambda_function.trend_analyzer.arn
}

output "dynamodb_products_table" {
  description = "DynamoDB products table name"
  value       = aws_dynamodb_table.products.name
}

output "dynamodb_alerts_table" {
  description = "DynamoDB alerts table name"
  value       = aws_dynamodb_table.alerts.name
}
