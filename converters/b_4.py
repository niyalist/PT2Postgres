import pandas as pd
from core.time_utils import normalize_time_slot, time_slot_to_code



def convert(df: pd.DataFrame, metadata=None) -> dict[str, pd.DataFrame]:
    df.columns = df.columns.str.strip()
    df = df.rename(columns={
        "地域_code": "kzone",
        "地域_name": "kzone_name",
        "地域_type": "kzone_type"
    })

    # 時間帯の列（"時刻_"から始まる列 or "不明"列も含める）より堅牢な time_columns 抽出
    time_columns = [col for col in df.columns if col.startswith("時刻_")]


    # melt で縦持ちに
    df_melted = df.melt(
        id_vars=["kzone", "kzone_name", "kzone_type"],
        value_vars=time_columns,
        var_name="time_slot_raw",
        value_name="population"
    )

    # time_slot を加工：接頭辞除去 + 全角→半角
    # "時刻_～3時台" → "～3時台"
    df_melted["time_slot"] = (
        df_melted["time_slot_raw"]
        .astype(str)
        .str.replace(r"^.*?_", "", regex=True)  # アンダースコア以降を残す
        .apply(normalize_time_slot)             # 全角→半角、strip
    )

    df_melted["time_code"] = df_melted["time_slot"].apply(time_slot_to_code)

    # 列順指定
    df_out = df_melted[[
        "kzone", "kzone_name", "kzone_type",
        "time_code", "time_slot", "population"
    ]]

    return {
        "population_by_time_slot": df_out
    }
