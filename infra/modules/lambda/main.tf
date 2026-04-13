# =============================================================================
# Lambda: girls-talk チャットハンドラー
# =============================================================================

# Lambda デプロイパッケージ（lambdaディレクトリをzip）
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../../lambda"
  output_path = "${path.module}/lambda_package.zip"
  excludes    = ["*.zip", "__pycache__", "*.pyc"]
}

# ---------------------------------------------------------------------------
# IAMロール
# ---------------------------------------------------------------------------

resource "aws_iam_role" "lambda_exec" {
  name = "${var.project_name}-${var.environment}-lambda-exec"

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

# 基本実行権限（CloudWatch Logs）
resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Bedrock呼び出し権限
resource "aws_iam_role_policy" "bedrock_invoke" {
  name = "${var.project_name}-${var.environment}-bedrock-invoke"
  role = aws_iam_role.lambda_exec.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
        ]
        Resource = "*"
      }
    ]
  })
}

# DynamoDB アクセス権限
resource "aws_iam_role_policy" "dynamodb_access" {
  name = "${var.project_name}-${var.environment}-dynamodb-access"
  role = aws_iam_role.lambda_exec.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
        ]
        Resource = [
          var.vtuber_phases_table_arn,
          var.vtuber_sessions_table_arn,
        ]
      }
    ]
  })
}

# ---------------------------------------------------------------------------
# Lambda関数
# ---------------------------------------------------------------------------

resource "aws_lambda_function" "chat_handler" {
  function_name = "${var.project_name}-${var.environment}-chat-handler"
  role          = aws_iam_role.lambda_exec.arn
  handler       = "handler.handler"
  runtime       = "python3.12"
  timeout       = 300
  memory_size   = 256

  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = {
      VTUBER_PHASES_TABLE   = var.vtuber_phases_table_name
      VTUBER_SESSIONS_TABLE = var.vtuber_sessions_table_name
    }
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# =============================================================================
# Lambda: DynamoDB 初期データ投入（seed）
# =============================================================================

# ---------------------------------------------------------------------------
# IAMロール（seed専用・最小権限）
# ---------------------------------------------------------------------------

resource "aws_iam_role" "lambda_seed_exec" {
  name = "${var.project_name}-${var.environment}-lambda-seed-exec"

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

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# 基本実行権限（CloudWatch Logs）
resource "aws_iam_role_policy_attachment" "lambda_seed_basic" {
  role       = aws_iam_role.lambda_seed_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# DynamoDB PutItem 権限（vtuber-phases テーブルのみ）
resource "aws_iam_role_policy" "seed_dynamodb_access" {
  name = "${var.project_name}-${var.environment}-seed-dynamodb-access"
  role = aws_iam_role.lambda_seed_exec.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
        ]
        Resource = [
          var.vtuber_phases_table_arn,
          var.vtuber_sessions_table_arn,
        ]
      }
    ]
  })
}

# ---------------------------------------------------------------------------
# Lambda関数（seed）
# ---------------------------------------------------------------------------

resource "aws_lambda_function" "seed_handler" {
  function_name = "${var.project_name}-${var.environment}-seed-handler"
  role          = aws_iam_role.lambda_seed_exec.arn
  handler       = "seed_handler.handler"
  runtime       = "python3.12"
  timeout       = 60
  memory_size   = 128

  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = {
      VTUBER_PHASES_TABLE   = var.vtuber_phases_table_name
      VTUBER_SESSIONS_TABLE = var.vtuber_sessions_table_name
    }
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}
