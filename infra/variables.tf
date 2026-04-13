variable "aws_region" {
  description = "AWSリージョン"
  type        = string
  default     = "ap-northeast-1"
}

variable "project_name" {
  description = "プロジェクト名（リソース名のプレフィックス）"
  type        = string
  default     = "girls-talk"
}

variable "environment" {
  description = "環境名（prod, staging, dev）"
  type        = string
  default     = "dev"
}
