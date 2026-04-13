"""
Bedrock 呼び出しクライアント
"""

import json
import boto3

# boto3 は Lambda Python ランタイムに標準同梱
client = boto3.client("bedrock-runtime", region_name="ap-northeast-1")

# Claude Sonnet 4.6 - JP クロスリージョン推論プロファイル（Tokyo/Osaka）
MODEL_ID = "jp.anthropic.claude-sonnet-4-6"


def invoke_bedrock(system_prompt: str, messages: list, max_tokens: int = 512) -> str:
    """
    Bedrock Claude にメッセージを送り、応答テキスト全文を返す

    Args:
        system_prompt: AIのシステムプロンプト
        messages: 会話履歴 [{"role": str, "content": str}, ...]
        max_tokens: 最大トークン数（デフォルト: 512）

    Returns:
        応答テキスト
    """
    body = json.dumps(
        {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "system": system_prompt,
            "messages": messages,
        }
    )

    response = client.invoke_model(
        modelId=MODEL_ID,
        contentType="application/json",
        accept="application/json",
        body=body,
    )

    decoded = json.loads(response["body"].read())
    content = decoded.get("content", [])
    if content and len(content) > 0:
        return content[0].get("text", "")
    return ""
