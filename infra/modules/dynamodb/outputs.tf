output "vtuber_phases_table_name" {
  description = "VTuberフェーズテーブル名"
  value       = aws_dynamodb_table.vtuber_phases.name
}

output "vtuber_phases_table_arn" {
  description = "VTuberフェーズテーブルのARN"
  value       = aws_dynamodb_table.vtuber_phases.arn
}

output "vtuber_sessions_table_name" {
  description = "VTuberセッションテーブル名"
  value       = aws_dynamodb_table.vtuber_sessions.name
}

output "vtuber_sessions_table_arn" {
  description = "VTuberセッションテーブルのARN"
  value       = aws_dynamodb_table.vtuber_sessions.arn
}
