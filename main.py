import argparse
from pathlib import Path

from core.preprocessing import load_and_clean_excel
from converters import (
    a_1, a_2,
    b_1, b_2, b_3, b_4,
    c_1, c_2, c_3, c_4,
    d_1,
    e_1, e_2, e_3, e_4,
)

# 対応ファイルと変換関数
FILE_MAP = {
    "a-1.xlsx": a_1,
    "a-2.xlsx": a_2,
    "b-1.xlsx": b_1,
    "b-2.xlsx": b_2,
    "b-3.xlsx": b_3,
    "b-4.xlsx": b_4,
    "c-1.xlsx": c_1,
    "c-2.xlsx": c_2,
    "c-3.xlsx": c_3,
    "c-4.xlsx": c_4,
    "d-1.csv": d_1,
    "e-1.xlsx": e_1,
    "e-2.xlsx": e_2,
    "e-3.xlsx": e_3,
    "e-4.xlsx": e_4,
}

def run_conversion(input_dir: Path, output_dir: Path, filenames, dry_run=False):
    for fname in filenames:
        input_path = input_dir / fname
        converter = FILE_MAP.get(fname)

        if converter is None:
            print(f"⚠️ スキップ：未対応ファイル {fname}")
            continue

        print(f"🚀 処理開始: {fname}")

        # load() 関数が存在する場合はそれを使う（例: d-1, e-4）
        if hasattr(converter, "load"):
            df_clean, description = converter.load(input_path)
        else:
            df_clean, description = load_and_clean_excel(input_path)

        tables = converter.convert(df_clean, metadata={"description": description})

        for table_name, df_out in tables.items():
            file_prefix = input_path.stem.replace("-", "")
            output_file = output_dir / f"{file_prefix}_{table_name}.csv"
            if not dry_run:
                df_out.to_csv(output_file, index=False, encoding='utf-8-sig')
                print(f"✅ 保存: {output_file}")
            else:
                print(f"(dry-run) 保存予定: {output_file}")

def main():
    parser = argparse.ArgumentParser(
        description="Convert person trip Excel data to tidy CSV files for PostgreSQL/PostGIS."
    )
    parser.add_argument(
        "--input-dir", "-i", type=Path, default=Path("input"),
        help="Input directory containing Excel/CSV files (default: input/)"
    )
    parser.add_argument(
        "--output-dir", "-o", type=Path, default=Path("output"),
        help="Output directory for CSV files (default: output/)"
    )
    parser.add_argument(
        "--files", "-f", nargs="*", default=list(FILE_MAP.keys()),
        help="Specific files to process (default: all known files)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Only show what would be done, do not write output"
    )

    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    run_conversion(args.input_dir, args.output_dir, args.files, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
