import os
import sys
import random
import sqlite3
import pandas as pd
from sklearn.model_selection import train_test_split
from bs4 import BeautifulSoup

import item_item_matrix as iim_5f
import gse_pmid_contact_author as ecp
import Author_Extraction as ae



def split_train_test(df,test_p=0.3):
    """Splits author series dataframe into train and test subsets """
    train_df, test_df = train_test_split(df, test_size=test_p,random_state=42)
    return train_df.reset_index(drop=True), test_df.reset_index(drop=True)


# Contact Author Email
def contact_email(soup):
    try:
        mail = soup.find('td',string='E-mail(s)').parent
        mail_text= mail.find('a').contents[0]
        return (mail_text)
    except:
        return ""

def load_soups(item, pmid):
    """Load and parse HTML soup objects for a GSE item and a PubMed ID."""
    gse_path = "./github/data/raw/gse/"
    pm_path = "./github/data/raw/pubmed/"

    with open(f"{gse_path}{item}.txt", encoding="utf-8") as fp:
        soup_gse = BeautifulSoup(fp, "html.parser")

    with open(f"{pm_path}{pmid}.txt", encoding="utf-8") as fp:
        soup_pm = BeautifulSoup(fp, "html.parser")

    return soup_gse, soup_pm

def author_count(soup):
    author_ls_soup=soup.find(class_="authors-list")
    data_label_ls=re.findall("data-ga-label", str(author_ls_soup))
    num_author=len(data_label_ls)
    return num_author


