import pandas as pd
from core.mappings import MODE7_MAP

def convert(df: pd.DataFrame, metadata=None) -> dict[str, pd.DataFrame]:
    """
    e-2.xlsx: ゾーン間・代表交通手段別平均所要時間（7区分）
    - 横持ちを縦持ちに変換
    - 発ゾーン・着ゾーンのコード/名称/typeを含む
    - 交通手段コード main_mode_code を付与
    """

    df = df.copy()
    df.columns = df.columns.map(str).str.strip()

    # melt 対象の列だけ抽出
    value_columns = [col for col in df.columns if col.startswith("平均所要時間（分）_")]

    df_melted = df.melt(
        id_vars=[
            "発ゾーン_code", "発ゾーン_name", "発ゾーン_type",
            "着ゾーン_code", "着ゾーン_name", "着ゾーン_type"
        ],
        value_vars=value_columns,
        var_name="mode_col",
        value_name="mean_travel_time"
    )

    # モード名の抽出・正規化
    df_melted["main_mode"] = (
        df_melted["mode_col"]
        .str.replace("平均所要時間（分）_", "", regex=False)
    )
    df_melted["main_mode_code"] = df_melted["main_mode"].map(MODE7_MAP)

    # 出力列の整備
    df_out = df_melted[[
        "発ゾーン_code", "発ゾーン_name", "発ゾーン_type",
        "着ゾーン_code", "着ゾーン_name", "着ゾーン_type",
        "main_mode_code", "main_mode", "mean_travel_time"
    ]].rename(columns={
        "発ゾーン_code": "origin_kzone",
        "発ゾーン_name": "origin_kzone_name",
        "発ゾーン_type": "origin_zone_type",
        "着ゾーン_code": "destination_kzone",
        "着ゾーン_name": "destination_kzone_name",
        "着ゾーン_type": "destination_zone_type"
    })

    return {
        "mean_travel_time_by_mode_and_od": df_out
    }
