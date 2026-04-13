variable "project_name" {
  description = "プロジェクト名"
  type        = string
}

variable "environment" {
  description = "環境名"
  type        = string
}

variable "vtuber_phases_table_name" {
  description = "VTuberフェーズテーブル名"
  type        = string
}

variable "vtuber_phases_table_arn" {
  description = "VTuberフェーズテーブルのARN"
  type        = string
}

variable "vtuber_sessions_table_name" {
  description = "VTuberセッションテーブル名"
  type        = string
}

variable "vtuber_sessions_table_arn" {
  description = "VTuberセッションテーブルのARN"
  type        = string
}
