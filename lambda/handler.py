"""
Lambda ハンドラー — girls-talk VTuber チャット API
"""

import json
import vtuber_handler

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
}


def _response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": {**CORS_HEADERS, "Content-Type": "application/json"},
        "body": json.dumps(body, ensure_ascii=False),
    }


def handler(event, context):
    # OPTIONS リクエスト（CORS preflight）対応
    if event.get("httpMethod") == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": {**CORS_HEADERS, "Content-Type": "application/json"},
            "body": "",
        }

    # パスベースのルーティング
    path = event.get("path", "")
    if path == "/chat/vtuber":
        result = vtuber_handler.handle(event, context)
        # エラーレスポンスの場合（statusCode が 4xx/5xx）
        if "error" in result:
            status_code = result.get("statusCode", 500)
            return _response(status_code, {"error": result["error"]})
        return _response(200, {"speaker": result["speaker"], "content": result["content"]})

    return _response(404, {"error": "Not found"})
