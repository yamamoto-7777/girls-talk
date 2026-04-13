output "api_endpoint" {
  description = "API GatewayのエンドポイントURL"
  value       = "https://${aws_api_gateway_rest_api.main.id}.execute-api.${data.aws_region.current.name}.amazonaws.com/${var.environment}"
}

output "api_id" {
  description = "REST API ID"
  value       = aws_api_gateway_rest_api.main.id
}
