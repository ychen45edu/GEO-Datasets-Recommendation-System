import os
import sqlite3
import pandas as pd
import item_item_matrix as iim_5f


class LargeScale5Features:
    """
    Manages author dataset loading from pre-split CSVs, SQLite metadata retrieval,
    and pairwise similarity scoring for a single author.
    """

    def __init__(self, author_id, db_path="sample.db"):
        """
        Initializes the scorer for a specific author.

        Args:
            author_id (str | int): Target author identifier.
            db_path (str): Path to the SQLite database containing the `series` table.
        """
        self.id = str(author_id).strip()
        self.db_path = db_path

    def _read_and_filter_csv(self, csv_path, only_true_labels=False):
        """
        Loads a split CSV, filters for `self.id`, and deduplicates `gse_id` rows.

        Args:
            csv_path (str): Path to `train.csv` or `test.csv`.
            only_true_labels (bool): If True and a `label` column exists, retains
                only rows where `label` equals 'TRUE' (case-insensitive).

        Returns:
            pd.DataFrame: Filtered and deduplicated subset for `self.id`.
        """
        df = pd.read_csv(csv_path)
        df["author_id"] = df["author_id"].astype(str).str.strip()
        sub = df[df["author_id"] == self.id].copy()

        # Keep only verified positive examples when loading training data
        if only_true_labels and "label" in sub.columns:
            sub = sub[sub["label"].astype(str).str.strip().str.upper() == "TRUE"]

        sub["gse_id"] = sub["gse_id"].astype(str).str.strip()
        return sub.drop_duplicates(subset=["gse_id"])

    def load_train_test_from_csv(self, train_csv_path="train.csv", test_csv_path="test.csv"):
        """
        Extracts deduplicated train/test series lists and ground-truth test labels.

        Args:
            train_csv_path (str): Path to the training split CSV.
            test_csv_path (str): Path to the testing split CSV.

        Returns:
            tuple[list[str], list[str], dict[str, bool]]:
                - `train_ls`: Positive training `gse_id` list.
                - `test_ls`: Candidate testing `gse_id` list.
                - `test_label_map`: Mapping of test `gse_id` -> boolean ground truth.
        """
        train_sub = self._read_and_filter_csv(train_csv_path, only_true_labels=True)
        test_sub = self._read_and_filter_csv(test_csv_path, only_true_labels=False)

        # Build lookup dictionary for ground-truth test labels if available
        test_label_map = {}
        if "label" in test_sub.columns:
            bool_labels = test_sub["label"].astype(str).str.strip().str.upper() == "TRUE"
            test_label_map = dict(zip(test_sub["gse_id"], bool_labels))

        return train_sub["gse_id"].tolist(), test_sub["gse_id"].tolist(), test_label_map

    def fetch_series_metadata(self, gse_ids):
        """
        Fetches metadata for all required series IDs in a single SQL query
        to avoid repeated database round-trips inside nested pair loops.

        Args:
            gse_ids (list[str]): Combined list of train and test GEO Series IDs.

        Returns:
            dict[str, dict]: Mapping of `series_id` -> metadata dict with keys
                `series_id`, `title`, `organism`, `experiment`, `summary`, `design`.
        """
        unique_ids = list(set(gse_ids))
        if not unique_ids:
            return {}

        placeholders = ",".join("?" for _ in unique_ids)
        sql = f"""
            SELECT series_id, title, organism, experiment, summary, design
            FROM series
            WHERE series_id IN ({placeholders})
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(sql, unique_ids).fetchall()

        return {row["series_id"]: dict(row) for row in rows}

    @staticmethod
    def calculate_pair_scores(train_meta, test_meta):
        """
        Computes 5-feature and 3-feature similarity aggregations on scalar values.

        Args:
            train_meta (dict): Metadata dictionary for the training series.
            test_meta (dict): Metadata dictionary for the testing series.

        Returns:
            dict[str, float]: Dictionary containing `5f_min_scores`, `5f_max_scores`,
                `5f_avg_scores`, `3f_avg_scores`, `3f_min_scores`, and `3f_max_scores`.
        """
        # Individual field-level text similarities
        exp_score = iim_5f.similarity_exp(train_meta["experiment"], test_meta["experiment"])
        org_score = iim_5f.similarity_organism(train_meta["organism"], test_meta["organism"])
        sum_score = iim_5f.similarity(train_meta["summary"], test_meta["summary"])
        des_score = iim_5f.similarity(train_meta["design"], test_meta["design"])
        tit_score = iim_5f.similarity(train_meta["title"], test_meta["title"])

        # 3-feature core subset vs. full 5-feature set
        scores_3f = (exp_score, org_score, sum_score)
        scores_5f = (*scores_3f, des_score, tit_score)

        return {
            "5f_min_scores": min(scores_5f),
            "5f_max_scores": max(scores_5f),
            "5f_avg_scores": sum(scores_5f) / 5.0,
            "3f_avg_scores": sum(scores_3f) / 3.0,
            "3f_min_scores": min(scores_3f),
            "3f_max_scores": max(scores_3f),
        }


def compute_all_pairs_df(author_id, database_path="sample.db",train_csv_path="train.csv", test_csv_path="test.csv"):
    """
    Evaluates all (test_id, train_id) pairs for a single author and compiles
    similarity scores and labels into a DataFrame.

    Args:
        author_id (str | int): Target author identifier.
        train_csv_path (str): Path to `train.csv`.
        test_csv_path (str): Path to `test.csv`.

    Returns:
        pd.DataFrame: Pairwise similarity table with `author_id` and boolean `label`.
    """
    pipeline = LargeScale5Features(author_id,database_path)
    train_ls, test_ls, test_label_map = pipeline.load_train_test_from_csv(train_csv_path, test_csv_path)
    metadata_map = pipeline.fetch_series_metadata(train_ls + test_ls)

    print(f"Calculating similarities for {len(train_ls)} train series against {len(test_ls)} test series...")
    results = []

    # Compute Cartesian product of test candidates against known positive train series
    for gseid_test in test_ls:
        test_meta = metadata_map.get(gseid_test)
        for gseid_train in train_ls:
            train_meta = metadata_map.get(gseid_train)
            if not train_meta or not test_meta:
                print(f"[WARN] Missing series metadata in sample.db for pair ({gseid_train}, {gseid_test}); skipping.")
                continue

            row = {"train": gseid_train, "test": gseid_test}
            row.update(pipeline.calculate_pair_scores(train_meta, test_meta))
            results.append(row)

    df = pd.DataFrame(results)
    df["author_id"] = pipeline.id
    df["label"] = df["test"].map(test_label_map).fillna(False).astype(bool) if not df.empty else pd.Series(dtype=bool)
    return df


def generate_recommendation_csv(author_id, output_dir, database_path="sample.db",train_csv_path="train.csv", test_csv_path="test.csv"):
    """
    Generates and exports `{output_dir}/{author_id}.csv` for a single author.

    Args:
        author_id (str | int): Target author identifier.
        output_dir (str): Destination directory for output CSV files.
        train_csv_path (str): Path to `train.csv`.
        test_csv_path (str): Path to `test.csv`.

    Returns:
        str: Path to the exported CSV file.
    """
    author_id_str = str(author_id).strip()
    print(f"\n[INFO] Starting recommendation workflow for Author ID: {author_id_str}")

    os.makedirs(output_dir, exist_ok=True)
    df = compute_all_pairs_df(author_id_str, database_path,train_csv_path, test_csv_path)

    output_file = os.path.join(output_dir, f"{author_id_str}.csv")
    df.to_csv(output_file, index=False)

    print(f"[SUCCESS] Recommendation table exported with {len(df)} rows.")
    print(f"[FILE] Saved to: {os.path.abspath(output_file)}\n")
    return output_file


def get_unique_authors(train_csv_path="train.csv"):
    """
    Extracts a clean, deduplicated list of all `author_id` values from `train.csv`.
    Reads only the `author_id` column to minimize memory usage.

    Args:
        train_csv_path (str): Path to `train.csv`.

    Returns:
        list[str]: Unique author ID strings in order of appearance.
    """
    df = pd.read_csv(train_csv_path, usecols=["author_id"])
    return (
        df["author_id"]
        .dropna()
        .astype(str)
        .str.strip()
        .drop_duplicates()
        .tolist()
    )

def compute_sim(output_dir,train_csv_path,test_csv_path,database_path):
    # Batch-process every unique author found in train.csv
    author_ids = get_unique_authors(train_csv_path)
    if author_ids:
        print(f"[INFO] Found {len(author_ids)} unique authors. Starting batch generation...")
        for idx, author_id in enumerate(author_ids, start=1):
            print(f"[INFO] Processing author {idx}/{len(author_ids)}: {author_id}")
            generate_recommendation_csv(
                author_id,
                output_dir,
                database_path,
                train_csv_path=train_csv_path,
                test_csv_path=test_csv_path,
            )
    else:
        print("[ERROR] No valid author_ids found in train.csv.")


if __name__ == "__main__":
    compute_sim(output_dir = "../test",
                   train_csv_path = "../data/train_test/historical_set.csv",
                   test_csv_path = "../data/train_test/test_set.csv",
                   database_path="../test/sample.db")