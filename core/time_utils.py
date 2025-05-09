import re

def normalize_time_slot(text: str) -> str:
    """
    時間帯表記の正規化：
    - 全角数字を半角に変換
    - 前後の空白を除去
    """
    return str(text).translate(str.maketrans("０１２３４５６７８９", "0123456789")).strip()


def time_slot_to_code(slot: str) -> int | None:
    """
    時間帯表記から時間コードへの変換：
    - "～3時台" → 2
    - "10時台", "27時台～" → 数値部分を抽出（例: 10, 27）
    - "不明" → 99
    - 上記以外は None
    """
    slot = normalize_time_slot(slot)

    if "不明" in slot:
        return 99
    if slot.startswith("～3"):
        return 2

    match = re.match(r"^(\d+)時台", slot)  # ← 「時台」で始まればOK、末尾に何がついていても可
    if match:
        return int(match.group(1))

    return None
