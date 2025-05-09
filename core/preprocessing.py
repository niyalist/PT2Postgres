import pandas as pd
from pathlib import Path
from typing import Tuple

# 同一ディレクトリ内の他モジュールからのインポート
from .zone_utils import split_zone_column
from .filters import filter_summary_rows, filter_summary_columns, filter_summary_zones

def load_and_clean_excel(filepath: Path):
    df = pd.read_excel(filepath, header=None)

    data_description, description_column_index = _detect_description_column(df)
    df = df.iloc[:, description_column_index:]

    header_start = _detect_header_row(df)
    header_labels = _build_header(df, header_start)

    data_start = header_start + 2
    df_data = df.iloc[data_start:].copy()
    df_data.columns = header_labels

    # 地域・ゾーン系列に対して split_zone_column を適用
    for col in ['地域', '発ゾーン', '着ゾーン', '発地', '着地']:
        if col in df_data.columns:
            df_data = split_zone_column(df_data, col)

    df_data_filtered = filter_summary_rows(df_data)
    df_data_filtered = filter_summary_columns(df_data_filtered)
    df_data_filtered = filter_summary_zones(df_data_filtered)

    return df_data_filtered, data_description


def _detect_description_column(df: pd.DataFrame) -> Tuple[str, int]:
    desc_row = df.iloc[0]
    for i, cell in enumerate(desc_row):
        if pd.notna(cell) and str(cell).strip():
            return str(cell).strip(), i
    raise ValueError("有効なデータ説明が見つかりません")


def _detect_header_row(df: pd.DataFrame, max_rows: int = 10) -> int:
    for i in range(1, max_rows):
        if df.iloc[i].notna().sum() > 0 and df.iloc[i + 1].notna().sum() > 0:
            return i
    raise ValueError("2行連続の有効なヘッダー行が見つかりません")


def _build_header(df: pd.DataFrame, header_start: int) -> list[str]:
    multi_headers = df.iloc[header_start:header_start + 2].ffill(axis=1)
    header_labels = []
    for i, col_pair in enumerate(zip(*multi_headers.values)):
        parts = [str(p).strip() for p in col_pair if pd.notna(p) and str(p).strip().lower() != 'nan']
        combined = '_'.join(parts)
        header_labels.append(combined if combined else f"hidden_{chr(65 + i)}")
    return header_labels


