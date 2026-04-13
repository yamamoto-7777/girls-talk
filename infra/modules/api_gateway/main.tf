# =============================================================================
# API Gateway: girls-talk REST API (v1)
# =============================================================================

data "aws_region" "current" {}

# ---------------------------------------------------------------------------
# REST API (v1)
# ---------------------------------------------------------------------------

resource "aws_api_gateway_rest_api" "main" {
  name        = "${var.project_name}-${var.environment}-api"
  description = "Girls Talk AI Chat API"

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

# ---------------------------------------------------------------------------
# リソース: /chat
# ---------------------------------------------------------------------------

resource "aws_api_gateway_resource" "chat" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_rest_api.main.root_resource_id
  path_part   = "chat"
}

# ---------------------------------------------------------------------------
# メソッド: POST /chat
# ---------------------------------------------------------------------------

resource "aws_api_gateway_method" "chat_post" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.chat.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "chat_post" {
  rest_api_id             = aws_api_gateway_rest_api.main.id
  resource_id             = aws_api_gateway_resource.chat.id
  http_method             = aws_api_gateway_method.chat_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambda_invoke_arn
}

# ---------------------------------------------------------------------------
# メソッド: OPTIONS /chat（CORS preflight）
# ---------------------------------------------------------------------------

resource "aws_api_gateway_method" "chat_options" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.chat.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "chat_options" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.chat.id
  http_method = aws_api_gateway_method.chat_options.http_method
  type        = "MOCK"

  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "chat_options_200" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.chat.id
  http_method = aws_api_gateway_method.chat_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_integration_response" "chat_options_200" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.chat.id
  http_method = aws_api_gateway_method.chat_options.http_method
  status_code = aws_api_gateway_method_response.chat_options_200.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type'"
    "method.response.header.Access-Control-Allow-Methods" = "'POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

# ---------------------------------------------------------------------------
# リソース: /chat/vtuber
# ---------------------------------------------------------------------------

resource "aws_api_gateway_resource" "chat_vtuber" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.chat.id
  path_part   = "vtuber"
}

# ---------------------------------------------------------------------------
# メソッド: POST /chat/vtuber
# ---------------------------------------------------------------------------

resource "aws_api_gateway_method" "chat_vtuber_post" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.chat_vtuber.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "chat_vtuber_post" {
  rest_api_id             = aws_api_gateway_rest_api.main.id
  resource_id             = aws_api_gateway_resource.chat_vtuber.id
  http_method             = aws_api_gateway_method.chat_vtuber_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambda_invoke_arn
}

# ---------------------------------------------------------------------------
# メソッド: OPTIONS /chat/vtuber（CORS preflight）
# ---------------------------------------------------------------------------

resource "aws_api_gateway_method" "chat_vtuber_options" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.chat_vtuber.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "chat_vtuber_options" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.chat_vtuber.id
  http_method = aws_api_gateway_method.chat_vtuber_options.http_method
  type        = "MOCK"

  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "chat_vtuber_options_200" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.chat_vtuber.id
  http_method = aws_api_gateway_method.chat_vtuber_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_integration_response" "chat_vtuber_options_200" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.chat_vtuber.id
  http_method = aws_api_gateway_method.chat_vtuber_options.http_method
  status_code = aws_api_gateway_method_response.chat_vtuber_options_200.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type'"
    "method.response.header.Access-Control-Allow-Methods" = "'POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

# ---------------------------------------------------------------------------
# デプロイ & ステージ
# ---------------------------------------------------------------------------

resource "aws_api_gateway_deployment" "main" {
  rest_api_id = aws_api_gateway_rest_api.main.id

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_integration.chat_post,
      aws_api_gateway_integration.chat_options,
      aws_api_gateway_integration.chat_vtuber_post,
      aws_api_gateway_integration.chat_vtuber_options,
      aws_api_gateway_integration_response.chat_options_200,
      aws_api_gateway_integration_response.chat_vtuber_options_200,
    ]))
  }

  depends_on = [
    aws_api_gateway_integration.chat_post,
    aws_api_gateway_integration.chat_options,
    aws_api_gateway_integration.chat_vtuber_post,
    aws_api_gateway_integration.chat_vtuber_options,
    aws_api_gateway_integration_response.chat_options_200,
    aws_api_gateway_integration_response.chat_vtuber_options_200,
  ]

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "main" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  deployment_id = aws_api_gateway_deployment.main.id
  stage_name    = var.environment
}

# ---------------------------------------------------------------------------
# Lambda実行権限（API Gatewayから呼び出せるよう）
# ---------------------------------------------------------------------------

resource "aws_lambda_permission" "apigw_invoke" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.main.execution_arn}/*/*"
}
