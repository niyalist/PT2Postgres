import pandas as pd
from core.mappings import PURPOSE_MAP, PARKING_LOCATION_MAP

def convert(df: pd.DataFrame, metadata=None) -> dict[str, pd.DataFrame]:
    """
    e-3.xlsx: 着ゾーン別・目的種類別・駐車場所数
    - 地域列は split_zone_column 済み（地域_code, name, type）
    - 駐車場所列を縦持ちに変換し、対応コードを付加
    - 目的種類 → purpose_code を付加
    """
    df = df.copy()
    df.columns = df.columns.map(str).str.strip()

    id_vars = ["地域_code", "地域_name", "地域_type", "目的種類"]
    value_vars = [col for col in df.columns if col.startswith("駐車場所_") and "合計" not in col]

    # melt で縦持ちに
    df_melted = df.melt(
        id_vars=id_vars,
        value_vars=value_vars,
        var_name="parking_location",
        value_name="count"
    )

    # ラベル整形とコード付加
    df_melted["parking_location"] = df_melted["parking_location"].str.replace("駐車場所_", "", regex=False)
    df_melted["parking_location_code"] = df_melted["parking_location"].map(PARKING_LOCATION_MAP)
    df_melted["purpose_code"] = df_melted["目的種類"].map(PURPOSE_MAP)

    # カラム整形・並び順
    df_out = df_melted.rename(columns={
        "地域_code": "kzone",
        "地域_name": "kzone_name",
        "地域_type": "kzone_type",
        "目的種類": "purpose"
    })[[
        "kzone", "kzone_name", "kzone_type",
        "purpose_code", "purpose",
        "parking_location_code", "parking_location",
        "count"
    ]]

    return {
        "parking_count_by_location_and_purpose": df_out
    }
