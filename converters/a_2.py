import pandas as pd
from core.mappings import EMPLOYMENT_TYPE_MAP

def convert(df: pd.DataFrame, metadata=None) -> dict[str, pd.DataFrame]:
    """
    a-2.xlsx: 居住地ゾーン別・就業別人口
    - 各就業形態列を縦持ちに変換
    - EMPLOYMENT_TYPE_MAP を参照して employment_type_code を付加
    - 地域コード・名称・種別を出力（前処理で分解済み）
    """
    # 対象となる就業形態列
    employment_columns = [f"就業_{label}" for label in EMPLOYMENT_TYPE_MAP]

    # melt で縦持ちに変換
    df_melted = df.melt(
        id_vars=["地域_code", "地域_name", "地域_type"],
        value_vars=employment_columns,
        var_name="employment_type",
        value_name="population"
    )

    # ラベル整形とコード付加
    df_melted["employment_type"] = df_melted["employment_type"].str.replace("就業_", "", regex=False)
    df_melted["employment_type_code"] = df_melted["employment_type"].map(EMPLOYMENT_TYPE_MAP)

    # 列名整理
    df_melted = df_melted.rename(columns={
        "地域_code": "kzone",
        "地域_name": "kzone_name",
        "地域_type": "kzone_type"
    })

    df_out = df_melted[[
        "kzone", "kzone_name", "kzone_type",
        "employment_type_code", "employment_type", "population"
    ]].copy()

    return {
        "population_by_employment_type": df_out
    }
