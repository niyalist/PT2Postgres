import pandas as pd

def filter_summary_rows(df: pd.DataFrame) -> pd.DataFrame:
    aggregation_keywords = ['合計', '計', '乗降計']
    exception_keyword = '圏域外合計'
    columns_to_check = df.columns[:5]

    def no_aggregation_keywords(row):
        has_exception = False
        has_summary_term = False
        for col in columns_to_check:
            val = str(row.get(col, ""))
            if exception_keyword in val:
                has_exception = True  # 「圏域外合計」が含まれる行は除外しない
            if any(keyword in val for keyword in aggregation_keywords) and not exception_keyword in val:
                has_summary_term = True
        if has_exception and not has_summary_term:
            return True
        if has_summary_term:
            return False
        return True

    condition_no_keywords = df.apply(no_aggregation_keywords, axis=1)
    return df[condition_no_keywords].copy()


def filter_summary_columns(df: pd.DataFrame) -> pd.DataFrame:
    columns_to_drop = [
        col for col in df.columns
        if str(col).endswith(('_計', '_合計', '_乗降計'))
    ]
    return df.drop(columns=columns_to_drop).copy()

def filter_summary_zones(df:pd.DataFrame) -> pd.DataFrame:
    # zone_type が summary の行を削除
    df = df.copy()
    if any(col.endswith("_type") for col in df.columns):
        zone_type_cols = [c for c in df.columns if c.endswith("_type")]
        for ztc in zone_type_cols:
            df = df[df[ztc] != "summary"]
    return df