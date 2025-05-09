import pandas as pd
import re
from core.mappings import MODE7_MAP, FACILITY_MAP


def convert(df: pd.DataFrame, metadata=None) -> dict[str, pd.DataFrame]:
    """
    c-4.xlsx: ゾーン別・施設別・代表交通手段別発生集中量
    - 地域を地域_code/name/typeで処理
    - 発生量・集中量を縦持ちに変換
    - 施設コード facility_code を付与
    - モードコード main_mode_code を付与
    - 出力列順を整理
    """

    df = df.copy()
    df.columns = df.columns.map(lambda x: str(x).strip())

    origin_pattern = r"^発生量（トリップ数）_(.+)$"
    destination_pattern = r"^集中量（トリップ数）_(.+)$"

    origin_cols = [col for col in df.columns if re.match(origin_pattern, col)]
    destination_cols = [col for col in df.columns if re.match(destination_pattern, col)]

    def melt_and_parse(df, col_names, value_name, prefix):
        df_melted = df[["地域_code", "地域_name", "地域_type", "施設"] + col_names].melt(
            id_vars=["地域_code", "地域_name", "地域_type", "施設"],
            var_name="full_col", value_name=value_name
        )
        df_melted["main_mode"] = df_melted["full_col"].str.replace(prefix, "", regex=False)
        df_melted = df_melted.rename(columns={"施設": "facility"})
        df_melted["main_mode_code"] = df_melted["main_mode"].map(MODE7_MAP)
        df_melted["facility_code"] = df_melted["facility"].map(FACILITY_MAP)
        return df_melted

    df_origin = melt_and_parse(df, origin_cols, "production_trip_count", "発生量（トリップ数）_")
    df_dest = melt_and_parse(df, destination_cols, "attraction_trip_count", "集中量（トリップ数）_")

    df_merged = pd.merge(
        df_origin,
        df_dest,
        on=["地域_code", "地域_name", "地域_type", "facility", "facility_code", "main_mode", "main_mode_code"],
        how="outer"
    )

    df_merged = df_merged.rename(columns={
        "地域_code": "kzone",
        "地域_name": "kzone_name",
        "地域_type": "kzone_type"
    })

    df_merged = df_merged[
        ["kzone", "kzone_name", "kzone_type",
         "facility_code", "facility", "main_mode_code", "main_mode",
         "production_trip_count", "attraction_trip_count"]
    ]

    return {
        "trip_origin_dest_by_facility_and_mode": df_merged
    }