class large_scale_5_features:
    """Manages author dataset extraction, random candidate sampling, and similarity calculations."""
    def __init__(self, author_id):
        self.conn = sqlite3.connect("sample.db")
        self.cur = self.conn.cursor()
        self.id = author_id

    def close_conn(self):
        """Closes active SQLite connection."""
        self.cur.close()
        self.conn.close()

    def ds_ls(self):
        """Fetches series associated with the current author."""
        sql_com = """ 
            SELECT series_id, author_id
            FROM author_series
            WHERE author_id = (?);
        """
        self.author_series_df = pd.read_sql(sql_com, self.conn, params=(self.id,))
        print(self.author_series_df)
        return self.author_series_df

    def full_ds(self):
        """Extracts list of series IDs for the author."""
        self.full_ds_ls = self.author_series_df["series_id"].tolist()
        return self.full_ds_ls

    def potential_ls(self):
        """Retrieves global pool of candidate series IDs."""
        sql_com = """ 
            SELECT series_id
            FROM author_series
        """
        df = pd.read_sql(sql_com, self.conn)
        self.potential_ls_full = df["series_id"].tolist()
        return self.potential_ls_full

    def rand_ds(self):
        """Samples random negative candidate series balanced with existing series."""
        random.seed(int(self.id))
        potential_ls_no_test_and_train = [i for i in self.potential_ls_full if i not in self.full_ds_ls]
        potential_ls = self.full_ds() + (random.sample(potential_ls_no_test_and_train, len(self.full_ds_ls)))

        a_ls = [self.id] * len(potential_ls)
        self.df_ran = pd.DataFrame({
            'series_id': potential_ls,
            'author_id': a_ls
        })
        return self.df_ran

    def train_test_ds_rand(self):
        """Splits sampled data into train and test sets, retaining positive series for training."""
        random.seed(int(self.id))
        train_df, test_df = split_train_test(self.df_ran)
        train_df = train_df[train_df['series_id'].isin(self.full_ds_ls)]
        return {
            "train": train_df,
            "test": test_df,
            "train_ls": train_df["series_id"].tolist(),
            "test_ls": test_df["series_id"].tolist()
        }

    def cross_join_single_ds_one_match(self, gseid_x, gseid_y):
        """Executes cross join between two specific series IDs to align feature columns."""
        sql_com = """ 
        SELECT s1.series_id AS GSEID_x, s1.title AS title_x, s1.organism AS organism_x, s1.experiment AS experiment_x, 
            s1.summary AS summary_x, s1.design AS design_x, s2.series_id AS GSEID_y, s2.title AS title_y, s2.organism AS organism_y,
            s2.experiment AS experiment_y, s2.summary AS summary_y, s2.design AS design_y
        FROM series as s2
        CROSS JOIN (
            SELECT s.series_id, s.design, s.experiment, s.organism, s.summary, s.title
            FROM series s
            WHERE s.series_id = (?)
        ) as s1
        WHERE s2.series_id = (?);
        """
        self.cj_sin_ds_one_match_df = pd.read_sql(sql_com, self.conn, params=(gseid_x, gseid_y))
        return self.cj_sin_ds_one_match_df

    def calculate_scores(self):
        """Calculates multi-dimensional text similarities across design, experiment, organism, summary, and title."""
        training_df = self.cj_sin_ds_one_match_df
        training_df['DESIGN_SCORE'] = training_df.apply(
            lambda row: iim_5f.similarity(row['design_x'], row['design_y']), axis=1
        )
        training_df['EXPERIMENT_SCORE'] = training_df.apply(
            lambda row: iim_5f.similarity_exp(row['experiment_x'], row['experiment_y']), axis=1
        )
        training_df['ORGANISM_SCORE'] = training_df.apply(
            lambda row: iim_5f.similarity_organism(row['organism_x'], row['organism_y']), axis=1
        )
        training_df['SUMMARY_SCORE'] = training_df.apply(
            lambda row: iim_5f.similarity(row['summary_x'], row['summary_y']), axis=1
        )
        training_df['TITLE_SCORE'] = training_df.apply(
            lambda row: iim_5f.similarity(row['title_x'], row['title_y']), axis=1
        )

        # 5-Feature aggregations
        training_df['5f_MIN_SCORE'] = training_df.loc[:, [
            "DESIGN_SCORE", "EXPERIMENT_SCORE", "ORGANISM_SCORE", 'SUMMARY_SCORE', 'TITLE_SCORE'
        ]].min(axis=1)
        training_df['5f_MAX_SCORE'] = training_df.loc[:, [
            "DESIGN_SCORE", "EXPERIMENT_SCORE", "ORGANISM_SCORE", 'SUMMARY_SCORE', 'TITLE_SCORE'
        ]].max(axis=1)
        training_df['5f_OVERALL_SCORE'] = training_df.loc[:, [
            "DESIGN_SCORE", "EXPERIMENT_SCORE", "ORGANISM_SCORE", 'SUMMARY_SCORE', 'TITLE_SCORE'
        ]].mean(axis=1)

        # 3-Feature aggregations
        training_df['3f_OVERALL_SCORE'] = training_df.loc[:, [
            "EXPERIMENT_SCORE", "ORGANISM_SCORE", 'SUMMARY_SCORE'
        ]].mean(axis=1)
        training_df['3f_MIN_SCORE'] = training_df.loc[:, [
            "EXPERIMENT_SCORE", "ORGANISM_SCORE", 'SUMMARY_SCORE'
        ]].min(axis=1)
        training_df['3f_MAX_SCORE'] = training_df.loc[:, [
            "EXPERIMENT_SCORE", "ORGANISM_SCORE", 'SUMMARY_SCORE'
        ]].max(axis=1)

        return (
            training_df["5f_MIN_SCORE"].values[0],
            training_df["5f_MAX_SCORE"].values[0],
            training_df["5f_OVERALL_SCORE"].values[0],
            training_df['3f_OVERALL_SCORE'].values[0],
            training_df['3f_MIN_SCORE'].values[0],
            training_df['3f_MAX_SCORE'].values[0]
        )


class email_ground_true_class_for_add_tf_to_csv:
    """Verifies author publication ownership using email disambiguation."""
    def __init__(self, gse, author_id):
        self.gse = gse
        self.author_id = author_id
        self.gse_pmid_dic = ecp.series_ls_w_contact("./github/data/raw/series_info.csv", 0)
        self.g_c_dic = ecp.g_c_dic("./github/data/raw/series_info.csv")
        self.pmid = self.gse_pmid_dic.get(gse)
        self.email = ""

    def author_info_sql(self):
        """Fetches contact status, author email, and last name from database."""
        conn = sqlite3.connect("sample.db")
        cur = conn.cursor()

        sql_com = """   
        SELECT contact
        FROM author_series
        WHERE author_id = (?) AND series_id = (?);
        """
        sql_email = """   
        SELECT email
        FROM author
        WHERE author_id = (?);
        """
        sql_last_name = """   
        SELECT last_name
        FROM author
        WHERE author_id = (?);
        """

        cur.execute(sql_com, (self.author_id, self.gse))
        result = cur.fetchone()
        self.contact_match = result[0] if result else 0

        cur.execute(sql_email, (self.author_id,))
        email_res = cur.fetchone()
        self.author_email_sql = email_res[0] if email_res else ""

        cur.execute(sql_last_name, (self.author_id,))
        name_res = cur.fetchone()
        self.author_last_name_sql = name_res[0] if name_res else ""
        conn.close()
        return self.contact_match, self.author_email_sql, self.author_last_name_sql

    def email_ground_true(self):
        """Resolves paper authorship email via PubMed extraction."""
        if not self.pmid:
            self.email = ""
            return self.email

        pmid_list = self.pmid if isinstance(self.pmid, list) else [self.pmid]
        email_final = ""

        for single_pmid in pmid_list:

            s_gse,s_pm=load_soups(self.gse,single_pmid)
            if self.contact_match == 1:
                extracted = contact_email(s_gse)
                print(extracted)
            else:
                name_ls = ae.name_full_list(s_pm, author_count(s_pm))
                positions = [idx for idx, name in enumerate(name_ls) if self.author_last_name_sql in name]
                if positions:
                    affil = ae.affiliation(s_pm, positions[0])
                    try:
                        extracted = ae.email(s_pm, positions[0], affil)
                    except Exception:
                        extracted = ae.email_alter(affil)
                else:
                    extracted = ""

            if len(extracted or "") > len(email_final):
                email_final = extracted or ""

        self.email = email_final
        return self.email

    def gse_ground_true(self):
        """Checks whether the extracted email matches the ground truth database email."""
        return bool(self.author_email_sql and (self.author_email_sql == self.email))


