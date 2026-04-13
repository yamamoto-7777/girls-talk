"""
Bedrock 呼び出しクライアント
"""

import logging

import boto3

logger = logging.getLogger(__name__)

# Claude Sonnet 4.6 - JP クロスリージョン推論プロファイル（Tokyo/Osaka）
MODEL_ID = "jp.anthropic.claude-sonnet-4-6"

# boto3 は Lambda Python ランタイムに標準同梱
# モジュールレベルで初期化（コールドスタート対策）
client = boto3.client("bedrock-runtime", region_name="ap-northeast-1")


def invoke_bedrock(
    system_prompt: str,
    messages: list,
    session_id: str,
    max_tokens: int = 512,
) -> str:
    """
    Bedrock Claude にメッセージを送り、応答テキスト全文を返す。
    session_id は将来の AgentCore Memory 統合のために受け取るが、現在は未使用。
    """
    response = client.converse(
        modelId=MODEL_ID,
        system=[{"text": system_prompt}],
        messages=messages,
        inferenceConfig={"maxTokens": max_tokens},
    )

    output = response.get("output", {})
    message = output.get("message", {})
    content = message.get("content", [])

    text_parts = [
        block.get("text", "")
        for block in content
        if isinstance(block, dict) and block.get("text")
    ]
    result = "".join(text_parts)

    if not result:
        logger.error("Bedrock converse から空のレスポンスが返されました: %s", response)
        raise ValueError("Bedrock から空のレスポンスが返されました")

    return result
