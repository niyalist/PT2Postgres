import pandas as pd
from core.age_utils import parse_age_to_tuple

def convert(df: pd.DataFrame, metadata=None) -> dict[str, pd.DataFrame]:
    """
    a-1.xlsx: 居住地ゾーン別・性別・年齢階層別人口
    - 年齢階層列を縦持ちに変換
    - 年齢階層を '5-9' の形式に正規化し、min/max/medianも追加
    - 年齢階層85〜 は、85+という形式に変換し、仮に85-90の幅としてmin/max/medianを設定
    - 地域_code → kzone, 地域_name, 地域_type も含めて出力
    """

    age_columns = [col for col in df.columns if str(col).startswith("年齢階層_")]

    df_melted = df.melt(
        id_vars=["地域_code", "地域_name", "地域_type", "性別"],
        value_vars=age_columns,
        var_name="年齢階層",
        value_name="人口"
    )

    # 共通関数に置き換え
    df_melted[["age_group", "age_min", "age_max", "age_median"]] = df_melted["年齢階層"].apply(
        lambda x: pd.Series(parse_age_to_tuple(x))
    )

    df_out = df_melted.rename(columns={
        "地域_code": "kzone",
        "地域_name": "kzone_name",
        "地域_type": "kzone_type",
        "性別": "gender",
        "人口": "population"
    })[
        ["kzone", "kzone_name", "kzone_type", "gender", "age_group", "age_min", "age_max", "age_median", "population"]
    ]

    return {
        "population_by_age_and_gender": df_out
    }
