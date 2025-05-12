import platform
from pathlib import Path

OUTPUT_DIR = Path("output")
SCHEMA_NAME = "pt2018"
SCRIPT_PATH = Path("schemas/02_copy_all_data.sql")

def generate_copy_commands():
    system = platform.system()
    if system == "Windows":
        command_template = 'type "{path}"'  # Windows 用
    else:
        command_template = "cat {path}"     # macOS / Linux 用

    csv_files = sorted(OUTPUT_DIR.glob("*.csv"))
    lines = [
        "-- Auto-generated COPY commands (OS-aware absolute path version)",
        "-- NOTE: Run this script from the project root directory.",
        "--       On Windows, this uses `type`; on macOS/Linux, it uses `cat`.",
        "\\set ON_ERROR_STOP on",
        f"SET search_path TO {SCHEMA_NAME};",
        "",
    ]

    for csv_file in csv_files:
        abs_path = csv_file.resolve()
        if system == "Windows":
            # Windows の COPY はバックスラッシュで指定（PostgreSQLは"で囲む必要あり）
            formatted_path = str(abs_path).replace("/", "\\")
        else:
            formatted_path = abs_path.as_posix()

        table = csv_file.stem
        cmd = command_template.format(path=formatted_path)
        lines.append(
            f"COPY {table} FROM PROGRAM '{cmd}' "
            "WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');"
        )

    SCRIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
    SCRIPT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ COPY commands saved to: {SCRIPT_PATH}")
    print(f"📦 Detected OS: {system}")

if __name__ == "__main__":
    generate_copy_commands()
