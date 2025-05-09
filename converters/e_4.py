import pandas as pd
from pathlib import Path

def load(path: Path) -> pd.DataFrame:
    """
    e-4.xlsx の 2〜6 番目のシートを読み込み、0・1行目を結合したヘッダーを適用してから結合する。
    """
    xls = pd.ExcelFile(path)
    target_sheets = xls.sheet_names[1:]  # 2番以降のシートを使用

    dfs = []
    for sheet in target_sheets:
        tmp = pd.read_excel(xls, sheet_name=sheet, header=None)
        # 0・1行目を結合したヘッダを作成
        header = [
            f"{str(a).strip()}_{str(b).strip()}" if pd.notna(a) and pd.notna(b)
            else str(a).strip() if pd.notna(a)
            else str(b).strip()
            for a, b in zip(tmp.iloc[1], tmp.iloc[2])
        ]
        df_body = tmp.iloc[3:].copy()
        df_body.columns = header
        #都道府県名を設定（シート名が都道府県名）
        df_body['prefecture'] = sheet
        dfs.append(df_body)

    return pd.concat(dfs, ignore_index=True), "ゾーンコード表"

def convert(df: pd.DataFrame, metadata=None) -> dict[str, pd.DataFrame]:
    """
    ゾーンコードに関する階層情報を持つ市区町村対応表を整形する
    - lzone: 大ゾーン
    - mzone: 中ゾーン
    - kzone: 計画ゾーン（kzone）
    - szone: 小ゾーン
    """
    df = df.copy()

    # 欠損値除去と型変換
    df = df.dropna(subset=["ゾーンコード_大", "中", "計", "小"])
    df[["ゾーンコード_大", "中", "計", "小"]] = df[["ゾーンコード_大", "中", "計", "小"]].astype(int)

    # 桁結合
    df["lzone"] = df["ゾーンコード_大"].astype(str).str.zfill(2)
    df["mzone"] = df["lzone"] + df["中"].astype(str)
    df["kzone"] = df["mzone"] + df["計"].astype(str)
    df["szone"] = df["kzone"] + df["小"].astype(str)

    # カラム整備
    df = df.rename(columns={
        "市区町村": "municipality",
        "該当町丁・字名": "local_area_names"
    })

    df_out = df[["lzone", "mzone", "kzone", "szone", "prefecture", "municipality", "local_area_names"]].copy()

    return {
        "zone_code_to_area_lookup": df_out
    }
