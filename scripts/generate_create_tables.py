import pandas as pd
from pathlib import Path

# 優先的に使う型マッピング
FORCED_COLUMN_TYPES = {
    "lzone": "TEXT",
    "mzone": "TEXT",
    "kzone": "TEXT",
    "szone": "TEXT",
    "origin_kzone": "TEXT",
    "destination_kzone": "TEXT",
    "mobility_rate": "REAL",
    "mode_share_percent": "REAL",
    "trip_count": "INTEGER",
    "trips_per_person": "REAL",
    "trips_per_mobile_person": "REAL"
}

# スキーマ名（明示）
SCHEMA_NAME = "pt2018"
#SCHEMA_NAME = "public"  #このように指定することでpublic スキーマに所属することになる


# このスクリプトの位置からの基準パスを定義
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"
SCHEMA_DIR = BASE_DIR / "schemas/sql"
COMBINED_FILE = BASE_DIR / "schemas/create_all_tables.sql"

def infer_sql_type(value):
    try:
        float_val = float(value)
        return "INTEGER" if float_val.is_integer() else "REAL"
    except:
        return "TEXT"

def infer_column_types(csv_path: Path, sample_size=100):
    df = pd.read_csv(csv_path, encoding="utf-8-sig", nrows=sample_size)
    types = {}
    for col in df.columns:
        if col in FORCED_COLUMN_TYPES:
            types[col] = FORCED_COLUMN_TYPES[col]
        else:
            first_valid = df[col].dropna().astype(str).str.strip().replace("", pd.NA).dropna()
            types[col] = infer_sql_type(first_valid.iloc[0]) if not first_valid.empty else "TEXT"
    return types

def generate_create_table_statement(table_name: str, column_types: dict) -> str:
    full_table_name = f"{SCHEMA_NAME}.{table_name}"
    cols = [f'"{col}" {dtype}' for col, dtype in column_types.items()]
    return f'CREATE TABLE {full_table_name} (\n    ' + ',\n    '.join(cols) + '\n);'

def main():
    SCHEMA_DIR.mkdir(parents=True, exist_ok=True)
    COMBINED_FILE.parent.mkdir(parents=True, exist_ok=True)

    include_lines = []

    for csv_file in sorted(OUTPUT_DIR.glob("*.csv")):
        table_name = csv_file.stem
        column_types = infer_column_types(csv_file)
        statement = generate_create_table_statement(table_name, column_types)

        sql_path = SCHEMA_DIR / f"{table_name}.sql"
        with open(sql_path, "w", encoding="utf-8") as f:
            f.write("-- Auto-generated CREATE TABLE statement\n")
            f.write(statement + "\n")

        include_lines.append(f"\\i schemas/sql/{table_name}.sql")

    with open(COMBINED_FILE, "w", encoding="utf-8") as f:
        f.write("-- Run this with psql to create all tables\n\n")
        f.write(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME};\n")
        f.write("\n".join(include_lines))

if __name__ == "__main__":
    main()
