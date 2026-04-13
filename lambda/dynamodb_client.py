"""
DynamoDB クライアント — VTuber フェーズ・セッション管理
"""

import os
import time
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


def update_session_turn_counts(session_id: str, phase_turn_count: int, total_turn_count: int) -> None:
    """
    セッションのターンカウントを更新する。
    current_phase_id は変更しない（フェーズ遷移はプログラムで行わない設計）。
    セッションが存在しない場合は opening フェーズで新規作成する。
    TTL は 24 時間後に設定する。
    """
    ttl = int(time.time()) + 86400  # 24時間後

    _sessions_table.update_item(
        Key={"session_id": session_id},
        UpdateExpression=(
            "SET phase_turn_count = :ptc, total_turn_count = :ttc, #ttl_attr = :ttl, "
            "current_phase_id = if_not_exists(current_phase_id, :default_phase)"
        ),
        ExpressionAttributeNames={"#ttl_attr": "ttl"},
        ExpressionAttributeValues={
            ":ptc": phase_turn_count,
            ":ttc": total_turn_count,
            ":ttl": ttl,
            ":default_phase": _DEFAULT_SESSION["current_phase_id"],
        },
    )


def get_phase(phase_id: str) -> dict | None:
    """
    フェーズテーブルからフェーズ定義を取得する。

    Returns:
        フェーズ定義 dict、または未存在なら None
    """
    response = _phases_table.get_item(Key={"phase_id": phase_id})
    return response.get("Item")
