import argparse
from pathlib import Path
import pandas as pd
import psycopg2
from sqlalchemy import create_engine

def load_csv_to_table(engine, csv_path: Path, table_name: str):
    print(f"📥 Loading {csv_path} into table {table_name}...")
    df = pd.read_csv(csv_path)
    df.to_sql(table_name, engine, if_exists='replace', index=False)
    print(f"✅ Done: {table_name}")

def main():
    parser = argparse.ArgumentParser(description="Load CSVs into PostgreSQL")
    parser.add_argument("--input-dir", "-i", type=Path, default=Path("output"), help="Directory containing CSVs")
    parser.add_argument("--db-url", "-d", required=True, help="Database URL (e.g., postgresql://user:pass@host/dbname)")
    parser.add_argument("--dry-run", action="store_true", help="Preview only, do not load")
    args = parser.parse_args()

    engine = create_engine(args.db_url)

    for csv_file in sorted(args.input_dir.glob("*.csv")):
        table_name = csv_file.stem
        if args.dry_run:
            print(f"(dry-run) Would load {csv_file} into {table_name}")
        else:
            load_csv_to_table(engine, csv_file, table_name)

if __name__ == "__main__":
    main()
