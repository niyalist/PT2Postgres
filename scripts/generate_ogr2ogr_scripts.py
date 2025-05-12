import argparse
from pathlib import Path
from urllib.parse import urlparse

def make_pg_connection_string(pgurl: str, schema: str) -> str:
    url = urlparse(pgurl)
    user = url.username or ""
    password = url.password or ""
    host = url.hostname or "localhost"
    port = url.port or 5432
    dbname = url.path.lstrip("/")  # remove leading /

    parts = [
        f'dbname={dbname}',
        f'user={user}',
        f'host={host}',
        f'port={port}',
        f'active_schema={schema}'
    ]
    if password:
        parts.insert(2, f'password={password}')

    return 'PG:"' + ' '.join(parts) + '"'

def generate_script(ogr2ogr_path, pg_str, shape_file, table_name, srs_src, srs_dst, platform):
    ogr_cmd = f'"{ogr2ogr_path}"' if platform == 'windows' else ogr2ogr_path
    shape_path = f"{shape_file}.shp"

    return (
        f'{ogr_cmd} -f "PostgreSQL" {pg_str} "{shape_path}" '
        f'-nln {table_name} -nlt PROMOTE_TO_MULTI '
        f'-lco GEOMETRY_NAME=geom -lco FID=gid -lco PRECISION=NO '
        f'-t_srs EPSG:{srs_dst} -s_srs EPSG:{srs_src} -overwrite'
    )

def write_postprocess_sql(path: Path):
    sql = """\
-- Validate geometries
UPDATE pt2018.kzone
SET geom = ST_CollectionExtract(ST_MakeValid(geom), 3)
WHERE NOT ST_IsValid(geom);

UPDATE pt2018.szone
SET geom = ST_CollectionExtract(ST_MakeValid(geom), 3)
WHERE NOT ST_IsValid(geom);


-- Convert integer IDs to 4-digit zero-padded text
ALTER TABLE pt2018.kzone
  ALTER COLUMN kzone TYPE text;
UPDATE pt2018.kzone
SET kzone = LPAD(kzone, 4, '0');

ALTER TABLE pt2018.szone
  ALTER COLUMN szone TYPE text;
UPDATE pt2018.szone
SET szone = LPAD(szone, 5, '0');
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(sql, encoding="utf-8")
    print(f"✅ Generated: {path}")

def main():
    parser = argparse.ArgumentParser(description="Generate ogr2ogr and postprocess SQL scripts for PT2Postgres project")
    parser.add_argument("--pgurl", required=True, help="PostgreSQL connection string (URL format)")
    parser.add_argument("--ogr2ogr", default="ogr2ogr", help="Path to ogr2ogr binary (default: use from PATH)")
    parser.add_argument("--shape-dir", default="input/H30_gis", help="Directory containing shapefiles (default: input/H30_gis)")
    parser.add_argument("--schema", default="pt2018", help="PostgreSQL schema name (default: pt2018)")
    args = parser.parse_args()

    srs_src = 6677  # JGD2011 / Japan Plane Rectangular CS IX
    srs_dst = 4326  # WGS84

    pg_str = make_pg_connection_string(args.pgurl, args.schema)

    shapes = {
        "H30_szone": "szone",
        "H30_kzone": "kzone",
    }

    for platform in ("unix", "windows"):
        lines = []
        for filename, tablename in shapes.items():
            shp_path = Path(args.shape_dir) / filename
            cmd = generate_script(args.ogr2ogr, pg_str, shp_path, tablename, srs_src, srs_dst, platform)
            lines.append(cmd)

        out_filename = f"import_shape_{platform}.{'sh' if platform == 'unix' else 'bat'}"
        with open(out_filename, "w", encoding="utf-8") as f:
            f.write("#!/bin/bash\n\n" if platform == "unix" else "@echo off\n\n")
            for line in lines:
                f.write(line + "\n")
        print(f"✅ Generated: {out_filename}")

    # Generate postprocess SQL
    write_postprocess_sql(Path("schemas/03_postprocess_zones.sql"))

if __name__ == "__main__":
    main()
