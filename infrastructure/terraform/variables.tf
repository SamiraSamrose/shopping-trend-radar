# infrastructure/terraform/variables.tf

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "s3_bucket_name" {
  description = "S3 bucket name for data storage"
  type        = string
  default     = "shopping-trend-radar-data"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "app_version" {
  description = "Application version"
  type        = string
  default     = "1.0.0"
}
