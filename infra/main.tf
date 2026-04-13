terraform {
  required_version = ">= 1.5"

  backend "s3" {
    bucket = "girls-talk-terraform-state"
    key    = "terraform.tfstate"
    region = "ap-northeast-1"
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.21"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# DynamoDB モジュール
module "dynamodb" {
  source = "./modules/dynamodb"

  project_name = var.project_name
  environment  = var.environment
}

# Lambda モジュール
module "lambda" {
  source = "./modules/lambda"

  project_name               = var.project_name
  environment                = var.environment
  vtuber_phases_table_name   = module.dynamodb.vtuber_phases_table_name
  vtuber_phases_table_arn    = module.dynamodb.vtuber_phases_table_arn
  vtuber_sessions_table_name = module.dynamodb.vtuber_sessions_table_name
  vtuber_sessions_table_arn  = module.dynamodb.vtuber_sessions_table_arn
  agentcore_runtime_arn      = var.agentcore_runtime_arn
}

# API Gateway モジュール
module "api_gateway" {
  source = "./modules/api_gateway"

  project_name          = var.project_name
  environment           = var.environment
  lambda_invoke_arn     = module.lambda.lambda_invoke_arn
  lambda_function_name  = module.lambda.lambda_function_name
}
