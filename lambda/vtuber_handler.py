"""
VTuber ハンドラー — フェーズ管理付き AI VTuber 会話 API
"""

import json

import dynamodb_client
import agentcore_memory_client
from bedrock_client import invoke_bedrock


def _build_messages(conversation_history: list, topic: str) -> list:
    """
    会話履歴を Bedrock messages 形式に整形する。
    履歴が空の場合は初回メッセージを生成する。
    """
    if not conversation_history:
        return [{"role": "user", "content": f"今日のトピックは「{topic}」です。配信を始めよう！自己紹介とトピックの紹介をしてください。"}]

    messages = list(conversation_history)

    # Bedrock は最後のメッセージが user である必要があるため調整
    if messages and messages[-1]["role"] == "assistant":
        messages.append({"role": "user", "content": "続けてください。"})

    return messages


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

    # AgentCore Memory から会話履歴を取得
    conversation_history = agentcore_memory_client.get_conversation_history(session_id)

    messages = _build_messages(conversation_history, topic)

    # ユーザーメッセージ（保存用）
    user_content = messages[-1]["content"] if messages and messages[-1]["role"] == "user" else "続けてください。"

    # Bedrock 呼び出し
    content = invoke_bedrock(system_prompt, messages, max_tokens=512)

    # AgentCore Memory に保存
    agentcore_memory_client.save_conversation_turn(session_id, user_content, content)

    return {"speaker": "vtuber", "content": content}
