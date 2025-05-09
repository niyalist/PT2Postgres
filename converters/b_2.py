import pandas as pd
from core.mappings import EMPLOYMENT_TYPE_MAP, PURPOSE_MAP
from core.age_utils import parse_age_to_tuple


def convert(df: pd.DataFrame, metadata=None) -> dict[str, pd.DataFrame]:
    df.columns = df.columns.str.strip()
    df = df.rename(columns={"地域_code": "kzone", "地域_name": "kzone_name", "地域_type": "kzone_type",
                             "就業": "employment_type", "年齢": "age"})

    df[["age_group", "age_min", "age_max", "age_median"]] = df["age"].apply(lambda x: pd.Series(parse_age_to_tuple(x)))

    # employment_type に合わせて表記を変換してからコード割当（"その他、就業状態詳細不明" → "その他"）し、その後戻す
    df["employment_type"] = df["employment_type"].replace({"その他、就業状態詳細不明": "その他"})
    # 就業形態コード付与
    df["employment_type_code"] = df["employment_type"].map(EMPLOYMENT_TYPE_MAP)
    df["employment_type"] = df["employment_type"].replace({"その他": "その他、就業状態詳細不明"})

    # 列分類
    trip_cols = [c for c in df.columns if c.startswith("トリップ数_")]
    gross_cols = [c for c in df.columns if c.startswith("グロス原単位_")]
    net_cols = [c for c in df.columns if c.startswith("ネット原単位_")]
    pop_cols = ["人口・外出率_居住人口", "人口・外出率_外出人口", "人口・外出率_外出率"]

    id_vars = ["kzone", "kzone_name", "kzone_type",
               "employment_type", "employment_type_code",
               "age_group", "age_min", "age_max", "age_median"]

    def melt_values(cols, prefix, value_name):
        df_m = df.melt(id_vars=id_vars, value_vars=cols,
                       var_name="purpose", value_name=value_name)
        df_m["purpose"] = df_m["purpose"].str.replace(f"{prefix}_", "", regex=False)
        return df_m

    trip_df = melt_values(trip_cols, "トリップ数", "trip_count")
    gross_df = melt_values(gross_cols, "グロス原単位", "trips_per_person")
    net_df = melt_values(net_cols, "ネット原単位", "trips_per_mobile_person")

    # マージ
    merged = trip_df.merge(gross_df, on=id_vars + ["purpose"], how="outer")
    merged = merged.merge(net_df, on=id_vars + ["purpose"], how="outer")
    merged["purpose_code"] = merged["purpose"].map(PURPOSE_MAP)

    # 並び順を整える
    merged = merged[[
        "kzone", "kzone_name", "kzone_type",
        "employment_type_code", "employment_type",
        "age_group", "age_min", "age_max", "age_median",
        "purpose_code", "purpose",
        "trip_count", "trips_per_person", "trips_per_mobile_person"
    ]]

    # population系
    pop_df = df[[
        "kzone", "kzone_name", "kzone_type",
        "employment_type_code", "employment_type",
        "age_group", "age_min", "age_max", "age_median"
    ] + pop_cols].copy()

    pop_df = pop_df.rename(columns={
        "人口・外出率_居住人口": "population",
        "人口・外出率_外出人口": "mobile_population",
        "人口・外出率_外出率": "mobility_rate"
    })

    return {
        "population_by_employment_age": pop_df,
        "trip_stats_by_purpose_employment_age": merged
    }
