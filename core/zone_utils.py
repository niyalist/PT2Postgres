import pandas as pd
import re

def split_zone_column(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """
    ゾーン情報を含む1列（例: '地域', '発地', '着地'）を分解し、
    以下の3列を追加する処理を行う：

        - {col}_code : ゾーンコード部分（4桁の数字など）
        - {col}_name : コードに続く名称部分（市区町村名や区分名など）
        - {col}_type : ゾーンの分類を示す種別ラベル（'zone', 'other_zone', 'summary', 'unknown'）

    ▼ 分類ルール：
        - コード部分が4桁の数字のみの場合（例: ':0010', '8700'）
            → 'zone'
        - 名称部分に以下の語を含む場合（例: '（その他）', ' 不明', '圏域外合計', '以下不明'）
            → 'other_zone'
        - 上記に当てはまらず、コードに続いて何らかの名称がある場合（例: '神奈川県', '千葉県'）
            → 'summary'
        - その他、形式に一致しない、または空欄の場合
            → 'unknown'

    ▼ 入力例と処理結果：

        - ':0010 相模原市'
            → code='0010', name='相模原市', type='zone'

        - ':62-- 相模原市（その他）'
            → code='62--', name='相模原市（その他）', type='other_zone'

        - ':9999 不明'
            → code='9999', name='不明', type='other_zone'

        - ':8700 圏域外合計（含不明）'
            → code='8700', name='圏域外合計（含不明）', type='other_zone'

        - ':49-- 千葉県'
            → code='49--', name='千葉県', type='summary'

        - '全体'
            → code='全体', name=None, type='summary'

    Parameters:
        df : pandas.DataFrame
            対象となるデータフレーム
        col : str
            分解対象となるカラム名（例: '地域', '発地', '着地'）

    Returns:
        df : pandas.DataFrame
            入力の df に3列（_code, _name, _type）を追加した新しいデータフレーム
    """
    df = df.copy()

    # 様々な表記の揺れに対応（パターン1に統一）
    # パターン1 前に半角のコロン 例 :0010, :7000 東京区部
    # パターン2 前に全角のコロン 例 ：0010, ：7000 東京区部
    # パターン3 前後に半角のコロン 例 :0010:, :7000:東京区部
    df[col] = (
        df[col]
        .astype(str)
        .str.replace("：", ":", regex=False)                      # 全角コロン → 半角
        .str.replace(r"^:+", "", regex=True)                      # 先頭のコロン1つ以上を除去
        .str.replace(r":+$", "", regex=True)                      # 末尾のコロン1つ以上を除去
        .str.replace(r"(?<=^[\d\-]{4}):", " ", regex=True)        #4桁の数字または-の後のコロンをスペースに置換
        .str.strip()                                              # 前後空白を除去
    )

    def parse(val):
        if pd.isna(val) or val.strip() == "":
            return pd.Series([None, None, "unknown"])
        val = val.lstrip(":").strip()
        match = re.match(r"^([0-9\-]+)\s*(.*)$", val)
        if match:
            code = match.group(1).strip()
            name = match.group(2).strip() or None

            if re.fullmatch(r"\d{4}", code) and (not name or pd.isna(name)):
                zone_type = "zone"
            elif name and any(kw in name for kw in ["（その他）", "不明", "圏域外合計", "以下不明"]):
                zone_type = "other_zone"
            else:
                zone_type = "summary"
        else:
            code, name, zone_type = val, None, "unknown"
        return pd.Series([code, name, zone_type])

    df[[f"{col}_code", f"{col}_name", f"{col}_type"]] = df[col].apply(parse)
    return df

