import pandas as pd
from core.mappings import MODE13_MAP

def convert(df: pd.DataFrame, metadata=None) -> dict[str, pd.DataFrame]:
    """
    E-1: 鉄道駅別・乗降別・端末交通手段別トリップ数
    - 駅コードと駅名を分離
    - 各交通手段について、トリップ数と構成比（％）を縦持ち化
    - mode_code（13区分）を付与
    """
    df = df.copy()

    # 駅コード・名称分離
    df[['station_code', 'station_name']] = df['鉄道駅'].str.split(':', expand=True)

    records = []
    for _, row in df.iterrows():
        for mode in MODE13_MAP:
            trip_count = row.get("トリップ数_" + mode)
            mode_share = row.get("構成比（％）_" + mode)

            records.append({
                "station_code": row.station_code,
                "station_name": row.station_name,
                "boarding_type": row["乗車／降車"],
                "mode_code": MODE13_MAP[mode],
                "mode": mode,
                "trip_count": trip_count,
                "mode_share_percent": mode_share
            })

    df_out = pd.DataFrame.from_records(records)
    return {
        "trip_by_station_and_terminal_mode": df_out
    }
