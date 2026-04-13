"""
VTuber フェーズ初期データ投入スクリプト

使用方法:
    VTUBER_PHASES_TABLE=girls-talk-prod-vtuber-phases python vtuber_seed.py

テーブル名は環境変数 VTUBER_PHASES_TABLE から読み込む。
未設定の場合はスクリプト内のデフォルト値を使用する。
"""

import os
import boto3

# テーブル名（terraform apply 後に環境変数で上書き可能）
PHASES_TABLE_NAME = os.environ.get(
    "VTUBER_PHASES_TABLE",
    "girls-talk-prod-vtuber-phases",
)

dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-1")
table = dynamodb.Table(PHASES_TABLE_NAME)

PHASES = [
    {
        "phase_id": "opening",
        "order": 1,
        "turns_in_phase": 2,
        "next_phase_id": "main",
        "system_prompt": (
            "あなたはAI VTuberです。"
            "明るく元気な性格で、配信を盛り上げるのが得意です。"
            "今から配信を始めます。まずは自己紹介とトピックの紹介をしてください。"
        ),
    },
    {
        "phase_id": "main",
        "order": 2,
        "turns_in_phase": 6,
        "next_phase_id": "closing",
        "system_prompt": (
            "あなたはAI VTuberです。"
            "明るく元気な性格です。"
            "トピックについて自分の意見や感想を自由に話してください。"
            "視聴者が楽しめるよう、エンタメ性を大切にしながら話を盛り上げてください。"
        ),
    },
    {
        "phase_id": "closing",
        "order": 3,
        "turns_in_phase": 2,
        "next_phase_id": None,
        "system_prompt": (
            "あなたはAI VTuberです。"
            "配信の締めくくりです。"
            "今日の話題を振り返って感想を述べ、視聴者に感謝の気持ちを伝えてください。"
        ),
    },
]


def seed() -> None:
    print(f"テーブル '{PHASES_TABLE_NAME}' へのデータ投入を開始します...")

    for phase in PHASES:
        # DynamoDB は None を格納できないため next_phase_id が None の場合はスキップ
        item = {k: v for k, v in phase.items() if v is not None}
        table.put_item(Item=item)
        print(f"  投入完了: phase_id={phase['phase_id']}")

    print("全フェーズデータの投入が完了しました。")


if __name__ == "__main__":
    seed()
