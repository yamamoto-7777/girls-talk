variable "project_name" {
  description = "プロジェクト名"
  type        = string
}

variable "environment" {
  description = "環境名"
  type        = string
}

variable "lambda_invoke_arn" {
  description = "LambdaのInvoke ARN"
  type        = string
}

variable "lambda_function_name" {
  description = "Lambda関数名"
  type        = string
}
