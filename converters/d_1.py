import pandas as pd
from pathlib import Path
from core.mappings import MODE7_MAP, PURPOSE_MAP
from core.filters import filter_summary_rows, filter_summary_columns, filter_summary_zones
from core.zone_utils import split_zone_column

def load(path: Path) -> tuple[pd.DataFrame, str]:
    """
    d-1.csv を Shift_JIS で読み込み、先頭3行をスキップしてヘッダーを取得。
    不要列（SEQ系）を除去し、共通フィルタ処理を適用。
    """
    df = pd.read_csv(path, encoding="shift_jis", header=3)

    # カラム名と値の前後の空白を除去
    df.columns = df.columns.str.strip()
    # 新（列ごとに文字列型だけ strip する）
    df = df.apply(lambda col: col.str.strip() if col.dtype == "object" else col)


    # 不要列（SEQ系）を削除
    seq_cols = [col for col in df.columns if col.strip() in {"発SEQ", "着SEQ", "目的SEQ"}]
    df = df.drop(columns=seq_cols)

    # 地域・ゾーン系列に対して split_zone_column を適用
    for col in ['地域', '発ゾーン', '着ゾーン', '発地', '着地']:
        if col in df.columns:
            df = split_zone_column(df, col)
    # 共通フィルタ処理
    df = filter_summary_rows(df)
    df = filter_summary_columns(df)
    df = filter_summary_zones(df)
    print(df)
    return df, "目的種類別×交通手段別OD表"


def convert(df: pd.DataFrame, metadata=None) -> dict[str, pd.DataFrame]:
    """
    d-1: 目的種類別×交通手段別OD表
    - 発着地ゾーンコード・名称・タイプ、目的種類ごとに、交通手段別トリップ数を縦持ちに変換
    - 目的種類コード (purpose_code) と交通手段コード (main_mode_code) を付与
    """

    df = df.copy()
    df["目的種類"] = df["目的種類"].str.replace("−", "－", regex=False)

    # カンマ区切りの数値文字列を float に変換
    for col in MODE7_MAP.keys():
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(",", "")
                .replace("nan", "0")
                .astype(int)
            )

    df["purpose_code"] = df["目的種類"].map(PURPOSE_MAP)

    records = []
    for _, row in df.iterrows():
        for mode, code in MODE7_MAP.items():
            if mode in row:
                records.append({
                    "origin_kzone": row["発地_code"],
                    "origin_kzone_name": row.get("発地_name"),
                    "origin_kzone_type": row.get("発地_type"),
                    "destination_kzone": row["着地_code"],
                    "destination_kzone_name": row.get("着地_name"),
                    "destination_kzone_type": row.get("着地_type"),
                    "purpose_code": row["purpose_code"],
                    "purpose": row["目的種類"],
                    "main_mode_code": code,
                    "main_mode": mode,
                    "trip_count": row[mode]
                })

    df_out = pd.DataFrame.from_records(records)

    return {
        "trip_od_by_purpose_and_mode": df_out
    }

