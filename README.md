# PT2Postgres

**PT2Postgres** は、全国パーソントリップ調査のExcel/CSV形式の集計データを、PostgreSQLやGISツールで扱いやすい**tidyなCSV形式に変換**するためのスクリプト群です。  
主に、交通・都市計画・モビリティ研究などでのデータ整備・分析作業を効率化することを目的としています。

---

## 📂 構成

- `main.py` — 一括変換スクリプト
- `converters/` — 各調査表 (a-1 〜 e-4) に対応した変換処理
- `core/` — 共通の前処理・マスタ定義（目的コード、交通手段など）
- `input/` — 元データ（Excel, CSV）を配置（※配布されていません）
- `output/` — 変換結果が保存されます（`*.csv`）

---

## ✅ 対応している調査項目

| ファイル名 | 内容 |
|------------|------|
| `a1_population_by_age_and_gender.csv` | 年齢・性別別人口 |
| `a2_population_by_employment_type.csv` | 就業形態別人口 |
| `b1_trip_stats_by_purpose_age_gender.csv` | 原単位（性別・年齢階層別） |
| `b2_trip_stats_by_purpose_employment_age.csv` | 原単位（就業・年齢階層別） |
| `b3_trip_count_by_vehicle_and_purpose.csv` | 車種別トリップ数 |
| `b4_population_by_time_slot.csv` | 時間帯別滞留人口 |
| `c1_trip_origin_dest_by_mode_and_purpose.csv` | O/D別 代表手段・目的別発着トリップ |
| `c2_trip_origin_dest_by_time_and_purpose.csv` | O/D別 時間帯・目的別発着トリップ |
| `c3_trip_origin_dest_by_mode_and_time.csv` | O/D別 手段・時間帯別発着トリップ |
| `c4_trip_origin_dest_by_facility_and_mode.csv` | O/D別 施設・手段別発着トリップ |
| `d1_trip_od_by_purpose_and_mode.csv` | O/Dマトリクス（目的×手段別） |
| `e1_trip_by_station_and_terminal_mode.csv` | 鉄道駅端末手段別トリップ数 |
| `e2_mean_travel_time_by_mode_and_od.csv` | ゾーン間平均所要時間（代表手段別） |
| `e3_parking_count_by_location_and_purpose.csv` | 駐車場所台数（目的別） |
| `e4_zone_code_to_area_lookup.csv` | ゾーンコード ↔ 地域名称対応表 |

---

## 🚀 使い方

```bash
python3 main.py \
  --input-dir input \
  --output-dir output \
  --files a-1.xlsx b-1.xlsx d-1.csv

