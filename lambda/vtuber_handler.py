"""
VTuber ハンドラー — フェーズ管理付き AI VTuber 会話 API
"""

import json

import dynamodb_client
from bedrock_client import invoke_bedrock


def _build_message(session: dict, topic: str) -> list:
    """
    今回のターンで送信するメッセージを生成する。
    会話履歴は AgentCore Runtime がセッション単位で保持するため、
    ここでは今回のメッセージのみを返す。
    """
    total_turn_count = session.get("total_turn_count", 0)

    if total_turn_count == 0:
        return [{"role": "user", "content": f"今日のトピックは「{topic}」です。配信を始めよう！自己紹介とトピックの紹介をしてください。"}]

    return [{"role": "user", "content": "続けてください。"}]


def handle(event: dict, context) -> dict:
    """
    POST /chat/vtuber ハンドラー

    リクエスト:
        {
            "sessionId": str,
            "topic": str
        }

    レスポンス:
        { "speaker": "vtuber", "content": str }
    """
    # リクエストボディのパース
    try:
        raw_body = event.get("body", "{}")
        if isinstance(raw_body, str):
            body = json.loads(raw_body)
        else:
            body = raw_body or {}

        session_id = body.get("sessionId")
        topic = body.get("topic", "")
    except (json.JSONDecodeError, TypeError):
        return {"statusCode": 400, "error": "Invalid request body"}

    # バリデーション
    if not session_id:
        return {"statusCode": 400, "error": "sessionId is required"}

    # セッション取得
    session = dynamodb_client.get_session(session_id)
    current_phase_id = session["current_phase_id"]

    # フェーズ定義取得
    phase = dynamodb_client.get_phase(current_phase_id)
    if not phase:
        return {"statusCode": 500, "error": f"Phase not found: {current_phase_id}"}

    system_prompt = phase.get("system_prompt", "")

    messages = _build_message(session, topic)

    # Bedrock AgentCore Runtime 呼び出し
    content = invoke_bedrock(system_prompt, messages, session_id=session_id, max_tokens=512)

    # セッションのターンカウントを更新して永続化
    # current_phase_id は変更しない（フェーズ遷移はDynamoDBを手動変更で管理する設計）
    new_total_turn_count = session.get("total_turn_count", 0) + 1
    new_phase_turn_count = session.get("phase_turn_count", 0) + 1
    dynamodb_client.update_session_turn_counts(
        session_id=session_id,
        phase_turn_count=new_phase_turn_count,
        total_turn_count=new_total_turn_count,
    )

    return {"speaker": "vtuber", "content": content}
