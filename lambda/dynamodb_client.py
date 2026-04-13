"""
DynamoDB クライアント — VTuber フェーズ・セッション管理
"""

import os
import boto3
from boto3.dynamodb.conditions import Key

# boto3 リソースはモジュールレベルで初期化（コールドスタート対策）
dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-1")

PHASES_TABLE_NAME = os.environ["VTUBER_PHASES_TABLE"]
SESSIONS_TABLE_NAME = os.environ["VTUBER_SESSIONS_TABLE"]

_phases_table = dynamodb.Table(PHASES_TABLE_NAME)
_sessions_table = dynamodb.Table(SESSIONS_TABLE_NAME)

# セッションが存在しない場合のデフォルト値
_DEFAULT_SESSION = {
    "current_phase_id": "opening",
    "phase_turn_count": 0,
    "total_turn_count": 0,
}


def get_session(session_id: str) -> dict:
    """
    セッションテーブルから現在のフェーズ情報を取得する。
    未存在の場合はデフォルト値を返す。

    Returns:
        {
            "current_phase_id": str,
            "phase_turn_count": int,
            "total_turn_count": int,
        }
    """
    response = _sessions_table.get_item(Key={"session_id": session_id})
    item = response.get("Item")
    if not item:
        return dict(_DEFAULT_SESSION)

    return {
        "current_phase_id": item.get("current_phase_id", _DEFAULT_SESSION["current_phase_id"]),
        "phase_turn_count": int(item.get("phase_turn_count", _DEFAULT_SESSION["phase_turn_count"])),
        "total_turn_count": int(item.get("total_turn_count", _DEFAULT_SESSION["total_turn_count"])),
    }


def get_phase(phase_id: str) -> dict | None:
    """
    フェーズテーブルからフェーズ定義を取得する。

    Returns:
        フェーズ定義 dict、または未存在なら None
    """
    response = _phases_table.get_item(Key={"phase_id": phase_id})
    return response.get("Item")
