# AI VTuber - プロジェクト設定

## プロジェクト概要

AI VTuber配信システム。AI VTuberがユーザーの指定したトピックについてフェーズ制で自動トークする。フェーズ管理（プロンプト・遷移ルール・現在状態）はすべてDynamoDBで一元管理し、フロントエンドはただバックエンドを呼ぶだけのシンプルな設計。

## ディレクトリ構成

```
girls_talk/
├── frontend/          # React SPA（Vite）
│   └── src/
│       ├── components/   # VTuberView 等
│       ├── hooks/        # useVTuberConversation（useReducer）
│       ├── constants/    # 定義ファイル
│       └── types/        # 型定義
├── lambda/            # Python バックエンド（AWS Lambda）
│   ├── handler.py        # エントリーポイント・CORS処理・パスルーティング
│   ├── vtuber_handler.py # VTuber用ハンドラー（フェーズ管理・Bedrock呼び出し）
│   ├── dynamodb_client.py # DynamoDB アクセスユーティリティ
│   ├── bedrock_client.py # Bedrock Claude 呼び出し
│   ├── personas.py       # キャラクターのシステムプロンプト
│   └── vtuber_seed.py    # DynamoDB初期データ投入スクリプト（開発用）
└── infra/             # Terraform インフラ定義
    ├── main.tf
    └── modules/
        ├── lambda/       # Lambda + IAM（DynamoDB権限含む）
        ├── api_gateway/  # API Gateway + CORS（/chat/vtuber）
        └── dynamodb/     # DynamoDB テーブル定義
```

## 技術スタック

| 領域 | 技術 |
|------|------|
| フロントエンド | React 19 + TypeScript 6 + Vite 8 |
| スタイリング | CSS Modules |
| 状態管理 | useReducer のみ（外部ライブラリなし） |
| バックエンド | Python 3.12 + AWS Lambda |
| AI基盤 | AWS Bedrock + Claude Sonnet 4.6 |
| API | AWS API Gateway REST API（東京リージョン） |
| DB | AWS DynamoDB（オンデマンドキャパシティ） |
| インフラ | Terraform >= 1.5（S3バックエンド） |
| Linter | ESLint 9 + typescript-eslint 8 |

## 開発コマンド

```bash
# フロントエンド
cd frontend && npm run dev      # ローカル開発サーバー起動
cd frontend && npm run build    # tsc -b && vite build
cd frontend && npm run lint     # ESLint 実行

# インフラ
cd infra && terraform plan
cd infra && terraform apply

# DynamoDB 初期データ投入（terraform apply 後に実行）
cd lambda && VTUBER_PHASES_TABLE=<テーブル名> python vtuber_seed.py
```

## 環境変数

### フロントエンド

| 変数名 | 説明 |
|--------|------|
| `VITE_API_URL` | API GatewayのベースURL（例: `https://xxxxx.execute-api.ap-northeast-1.amazonaws.com/prod`） |

### Lambda

| 変数名 | 説明 |
|--------|------|
| `VTUBER_PHASES_TABLE` | vtuber-phases DynamoDB テーブル名 |
| `VTUBER_SESSIONS_TABLE` | vtuber-sessions DynamoDB テーブル名 |

## アーキテクチャ

```
[ユーザー] トピック入力 → 「開始」ボタン押下
  → [useVTuberConversation] sessionId(UUID)を生成
  → [fetch] POST /chat/vtuber { sessionId, currentSpeaker, conversationHistory(直近5件) }
  → [API Gateway] → [Lambda handler.py] → パスルーティング → [vtuber_handler.py]
  → [dynamodb_client.py] セッション状態取得（現在フェーズ）
  → [dynamodb_client.py] フェーズ定義取得（プロンプト）
  → [bedrock_client.py] Claude Sonnet 4.6 呼び出し
  → レスポンス { speaker, content }
  → フロント：表示 → 次リクエスト（最大10回 or 停止ボタンで中断）
```

## DynamoDB テーブル設計

### vtuber-phases（フェーズ定義マスタ）

| 属性 | 型 | 役割 |
|------|-----|------|
| `phase_id` (PK) | String | フェーズ識別子（opening / main / closing） |
| `order` | Number | フェーズ順序 |
| `system_prompt` | String | システムプロンプト |
| `turns_in_phase` | Number | このフェーズで消化するターン数 |
| `next_phase_id` | String / null | 次フェーズのID（最終フェーズはnull） |

初期データ:
- `opening`（order:1, turns:2, next→main）
- `main`（order:2, turns:6, next→closing）
- `closing`（order:3, turns:2, next→null）

### vtuber-sessions（セッション状態）

| 属性 | 型 | 役割 |
|------|-----|------|
| `session_id` (PK) | String | セッションUUID |
| `current_phase_id` | String | 現在のフェーズID |
| `phase_turn_count` | Number | 現フェーズ内の消化ターン数 |
| `total_turn_count` | Number | 全体の消化ターン数 |
| `ttl` | Number | TTL（24時間後に自動削除） |

## API仕様

### POST /chat/vtuber

- リクエスト: `{ sessionId: string, conversationHistory: Message[] }`
- レスポンス成功: `{ speaker: string, content: string }`
- レスポンスエラー: `{ error: string }`
- Lambda処理: DynamoDBからセッション状態・フェーズプロンプトを取得 → Bedrock呼び出し

## 設計方針

### フロントエンドの責務（最小限）
- `sessionId`（UUID）を生成して保持
- APIを呼んで応答を表示するループ（最大10回 or 停止ボタンで中断）
- フェーズもターン番号も意識しない

### バックエンド（Lambda）の責務
- DynamoDBから現在のフェーズ状態を取得
- フェーズに対応するプロンプトをDynamoDBから取得
- Bedrockを呼び出してレスポンス生成
- **フェーズ遷移はプログラムで行わない** — フェーズの切り替えはDynamoDBのデータを直接変更して管理する（手動 or 外部ツール）

### DynamoDBの責務（すべてのステートとプロンプトを管理）
- 各フェーズのプロンプト内容（マスタデータ）
- 現在のフェーズ（セッション状態）

## コーディング規約

- フロントエンド: TypeScript strict モード、CSS Modules でスタイリング
- ルーティングなし（単一ページ SPA）
- 外部状態管理ライブラリは使わず useReducer で管理
- バックエンド: Python、Lambda ハンドラーパターン
- CORSヘッダーはLambda側で付与
- DynamoDB テーブル名はハードコード禁止（環境変数から読み込む）
- Lambda の boto3 クライアントはモジュールレベルで初期化（コールドスタート対策）
