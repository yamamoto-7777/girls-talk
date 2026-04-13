"""
VTuber フェーズ・セッション初期データ投入 Lambda ハンドラー

AWSコンソールのテスト実行ボタンから実行することを想定。
テーブル名は環境変数 VTUBER_PHASES_TABLE / VTUBER_SESSIONS_TABLE から取得する。
"""

import json
import os

import boto3

PHASES_TABLE_NAME = os.environ["VTUBER_PHASES_TABLE"]
SESSIONS_TABLE_NAME = os.environ["VTUBER_SESSIONS_TABLE"]

dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-1")
table = dynamodb.Table(PHASES_TABLE_NAME)
sessions_table = dynamodb.Table(SESSIONS_TABLE_NAME)

INITIAL_SESSION = {
    "session_id": "test-session-001",
    "current_phase_id": "opening",
    "phase_turn_count": 0,
    "total_turn_count": 0,
}

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


def handler(event, context):
    """
    Lambda エントリーポイント。

    DynamoDB の vtuber-phases テーブルに初期フェーズデータを投入し、
    vtuber-sessions テーブルにテスト用セッション初期データを投入する。
    既存データがある場合は上書きされる（PutItem の冪等性を利用）。

    Returns:
        dict: statusCode と投入結果メッセージを含むレスポンス
    """
    inserted_phases = []
    inserted_sessions = []
    try:
        for phase in PHASES:
            # DynamoDB は None を格納できないため next_phase_id が None の場合はスキップ
            item = {k: v for k, v in phase.items() if v is not None}
            table.put_item(Item=item)
            inserted_phases.append(phase["phase_id"])

        sessions_table.put_item(Item=INITIAL_SESSION)
        inserted_sessions.append(INITIAL_SESSION["session_id"])

        message = (
            f"全データの投入が完了しました。"
            f"投入済みフェーズ: {inserted_phases}、"
            f"投入済みセッション: {inserted_sessions}"
        )
        print(message)
        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": message,
                    "inserted_phases": inserted_phases,
                    "inserted_sessions": inserted_sessions,
                },
                ensure_ascii=False,
            ),
        }

    except Exception as e:
        error_message = f"データ投入中にエラーが発生しました: {str(e)}"
        print(error_message)
        return {
            "statusCode": 500,
            "body": json.dumps(
                {"error": error_message},
                ensure_ascii=False,
            ),
        }
