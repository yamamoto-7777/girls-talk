output "lambda_invoke_arn" {
  description = "LambdaのInvoke ARN（API Gateway統合用）"
  value       = aws_lambda_function.chat_handler.invoke_arn
}

output "lambda_function_name" {
  description = "Lambda関数名"
  value       = aws_lambda_function.chat_handler.function_name
}

output "lambda_function_arn" {
  description = "Lambda関数のARN"
  value       = aws_lambda_function.chat_handler.arn
}

output "seed_lambda_function_name" {
  description = "seed Lambda関数名"
  value       = aws_lambda_function.seed_handler.function_name
}

output "seed_lambda_function_arn" {
  description = "seed Lambda関数のARN"
  value       = aws_lambda_function.seed_handler.arn
}

