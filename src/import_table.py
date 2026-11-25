import sqlite3
from pathlib import Path
import pandas as pd


def import_csvs_to_sqlite(csv_dir: str, db_path: str, tables: list[str], if_exists: str = "replace"):
    input_path = Path(csv_dir)
    conn = sqlite3.connect(db_path)

    try:
        for table in tables:
            csv_file = input_path / f"{table}.csv"
            print(f"Importing {table}...")

            df = pd.read_csv(csv_file, encoding="utf-8")
            df.to_sql(
                table,
                conn,
                if_exists=if_exists,  # 'replace' or 'append'
                index=False,
                chunksize=5000,
            )

            print(f"Loaded {len(df)} rows into '{table}'.")

        conn.commit()
        print("Done.")
    finally:
        conn.close()


if __name__ == "__main__":
    CSV_FOLDER = "../data"
    TARGET_DB = "../test/sample.db"

    TABLES = [
        "affiliation",
        "author",
        "publication",
        "series",
        "author_affiliation",
        "author_publication",
        "author_series",
        "publication_series",
    ]

    import_csvs_to_sqlite(CSV_FOLDER, TARGET_DB, TABLES,if_exists="replace")