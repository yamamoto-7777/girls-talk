# =============================================================================
# DynamoDB: girls-talk VTuber フェーズ管理テーブル
# =============================================================================

# ---------------------------------------------------------------------------
# vtuber-phases テーブル（フェーズ定義の格納）
# ---------------------------------------------------------------------------

resource "aws_dynamodb_table" "vtuber_phases" {
  name         = "${var.project_name}-${var.environment}-vtuber-phases"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "phase_id"

  attribute {
    name = "phase_id"
    type = "S"
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# ---------------------------------------------------------------------------
# vtuber-sessions テーブル（セッション状態の格納）
# ---------------------------------------------------------------------------

resource "aws_dynamodb_table" "vtuber_sessions" {
  name         = "${var.project_name}-${var.environment}-vtuber-sessions"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "session_id"

  attribute {
    name = "session_id"
    type = "S"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}
