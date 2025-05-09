import pandas as pd
import re
from core.mappings import PURPOSE_MAP, MODE7_MAP

def convert(df: pd.DataFrame, metadata=None) -> dict[str, pd.DataFrame]:
    """
    c-1.xlsx: ゾーン別・目的種類・代表交通手段別発生集中量
    - 地域列は前処理により '地域_code', '地域_name', '地域_type' に分割済
    - 交通手段別の発生量・集中量を縦持ちに
    - main_mode に7区分コード main_mode_code を付加
    """
    df = df.copy()
    df.columns = df.columns.map(str.strip)

    origin_cols = [col for col in df.columns if col.startswith("発生量") and not col.endswith("合計")]
    destination_cols = [col for col in df.columns if col.startswith("集中量") and not col.endswith("合計")]

    id_vars = ["地域_code", "地域_name", "地域_type", "目的種類"]

    # 発生量
    df_origin = df[id_vars + origin_cols].copy()
    df_origin = df_origin.melt(id_vars=id_vars, var_name="main_mode", value_name="production_trip_count")
    df_origin["main_mode"] = (
        df_origin["main_mode"]
        .str.replace("^発生量", "", regex=True)
        .str.replace("（トリップ数）_?", "", regex=True)
        .str.replace("_?", "", regex=True)
    )
    df_origin["main_mode_code"] = df_origin["main_mode"].apply(
        lambda x: next((v for k, v in MODE7_MAP.items() if k in x), None)
    )
    df_origin = df_origin.rename(columns={"目的種類": "purpose"})
    df_origin["purpose_code"] = df_origin["purpose"].map(PURPOSE_MAP)

    # 集中量
    df_dest = df[id_vars + destination_cols].copy()
    df_dest = df_dest.melt(id_vars=id_vars, var_name="main_mode", value_name="attraction_trip_count")
    df_dest["main_mode"] = (
        df_dest["main_mode"]
        .str.replace("^集中量", "", regex=True)
        .str.replace("（トリップ数）_?", "", regex=True)
        .str.replace("_?", "", regex=True)
    )
    df_dest["main_mode_code"] = df_dest["main_mode"].apply(
        lambda x: next((v for k, v in MODE7_MAP.items() if k in x), None)
    )
    df_dest = df_dest.rename(columns={"目的種類": "purpose"})
    df_dest["purpose_code"] = df_dest["purpose"].map(PURPOSE_MAP)

    # 結合
    merge_keys = ["地域_code", "地域_name", "地域_type", "purpose_code", "purpose", "main_mode_code", "main_mode"]
    df_merged = pd.merge(df_origin, df_dest, on=merge_keys, how="outer")

    # 整形
    df_merged = df_merged.rename(columns={
        "地域_code": "kzone",
        "地域_name": "kzone_name",
        "地域_type": "kzone_type"
    })

    df_merged = df_merged[
        ["kzone", "kzone_name", "kzone_type",
         "purpose_code", "purpose", "main_mode_code", "main_mode",
         "production_trip_count", "attraction_trip_count"]
    ]

    return {
        "trip_origin_dest_by_mode_and_purpose": df_merged
    }
