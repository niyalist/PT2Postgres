import pandas as pd
from core.mappings import PURPOSE_MAP
from core.age_utils import parse_age_to_tuple


def convert(df: pd.DataFrame, metadata=None) -> dict[str, pd.DataFrame]:
    """
    b-1.xlsx: 年齢階層別原単位（トリップ数, グロス, ネット）
    - 出力2種: population, purpose_stats
    - 年齢層正規化 + 目的コード付加
    - 地域を分解して kzone_code, name, type を出力に含める
    """
    df.columns = df.columns.str.strip()
    df[["age_group", "age_min", "age_max", "age_median"]] = df["年齢階層"].apply(lambda x: pd.Series(parse_age_to_tuple(x)))

    # rename 地域 → kzone_code など（前処理済みを前提）
    df = df.rename(columns={"性別": "gender"})

    # 列分類
    trip_cols = [c for c in df.columns if c.startswith("トリップ数_")]
    gross_cols = [c for c in df.columns if c.startswith("グロス原単位_")]
    net_cols = [c for c in df.columns if c.startswith("ネット原単位_")]
    pop_cols = ["人口・外出率_居住人口", "人口・外出率_外出人口", "人口・外出率_外出率"]

    id_vars = [
        "地域_code", "地域_name", "地域_type",
        "gender", "年齢階層", "age_group", "age_min", "age_max", "age_median"
    ]

    def melt_values(cols, prefix, value_name):
        df_m = df.melt(id_vars=id_vars, value_vars=cols,
                       var_name="purpose", value_name=value_name)
        df_m["purpose"] = df_m["purpose"].str.replace(f"{prefix}_", "", regex=False)
        return df_m

    trip_df = melt_values(trip_cols, "トリップ数", "trip_count")
    gross_df = melt_values(gross_cols, "グロス原単位", "trips_per_person")
    net_df = melt_values(net_cols, "ネット原単位", "trips_per_mobile_person")

    merged = trip_df.merge(gross_df, on=id_vars + ["purpose"], how="outer")
    merged = merged.merge(net_df, on=id_vars + ["purpose"], how="outer")
    merged["purpose_code"] = merged["purpose"].map(PURPOSE_MAP)

    # 不要な列削除と順序調整
    merged = merged.drop(columns=["年齢階層"])
    merged = merged[[
        "地域_code", "地域_name", "地域_type",
        "gender", "age_group", "age_min", "age_max", "age_median",
        "purpose_code", "purpose", "trip_count", "trips_per_person", "trips_per_mobile_person"
    ]]
    merged = merged.rename(columns={
        "地域_code": "kzone",
        "地域_name": "kzone_name",
        "地域_type": "kzone_type"
    })

    pop_df = df[[
        "地域_code", "地域_name", "地域_type",
        "gender", "age_group", "age_min", "age_max", "age_median"
    ] + pop_cols].copy()

    pop_df = pop_df.rename(columns={
        "地域_code": "kzone",
        "地域_name": "kzone_name",
        "地域_type": "kzone_type",
        "人口・外出率_居住人口": "population",
        "人口・外出率_外出人口": "mobile_population",
        "人口・外出率_外出率": "mobility_rate"
    })

    return {
        "population_by_age_and_gender": pop_df,
        "trip_stats_by_purpose_age_gender": merged
    }
