---
name: deploy
description: Lambda関数およびAPI GatewayをTerraformでデプロイする
disable-model-invocation: true
allowed-tools: Bash(terraform *)
---

# デプロイ手順

1. `infra/` ディレクトリで `terraform plan` を実行し、変更内容を確認する
2. ユーザーに変更内容を報告し、問題なければ適用する
3. 完了後、出力される `api_gateway_endpoint` を報告する

```bash
cd /Users/kazuma/Work/girls_talk/infra
terraform plan -no-color
terraform apply -auto-approve -no-color
```

## 注意事項

- Lambda のソースコードは `lambda/` ディレクトリを Terraform が自動で zip 化してアップロードする
- `source_code_hash` でコード変更を検知するため、コード変更があれば `terraform apply` だけで反映される
- S3 バックエンド（`girls-talk-terraform-state`）でステート管理
- リージョンは `ap-northeast-1`（東京）
