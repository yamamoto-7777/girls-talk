"""
Bedrock AgentCore Memory クライアント — 会話履歴の短期記憶管理
"""

import os
from datetime import datetime
import boto3

client = boto3.client("bedrock-agentcore", region_name="ap-northeast-1")

MEMORY_ID = os.environ["AGENTCORE_MEMORY_ID"]
ACTOR_ID = "vtuber-system"


def get_conversation_history(session_id: str, max_results: int = 10) -> list:
    """
    セッションの会話履歴を取得し、Bedrock messages 形式で返す。

    Returns:
        [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}, ...]
    """
    response = client.list_events(
        memoryId=MEMORY_ID,
        actorId=ACTOR_ID,
        sessionId=session_id,
        maxResults=max_results,
    )

    messages = []
    for event in response.get("events", []):
        for payload_item in event.get("payload", []):
            conv = payload_item.get("conversationPayload")
            if not conv:
                continue
            role = conv.get("role", "").lower()
            content_list = conv.get("content", [])
            text = content_list[0].get("text", "") if content_list else ""
            if role in ("user", "assistant") and text:
                messages.append({"role": role, "content": text})

    return messages


def save_conversation_turn(session_id: str, user_content: str, assistant_content: str) -> None:
    """
    1ターン分（user + assistant）の会話を保存する。
    """
    client.create_event(
        memoryId=MEMORY_ID,
        actorId=ACTOR_ID,
        sessionId=session_id,
        eventTimestamp=datetime.now(),
        payload=[
            {
                "conversationPayload": {
                    "content": [{"text": user_content}],
                    "role": "USER",
                }
            },
            {
                "conversationPayload": {
                    "content": [{"text": assistant_content}],
                    "role": "ASSISTANT",
                }
            },
        ],
    )
