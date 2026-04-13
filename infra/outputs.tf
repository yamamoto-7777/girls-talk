output "api_gateway_endpoint" {
  description = "API GatewayのエンドポイントURL（/chatまで）"
  value       = "${module.api_gateway.api_endpoint}/chat"
}

output "lambda_function_name" {
  description = "Lambda関数名"
  value       = module.lambda.lambda_function_name
}