def email_fn(gse_id, author_id):
    """Convenience wrapper to check ground truth email match."""
    e = email_ground_true_class_for_add_tf_to_csv(gse_id, author_id)
    e.author_info_sql()
    e.email_ground_true()
    return e.gse_ground_true()

def add_label(df, full_ds_ls):
    """
    Adds a 'label' column to the DataFrame.
    Returns True if the 'test' series is present in the author's ground truth series (full_ds_ls),
    and False otherwise. Handles empty DataFrames safely.
    """
    if "test" not in df.columns or df.empty:
        df["label"] = pd.Series(dtype=bool)
        return df
    df["label"] = df["test"].isin(full_ds_ls)
    return df

def df_recom_no_threshold_all_pairs(author_id):
    """Processes candidate pairs for a single author and generates pairwise similarity metrics."""
    r1 = large_scale_5_features(author_id)
    r1.ds_ls()
    true_ds=r1.full_ds()
    r1.potential_ls()
    r1.rand_ds()
    ds = r1.train_test_ds_rand()
    train_ls, test_ls = ds["train_ls"], ds["test_ls"]

    # Filter train list using list comprehension to avoid in-place deletion skipping
    train_ls = [train_gse for train_gse in train_ls if email_fn(train_gse, author_id)]

    result = []
    print(f"Calculating similarities for {len(train_ls)} train series against {len(test_ls)} test series...")

    for test_idx, gseid_test in enumerate(test_ls, start=1):
        for gseid_train in train_ls:
            r1.cross_join_single_ds_one_match(gseid_train, gseid_test)
            min_5f, max_5f, avg_5f, avg_3f, min_3f, max_3f = r1.calculate_scores()

            result.append({
                "train": gseid_train,
                "test": gseid_test,
                "5f_min_scores": min_5f,
                "5f_max_scores": max_5f,
                "5f_avg_scores": avg_5f,
                "3f_avg_scores": avg_3f,
                "3f_min_scores": min_3f,
                "3f_max_scores": max_3f
            })

    r1.close_conn()
    df = pd.DataFrame(result)
    df["author_id"] = author_id
    df = add_label(df, true_ds)
    return train_ls, test_ls, df


def generate_recommendation_csv(author_id, output_dir):
    """
    Main function: Takes a single author_id as input, calculates
    pairwise similarity metrics, and exports a CSV file named '{author_id}.csv'.
    """
    author_id_str = str(author_id).strip()
    print(f"\n[INFO] Starting recommendation workflow for Author ID: {author_id_str}")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    _, _, df = df_recom_no_threshold_all_pairs(author_id_str)

    output_file = os.path.join(output_dir, f"{author_id_str}.csv")
    df.to_csv(output_file, index=False)

    print(f"[SUCCESS] Recommendation table exported with {len(df)} rows.")
    print(f"[FILE] Saved to: {os.path.abspath(output_file)}\n")
    return output_file


if __name__ == "__main__":
    # Prompt interactively for exactly one author_id
    target_author_id =38410
    output_dir = "./test_run"
    if target_author_id:
        generate_recommendation_csv(target_author_id,output_dir)
    else:
        print("[ERROR] No valid author_id provided.")