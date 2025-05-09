import pandas as pd
import re
from core.mappings import MODE7_MAP
from core.time_utils import normalize_time_slot, time_slot_to_code


def convert(df: pd.DataFrame, metadata=None) -> dict[str, pd.DataFrame]:
    """
    c-3.xlsx: ゾーン別・代表交通手段別・発生時間帯別 発生集中量
    - 地域列（地域_code, 地域_name, 地域_type）に対応
    - 発生量・集中量を縦持ちに変換
    - 時間帯を 'time_slot' に統一、time_code を付与
    - main_mode_code を追加
    """
    df = df.copy()
    df.columns = df.columns.map(str.strip)

    origin_pattern = r"^発生量（トリップ）_(.+)$"
    destination_pattern = r"^集中量（トリップ）_(.+)$"

    origin_cols = [col for col in df.columns if re.match(origin_pattern, col)]
    destination_cols = [col for col in df.columns if re.match(destination_pattern, col)]


    def melt_and_parse(df, col_names, value_name, prefix):
        df_melted = df[["地域_code", "地域_name", "地域_type", "時間帯"] + col_names].melt(
            id_vars=["地域_code", "地域_name", "地域_type", "時間帯"],
            var_name="full_col", value_name=value_name
        )
        df_melted["main_mode"] = df_melted["full_col"].str.replace(prefix, "", regex=False)
        df_melted = df_melted.rename(columns={"時間帯": "time_slot"})

        df_melted["time_slot"] = df_melted["time_slot"].astype(str).apply(normalize_time_slot)
        df_melted["time_code"] = df_melted["time_slot"].map(time_slot_to_code)
        df_melted["main_mode_code"] = df_melted["main_mode"].apply(
            lambda x: next((v for k, v in MODE7_MAP.items() if k in x), None)
        )
        return df_melted

    df_origin = melt_and_parse(df, origin_cols, "production_trip_count", "発生量（トリップ）_")
    df_dest = melt_and_parse(df, destination_cols, "attraction_trip_count", "集中量（トリップ）_")

    merge_keys = ["地域_code", "地域_name", "地域_type", "main_mode", "main_mode_code", "time_slot", "time_code"]
    df_merged = pd.merge(df_origin, df_dest, on=merge_keys, how="outer")

    df_merged = df_merged.rename(columns={
        "地域_code": "kzone",
        "地域_name": "kzone_name",
        "地域_type": "kzone_type"
    })

    df_merged = df_merged[
        ["kzone", "kzone_name", "kzone_type",
         "main_mode_code", "main_mode", "time_code", "time_slot",
         "production_trip_count", "attraction_trip_count"]
    ]

    return {
        "trip_origin_dest_by_mode_and_time": df_merged
    }
