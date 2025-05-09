import pandas as pd
from core.mappings import PURPOSE_MAP, VEHICLE_TYPE_MAP


def convert(df: pd.DataFrame, metadata=None) -> dict[str, pd.DataFrame]:
    df.columns = df.columns.str.strip()

    # 前処理済みの列名に合わせてrename
    df = df.rename(columns={
        "地域_code": "kzone",
        "地域_name": "kzone_name",
        "地域_type": "kzone_type",
        "目的種類": "purpose",
        "車種": "vehicle_type"
    })

    # 合計の行や不正な分類を除外
    df = df[df["vehicle_type"].isin(VEHICLE_TYPE_MAP.keys())]
    df = df[df["purpose"].isin(PURPOSE_MAP.keys())]

    # meltで縦持ち
    df_melted = df.melt(
        id_vars=["kzone", "kzone_name", "kzone_type", "purpose", "vehicle_type"],
        value_vars=[
            "トリップ数（トリップ）_運転あり",
            "トリップ数（トリップ）_運転なし",
            "トリップ数（トリップ）_不明"
        ],
        var_name="driving_status",
        value_name="trip_count"
    )

    # コード類の追加と分類名整理
    df_melted["vehicle_type_code"] = df_melted["vehicle_type"].map(VEHICLE_TYPE_MAP)
    df_melted["purpose_code"] = df_melted["purpose"].map(PURPOSE_MAP)
    df_melted["driving_status"] = df_melted["driving_status"].str.extract(r"(運転あり|運転なし|不明)")

    # 列順を整える
    df_out = df_melted[
        ["kzone", "kzone_name", "kzone_type",
         "purpose_code", "purpose",
         "vehicle_type_code", "vehicle_type",
         "driving_status", "trip_count"]
    ]

    return {
        "trip_count_by_vehicle_and_purpose": df_out
    }
