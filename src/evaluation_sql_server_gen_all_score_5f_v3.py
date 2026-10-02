import pandas as pd
from sklearn.model_selection import train_test_split
import sqlite3
import item_item_matrix_v3 as iim
import item_item_matrix_v2 as iim_5f
import numpy as np
import matplotlib.pyplot as plt
from sklearn import metrics
import seaborn as sns
import random
import os
from bs4 import BeautifulSoup
import Item_Extraction_Local as ie
import database_import_local_email_disambiguation_second_server_version as dbi
import extract_contact_person as ecp
import Author_Extraction_Local_second as ae
import csv
import sys


# Select contact author that asociate with more than 9 series
def ca_s_9():
    conn = sqlite3.connect("recom_sys.db")
    sql_com = """ 
        select a.author_id,ps.series_id
        FROM author a
        JOIN author_publication ap
        ON a.author_id=ap.author_id
        JOIN publication_series ps
        ON ap.pmid=ps.pmid
        WHERE ap.contact=1
        AND a.author_id IN (
            select a.author_id
            FROM author a
            JOIN author_publication ap
            ON a.author_id=ap.author_id
            JOIN publication_series ps
            ON ap.pmid=ps.pmid
            WHERE ap.contact=1
            GROUP BY a.author_id
            HAVING count(a.author_id)>9)
        ORDER BY a.author_id;"""
    df = pd.read_sql(sql_com, conn)
    conn.close()
    return df


# Count number of series that associate with selected contact author
def distinct_series_count():
    conn = sqlite3.connect("recom_sys.db")
    cur = conn.cursor()

    sql_com = """ 
    select count(distinct ps.series_id)
    FROM author a
    JOIN author_publication ap
    ON a.author_id=ap.author_id
    JOIN publication_series ps
    ON ap.pmid=ps.pmid
    WHERE ap.contact=1
    AND a.author_id IN (
        select a.author_id
        FROM author a
        JOIN author_publication ap
        ON a.author_id=ap.author_id
        JOIN publication_series ps
        ON ap.pmid=ps.pmid
        WHERE ap.contact=1
        GROUP BY a.author_id
        HAVING count(a.author_id)>9);"""

    cur.execute(sql_com)
    count = cur.fetchall()[0][0]
    conn.close()
    return count


# Count authors that associate with selected datasets number threshold
def author_count(min, max):
    conn = sqlite3.connect("recom_sys.db")
    cur = conn.cursor()

    sql_com = """ 
    SELECT count(*)
    FROM (
        select ap.author_id
        FROM author_publication ap, publication_series ps, author a
        WHERE ap.pmid=ps.pmid
        AND a.author_id=ap.author_id
        AND a.email != '[]'
        GROUP BY ap.author_id
        HAVING count(ps.series_id) BETWEEN (?) AND (?));
        """

    cur.execute(sql_com, (min, max))
    count = cur.fetchall()[0][0]
    conn.close()
    return count


# Count authors that associate with selected datasets number threshold
def author_series_count(min, max):
    conn = sqlite3.connect("recom_sys.db")
    cur = conn.cursor()

    sql_com = """ 
    SELECT count(*)
    FROM (
        select ass.author_id
        FROM author_series ass, author a
        WHERE ass.author_id=a.author_id
        AND a.email != '[]'
        AND a.email != ""
        GROUP BY ass.author_id
        HAVING count(ass.series_id) BETWEEN (?) AND (?));
        """
    sql_series = """
    SELECT COUNT(DISTINCT(series_id))
    FROM author_series
    WHERE author_id IN
        (
        select ass.author_id
        FROM author_series ass, author a
        WHERE ass.author_id=a.author_id
        AND a.email != '[]'
        AND a.email != ""
        GROUP BY ass.author_id
        HAVING count(ass.series_id) BETWEEN (?) AND (?)); 
    """
    cur.execute(sql_com, (min, max))
    author_count = cur.fetchall()[0][0]

    cur.execute(sql_series, (min, max))

    distinct_series_count = cur.fetchall()[0][0]
    conn.close()

    return author_count, distinct_series_count


## For db_eval database
def author_series_count_gs(threshold):
    conn = sqlite3.connect("db_eval.db")
    cur = conn.cursor()

    sql_com = """   
    select count(distinct(author_id))
    FROM series_author
    WHERE author_id IN (
    select author_id
    FROM series_author
    WHERE email != ''
    AND contact != 'ENCODE DCC'
    GROUP BY email
    HAVING count(series_id) >= (?));
    """

    sql_series = """
    select count(distinct(series_id))
    FROM series_author
    WHERE author_id IN (
    select author_id
    FROM series_author
    WHERE email != ''
    AND contact != 'ENCODE DCC'
    GROUP BY email
    HAVING count(series_id) >= (?));
    """
    cur.execute(sql_com, (threshold,))
    author_count = cur.fetchall()[0][0]

    cur.execute(sql_series, (threshold,))

    distinct_series_count = cur.fetchall()[0][0]
    conn.close()

    return author_count, distinct_series_count


# Generate dataframe and .csv with range of datasets as threshold, related author count and series count:
def df_author_series_count(min=0, max=300, step=5):
    dic = {"Threshold": [], "Author_Count": [], "Distinct_Series": []}
    for i in range(min, max, step):
        dic["Threshold"].append(i)
        count = author_series_count(i, i + step - 1)
        dic["Author_Count"].append(count[0])
        dic["Distinct_Series"].append(count[1])
    tbl = pd.DataFrame.from_dict(dic)
    tbl.to_csv("Author_Series_tbl_step_100.csv")
    return tbl


# Create author count histogram
def author_count_histogram(csv1="Author_Series_tbl_step_100.csv", csv2="Author_Series_tbl.csv"):
    df_author_series_count(min=0, max=4000, step=5)
    df_author_series_count(min=0, max=4000, step=100)
    df = pd.read_csv(csv1, index_col=0)
    df1 = pd.read_csv(csv2, index_col=0)
    fig, axes = plt.subplots(2, 1, figsize=(50, 10))  # 2 row, 1 columns
    sns.barplot(df, x="Threshold", y='Author_Count', ax=axes[0])
    axes[0].set_title('Histogram for Author Count With Outlier')
    axes[0].bar_label(axes[0].containers[0], fontsize=10)

    # Plot second boxplot
    sns.barplot(df1, x="Threshold", y='Author_Count', ax=axes[1])
    axes[1].set_title('Histogram for Author Count Without Outlier')
    axes[1].set_xlim(-.5, 20.5)
    axes[1].bar_label(axes[1].containers[0], fontsize=10)
    plt.show()


# Function to split each group, default 70% train, 30% test
def group_train(df, test_p=0.3):
    x = df["author_id"]
    y = df['series_id']
    train_x, test_x, train_y, test_y = train_test_split(x, y, test_size=test_p, random_state=42)
    train = pd.concat([train_x, train_y], axis=1)
    return train


def group_test(df, test_p=0.3):
    x = df["author_id"]
    y = df['series_id']
    train_x, test_x, train_y, test_y = train_test_split(x, y, test_size=test_p, random_state=42)
    test = pd.concat([test_x, test_y], axis=1)
    return test


# Training and testing dataset for small scale db
def train_test_ds():
    df = ca_s_9()

    # Apply the function to each group
    train_df = df.groupby('author_id').apply(group_train).reset_index(drop=True)

    test_df = df.groupby('author_id').apply(group_test).reset_index(drop=True)

    # # Display the resulting DataFrame
    # pd.set_option('display.max_rows', None)
    # print(test_df)

    return {"train": train_df, "test": test_df}



"""
Training and testing dataset for large scale db

Step 1: Split the datasets of an author associated with an email address. 

Step 2:Cross join one dataset with other datasets with 5 features

"""


class large_scale_5_features:
    def __init__(self, id):
        self.conn = sqlite3.connect("recom_sys.db")
        self.cur = self.conn.cursor()
        self.id = id

    def close_conn(self):
        self.cur.close()
        self.conn.close()

    def ds_ls(self):  # id = author id
        sql_com = """ 
            SELECT series_id,author_id
            FROM author_series
            WHERE author_id=(?);
        """
        self.author_series_df = pd.read_sql(sql_com, self.conn, params=(self.id,))
        return self.author_series_df

    # Obtain all GSEID associate with author
    def full_ds(self):
        self.full_ds_ls = self.author_series_df["series_id"].tolist()
        return self.full_ds_ls

    # Split author's gse list into train and test set
    def train_test_ds(self):
        random.seed(int(self.id))
        # Apply the function to each group
        train_df = group_train(self.author_series_df, test_p=0.3).reset_index(drop=True)
        test_df = group_test(self.author_series_df).reset_index(drop=True)
        return {"train": train_df, "test": test_df, "train_ls": train_df["series_id"].tolist(),
                "test_ls": test_df["series_id"].tolist()}

    # Return ls of all datasets
    def potential_ls(self):
        sql_com = """ 
            select *
            FROM author_series
        """
        df = pd.read_sql(sql_com, self.conn)
        self.potential_ls_full = df["series_id"].tolist()
        return self.potential_ls_full

    # GSEID list of an author + same size of random selected GSEID list
    def rand_ds(self):
        random.seed(int(self.id))
        potential_ls_no_test_and_train = [i for i in self.potential_ls_full if i not in self.full_ds_ls]

        # Potential_ls = author's all datasets  + randomly selected gseid
        potential_ls = self.full_ds() + (random.sample(potential_ls_no_test_and_train, len(self.full_ds_ls)))

        a_ls = [self.id] * len(potential_ls)
        self.df_ran = pd.DataFrame({
            'series_id': potential_ls,
            'author_id': a_ls
        })
        return self.df_ran

    # After random matching same number of author's datasets, split combined datasets into training and testing
    def train_test_ds_rand(self):
        random.seed(int(self.id))
        # Apply the function to each group
        train_df = group_train(self.df_ran, test_p=0.3).reset_index(drop=True)
        test_df = group_test(self.df_ran).reset_index(drop=True)
        train_df = train_df[train_df['series_id'].isin(self.full_ds_ls)]
        return {"train": train_df, "test": test_df, "train_ls": train_df["series_id"].tolist(),
                "test_ls": test_df["series_id"].tolist()}

    def cross_join_single_ds(self, gseid):
        sql_com = """ 
            SELECT s1.series_id AS GSEID_x, s1.title AS title_x, s1.organism AS organism_x, s1.experiment AS experiment_x, 
                s1.summary AS summary_x, s1.design AS design_x,s2.series_id AS GSEID_y, s2.title AS title_y, s2.organism AS organism_y,
                s2.experiment AS experiment_y, s2.summary AS summary_y, s2.design AS design_y

            FROM series as s2
            CROSS JOIN(
                SELECT s.series_id,s.design,s.experiment,s.organism,s.summary,s.title
                FROM series s
                WHERE s.series_id=(?)) as s1
        """
        df = pd.read_sql(sql_com, self.conn, params=(gseid,))

        return df

    # Return one pair of datasets
    ## gseid_X: datasets that we have
    ## gseid_Y: potential datasets that can be recommended to the one we have
    def cross_join_single_ds_one_match(self, gseid_x, gseid_y):
        sql_com = """ 
        SELECT s1.series_id AS GSEID_x, s1.title AS title_x, s1.organism AS organism_x, s1.experiment AS experiment_x, 
            s1.summary AS summary_x, s1.design AS design_x,s2.series_id AS GSEID_y, s2.title AS title_y, s2.organism AS organism_y,
            s2.experiment AS experiment_y, s2.summary AS summary_y, s2.design AS design_y
        FROM series as s2
        CROSS JOIN(
            SELECT s.series_id,s.design,s.experiment,s.organism,s.summary,s.title
            FROM series s
            WHERE s.series_id=(?)) as s1
        WHERE GSEID_y=(?);
        """
        self.cj_sin_ds_one_match_df = pd.read_sql(sql_com, self.conn, params=(gseid_x, gseid_y))
        return self.cj_sin_ds_one_match_df

    ## gseid_X: datasets that we have
    ## gseid_Y: potential datasets that can be recommended to the one we have

    def calculate_scores(self):
        """
        Calculate the scores for each feature defined below.

         features = ['DESIGN_SCORE','EXPERIMENT_SCORE','ORGANISM_SCORE','SUMMARY_SCORE','MATCH']

        :return:
        """
        training_df = self.cj_sin_ds_one_match_df
        training_df['DESIGN_SCORE'] = training_df.apply(lambda row: iim_5f.similarity(row['design_x'], row['design_y']),
                                                        axis=1)
        training_df['EXPERIMENT_SCORE'] = training_df.apply(
            lambda row: iim_5f.similarity_exp(row['experiment_x'], row['experiment_y']), axis=1)
        training_df['ORGANISM_SCORE'] = training_df.apply(
            lambda row: iim_5f.similarity_organism(row['organism_x'], row['organism_y']), axis=1)
        training_df['SUMMARY_SCORE'] = training_df.apply(lambda row: iim_5f.similarity(row['summary_x'], row['summary_y']),
                                                         axis=1)
        training_df['TITLE_SCORE'] = training_df.apply(lambda row: iim_5f.similarity(row['title_x'], row['title_y']),
                                                       axis=1)
        training_df['MIN_SCORE'] = training_df.loc[:, ["DESIGN_SCORE", "EXPERIMENT_SCORE",
                                                           "ORGANISM_SCORE", 'SUMMARY_SCORE', 'TITLE_SCORE']].min(
            axis=1)

        training_df['MAX_SCORE'] = training_df.loc[:, ["DESIGN_SCORE", "EXPERIMENT_SCORE",
                                                       "ORGANISM_SCORE", 'SUMMARY_SCORE', 'TITLE_SCORE']].max(
        axis=1)

        training_df['OVERALL_SCORE'] = training_df.loc[:, ["DESIGN_SCORE", "EXPERIMENT_SCORE",
                                                           "ORGANISM_SCORE", 'SUMMARY_SCORE', 'TITLE_SCORE']].mean(
            axis=1)
        training_df['3f_OVERALL_SCORE'] = training_df.loc[:, ["EXPERIMENT_SCORE",
                                                           "ORGANISM_SCORE", 'SUMMARY_SCORE']].mean(
            axis=1)

        training_df['3f_MIN_SCORE'] = training_df.loc[:, ["EXPERIMENT_SCORE",
                                                           "ORGANISM_SCORE", 'SUMMARY_SCORE']].min(
            axis=1)
        training_df['3f_MAX_SCORE'] = training_df.loc[:, ["EXPERIMENT_SCORE",
                                                           "ORGANISM_SCORE", 'SUMMARY_SCORE']].max(
            axis=1)


        min_scores = training_df["MIN_SCORE"].values[0]
        max_scores = training_df["MAX_SCORE"].values[0]
        avg_scores = training_df["OVERALL_SCORE"].values[0]
        avg_3f_scores=training_df['3f_OVERALL_SCORE'].values[0]
        min_3f_scores=training_df['3f_MIN_SCORE'].values[0]
        max_3f_scores=training_df['3f_MAX_SCORE'].values[0]
        return min_scores,max_scores,avg_scores,avg_3f_scores,min_3f_scores,max_3f_scores


"""
Training and testing dataset for large scale db

Step 1: Split the datasets of an author associated with an email address. 

Step 2:Cross join one dataset with other datasets with concatenate 5 features into one sentence


"""


class large_scale:
    def __init__(self, id):
        self.conn = sqlite3.connect("recom_sys.db")
        self.cur = self.conn.cursor()
        self.id = id

    def close_conn(self):
        self.cur.close()
        self.conn.close()

    def ds_ls(self):  # id = author id
        sql_com = """ 
            SELECT series_id,author_id
            FROM author_series
            WHERE author_id=(?);
        """
        self.author_series_df = pd.read_sql(sql_com, self.conn, params=(self.id,))
        return self.author_series_df

    # Obtain all GSEID associate with author
    def full_ds(self):
        self.full_ds_ls = self.author_series_df["series_id"].tolist()
        return self.full_ds_ls

    # Split author's gse list into train and test set
    def train_test_ds(self):
        random.seed(int(self.id))
        # Apply the function to each group
        train_df = group_train(self.author_series_df, test_p=0.3).reset_index(drop=True)
        test_df = group_test(self.author_series_df).reset_index(drop=True)
        return {"train": train_df, "test": test_df, "train_ls": train_df["series_id"].tolist(),
                "test_ls": test_df["series_id"].tolist()}

    # Return ls of all datasets
    def potential_ls(self):
        sql_com = """ 
            select *
            FROM author_series
        """
        df = pd.read_sql(sql_com, self.conn)
        self.potential_ls_full = df["series_id"].tolist()
        return self.potential_ls_full

    # GSEID list of an author + same size of random selected GSEID list
    def rand_ds(self):
        random.seed(int(self.id))
        potential_ls_no_test_and_train = [i for i in self.potential_ls_full if i not in self.full_ds_ls]

        # Potential_ls = author's all datasets  + randomly selected gseid
        potential_ls = self.full_ds() + (random.sample(potential_ls_no_test_and_train, len(self.full_ds_ls)))

        a_ls = [self.id] * len(potential_ls)
        self.df_ran = pd.DataFrame({
            'series_id': potential_ls,
            'author_id': a_ls
        })
        return self.df_ran

    # After random matching same number of author's datasets, split combined datasets into training and testing
    def train_test_ds_rand(self):
        random.seed(int(self.id))
        # Apply the function to each group
        train_df = group_train(self.df_ran, test_p=0.3).reset_index(drop=True)
        test_df = group_test(self.df_ran).reset_index(drop=True)
        train_df = train_df[train_df['series_id'].isin(self.full_ds_ls)]
        return {"train": train_df, "test": test_df, "train_ls": train_df["series_id"].tolist(),
                "test_ls": test_df["series_id"].tolist()}

    def cross_join_single_ds(self, gseid):
        sql_com = """ 
            SELECT s1.series_id AS GSEID_x, s1.title AS title_x, s1.organism AS organism_x, s1.experiment AS experiment_x, 
                s1.summary AS summary_x, s1.design AS design_x,s2.series_id AS GSEID_y, s2.title AS title_y, s2.organism AS organism_y,
                s2.experiment AS experiment_y, s2.summary AS summary_y, s2.design AS design_y

            FROM series as s2
            CROSS JOIN(
                SELECT s.series_id,s.design,s.experiment,s.organism,s.summary,s.title
                FROM series s
                WHERE s.series_id=(?)) as s1
        """
        df = pd.read_sql(sql_com, self.conn, params=(gseid,))

        return df

    # Return one pair of datasets
    ## gseid_X: datasets that we have
    ## gseid_Y: potential datasets that can be recommended to the one we have

    def cross_join_single_ds_one_match(self, gseid_x, gseid_y):
        sql_com = """ 
        SELECT 
            s1.series_id AS GSEID_x, s1.title ||' '|| s1.organism ||' '|| s1.experiment ||' '|| 
            s1.summary ||' '|| s1.design AS all_info_x,
            s2.series_id AS GSEID_y, s2.title ||' '|| s2.organism ||' '|| s2.experiment ||' '|| 
            s2.summary ||' '|| s2.design AS all_info_y
        FROM series s1
        CROSS JOIN series s2
        WHERE s1.series_id=(?)
        AND s2.series_id=(?);
        """
        self.cj_sin_ds_one_match_df = pd.read_sql(sql_com, self.conn, params=(gseid_x, gseid_y))
        return self.cj_sin_ds_one_match_df

    ## gseid_X: datasets that we have
    ## gseid_Y: potential datasets that can be recommended to the one we have

    def calculate_scores(self):
        training_df = self.cj_sin_ds_one_match_df
        training_df['score'] = training_df.apply(lambda row: iim.similarity(row['all_info_x'], row['all_info_y']),
                                                 axis=1)
        training_scores_df = training_df["score"].values[0]
        return training_scores_df



# Function to remove gse with lowest similarity score
def remove_gse(dict):
    smallest_gse, smallest_score = "", 1  # Set default string and max similarity score = 1
    # loop through all gseid and their score, drop the lowest one
    for k, v in dict.items():
        if v < smallest_score:
            smallest_score = v
            smallest_gse = k
    dict.pop(smallest_gse)
    return dict


# df for recommendation result without randomly matched same number of datasets initially
def df(author_id):
    import random
    random.seed(author_id)
    r1 = large_scale()
    ds = r1.train_test_ds(author_id)
    train_ls, test_ls = ds["train_ls"], ds["test_ls"]
    potential_ls_no_test_and_train = [i for i in r1.potential_ls() if i not in train_ls and i not in test_ls]

    # Potential_ls = test gseid + randomly selected gseid
    potential_ls = list(set(test_ls + (random.sample(potential_ls_no_test_and_train, len(test_ls)))))

    dict, problem_ls = {}, []
    for j in range(len(train_ls)):
        for i in range(len(potential_ls)):
            try:
                gseid = potential_ls[i]
                score = r1.calculate_scores(train_ls[j], potential_ls[i])
                print(score)
                # add gseid and score pairs to dictionary if dictionary has less than 5 pairs
                # condition on score > 0.5
                if len(dict) < 5 and score > 0.5:
                    dict[gseid] = score
                # drop lowest score pair and add new pair in
                elif len(dict) >= 5 and score > 0.5:
                    if any(score > value for value in dict.values()) and gseid not in dict:
                        dict = r1.remove_gse(dict)
                        dict[gseid] = score
            except:
                problem_ls.append(gseid)

    r1.close_conn()
    print(f'problem list is {problem_ls}')
    df = pd.DataFrame.from_dict(dict, orient='index', columns=['scores'])
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'gseid'}, inplace=True)
    df["author_id"] = author_id
    return df

def author_ls():
    conn = sqlite3.connect("recom_sys.db")
    cur = conn.cursor()

    sql_com = """ 
    SELECT *
    FROM (
        SELECT ass.author_id
        FROM author_series ass
        JOIN author a ON ass.author_id = a.author_id
        JOIN series s ON ass.series_id = s.series_id
          WHERE s.design NOT LIKE 'Refer%'
          AND a.email IS NOT NULL
          AND a.email != '[]'
          AND a.email != ''
        GROUP BY ass.author_id
        HAVING COUNT(DISTINCT ass.series_id) BETWEEN 15 AND 21
    ) AS filtered_authors;
    """
    df = pd.read_sql(sql_com, conn)

    cur.close()
    conn.close()
    return df["author_id"].tolist()


"""
Recommendation
"""

"""
Generate recommended csv for each author with limited recommendation
"""


def output_recom_csv_w_limit(min_num_recom, max_num_recom, skip=1):  # Output
    author = author_ls()
    total_num = len(author)
    for j in range(min_num_recom, max_num_recom, skip):
        for i in author:
            train_ls, test_ls, df = df_ran(i, j)
            folder_path = f"./evaluation_recommendation_ds/recom_{j}_match_split"
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            df.to_csv(f"./evaluation_recommendation_ds/recom_{j}_match_split/{i}.csv")
            total_num -= 1
            print(f"{total_num} recommendation remaining")


"Generate recommended csv for each author without limited recommendation"
def output_recom_csv_no_limit():
    author = author_ls()
    total_num = len(author)
    for i in author:
        train_ls, test_ls, df = df_recom_no_threshold(i)
        folder_path = f"./evaluation_recommendation_ds/recom_match_split_full_test_ls"
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        df.to_csv(f"./evaluation_recommendation_ds/recom_match_split_w_no_limit/{i}.csv")
        total_num -= 1
        print(f"{total_num} recommendation remaining")


class email_ground_true_class_for_add_tf_to_csv:
    def __init__(self, gse, author_id):
        self.gse = gse
        self.author_id = author_id
        self.gse_pmid_dic = ecp.series_ls_w_contact("./series_sep25.csv", 0)
        self.g_c_dic = ecp.g_c_dic("./series_sep25.csv")
        self.pmid = self.gse_pmid_dic[gse]

    def author_info_sql(self):

        conn = sqlite3.connect("recom_sys.db")
        cur = conn.cursor()

        sql_com = """   
        SELECT contact
        FROM author_series
        WHERE author_id=(?)
        AND series_id=(?);
        """

        sql_email = """   
        SELECT email
        FROM author
        WHERE author_id=(?);
        """

        sql_last_name = """   
        SELECT last_name
        FROM author
        WHERE author_id=(?);
        """

        cur.execute(sql_com, (self.author_id, self.gse))
        result = cur.fetchone()
        if result:
            self.contact_match = result[0]
        else:
            self.contact_match = 0

        cur.execute(sql_email, (self.author_id,))
        self.author_email_sql = cur.fetchall()[0][0]

        cur.execute(sql_last_name, (self.author_id,))
        self.author_last_name_sql = cur.fetchall()[0][0]
        conn.close()
        return self.contact_match, self.author_email_sql, self.author_last_name_sql

    def email_ground_true(self):
        if type(self.pmid) == list:
            email_final = ""
            for pmid in self.pmid:
                se = dbi.series(self.gse, self.g_c_dic, pmid)
                if self.contact_match == 1:
                    self.email = ie.contact_email(se.soup_gse)
                else:
                    name_ls = ae.name_full_list(se.soup, se.num_author)
                    positions = [i for i, v in enumerate(name_ls) if self.author_last_name_sql in v]
                    if positions:
                        affil = ae.affiliation(se.soup, positions[0])
                        try:
                            self.email = ae.email(se.soup, positions[0], affil)
                        except:
                            self.email = ae.email_alter(affil)
                    else:
                        self.email = ""
                if len(self.email) > len(email_final):
                    email_final = self.email
            return email_final
        else:
            se = dbi.series(self.gse, self.g_c_dic, self.pmid)
            if self.contact_match == 1:
                self.email = ie.contact_email(se.soup_gse)
            else:
                name_ls = ae.name_full_list(se.soup, se.num_author)
                positions = [i for i, v in enumerate(name_ls) if self.author_last_name_sql in v]
                if positions:
                    affil = ae.affiliation(se.soup, positions[0])
                    try:
                        self.email = ae.email(se.soup, positions[0], affil)
                    except:
                        self.email = ae.email_alter(affil)
                else:
                    self.email = ""
        return self.email

    def gse_ground_true(self):

        if self.author_email_sql == self.email:
            return True
        else:
            return False


def evaluation():
    path = f"./evaluation_recommendation_ds/recom_match_split_w_no_limit/"
    files = os.listdir(path)
    count_author = len(files)
    tp, fp, tn, fn, precision_num, recall_num = 0, 0, 0, 0, 0, 0

    # Create a .csv to store tp,fp,tn,fn
    file_name = "./evaluation_recommendation_ds/evaluation_no_limit.csv"
    with open(file_name, mode="w", newline="") as file:
        writer = csv.writer(file)
        # Write a single header row (list of column names)
        writer.writerow(["author_id", "tp", "fp", "tn", "fn", "topn"])

    for i in files:
        df = pd.read_csv(f"{path}/{i}")
        recom = df["gseid"].tolist()
        topn = df.shape[0]
        author_id = i.replace(".csv", "")
        random.seed(author_id)
        r1 = large_scale(author_id)
        r1.ds_ls()
        r1.full_ds()
        r1.potential_ls()
        r1.rand_ds()
        ds = r1.train_test_ds_rand()
        train_ls, test_ls = ds["train_ls"], ds["test_ls"]
        # generate gold standard list to ground true datasets, and they are validated through author email
        gs = [i for i in test_ls if i in r1.full_ds()]
        gs_copy = gs.copy()

        for dataset in gs_copy:  # Keep only gs test set
            gt = email_ground_true_class(dataset, author_id)
            gt.author_info_sql()
            gt.email_ground_true()
            if not gt.gse_ground_true():
                gs.remove(dataset)

        if len(gs) == 0:
            count_author -= 1
            print(f"{i} is skip,{count_author} evaluation is remaining")
            continue

        not_recom = [i for i in test_ls if i not in recom]

        tp = len([i for i in recom if i in gs])
        fp = len([i for i in recom if i not in gs])
        tn = len([i for i in not_recom if i not in gs])
        fn = len([i for i in not_recom if i in gs])

        # Store values into csv
        with open(file_name, mode="a", newline="") as file:
            writer = csv.writer(file)
            new_row = [author_id, tp, fp, tn, fn, topn]
            writer.writerow(new_row)

        count_author -= 1
        print(f"{count_author} evaluation is remaining")


def email_fn(gse_id,author_id):
    e=email_ground_true_class_for_add_tf_to_csv(gse_id,author_id)
    e.author_info_sql()
    e.email_ground_true()
    return e.gse_ground_true()

def add_email_validation_to_author_csv():
    df=pd.read_csv("./evaluation_recommendation_ds/evaluation_no_limit.csv")
    author_ls=df["author_id"].tolist()
    for idx in author_ls:
        df = pd.read_csv(f"./evaluation_recommendation_ds/recom_match_split_w_no_limit/{idx}.csv")
        if len(df)==0:
            continue
        df["email"] = df.apply(lambda row: email_fn(row["gseid"], row["author_id"]), axis=1)
        df.to_csv(f"./evaluation_recommendation_ds/recom_match_split_w_no_limit_with_gt/{idx}.csv")

"""
Recommendation result df with random selected gseid first
No Recommend Threshold
No limited recommendation
"""

def df_recom_no_threshold(author_id):
    r1=large_scale(author_id)
    r1.ds_ls()
    r1.full_ds()
    r1.potential_ls()
    r1.rand_ds()
    ds=r1.train_test_ds_rand()
    train_ls,test_ls=ds["train_ls"],ds["test_ls"]
    dict, problem_ls = {}, []

    # Match all train dataset for every test dataset
    for j in range(len(test_ls)):
        gseid_test = test_ls[j]
        score_sum = 0
        for i in range(len(train_ls)):
            gseid_train = train_ls[i]
            r1.cross_join_single_ds_one_match(gseid_train, gseid_test)
            score = r1.calculate_scores()
            score_sum += score
        # Averages the similarity scores for each test dataset
        dict[gseid_test] = score_sum / len(train_ls)
    r1.close_conn()
    df = pd.DataFrame.from_dict(dict, orient='index', columns=['scores'])
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'gseid'}, inplace=True)
    df["author_id"] = author_id
    df["label"] = df.apply(lambda row: email_fn(row["gseid"], row["author_id"]), axis=1)
    return train_ls, test_ls, df


"""
Recommendation result df with random and non-random selected test gseid 
No Recommended Threshold
No limited recommendation
Generate similarity score for every matching per author
"""

def df_recom_no_threshold_all_pairs(author_id):
    r1=large_scale_5_features(author_id)
    r1.ds_ls()
    r1.full_ds()
    r1.potential_ls()
    r1.rand_ds()
    ds=r1.train_test_ds_rand()
    train_ls,test_ls=ds["train_ls"],ds["test_ls"]
    for train_gse in train_ls:
        if not email_fn(train_gse, author_id):
            train_ls.remove(train_gse)
    result= []
    # Match all train dataset for every test dataset
    for j in range(len(test_ls)):
        gseid_test = test_ls[j]
        score_sum = 0
        for i in range(len(train_ls)):
            gseid_train = train_ls[i]
            r1.cross_join_single_ds_one_match(gseid_train, gseid_test)
            min_scores, max_scores, avg_scores, avg_3f_scores, min_3f_scores, max_3f_scores = r1.calculate_scores()

            result.append({
                "train": gseid_train,
                "test": gseid_test,
                "min_scores": min_scores,
                "max_scores": max_scores,
                "avg_scores": avg_scores,
                "3f_avg_scores":avg_3f_scores,
                "3f_min_scores": min_3f_scores,
                "3f_max_scores": max_3f_scores
            })
    r1.close_conn()
    df = pd.DataFrame(result)
    df["author_id"] = author_id
    return train_ls, test_ls, df

if __name__ == "__main__":
    author = author_ls()
    total_num = len(author)


    for i in range(int(sys.argv[1]), int(sys.argv[1])+199):
        id = author[i]
        train_ls, test_ls, df = df_recom_no_threshold_all_pairs(id)
        folder_path = f"./evaluation_recommendation_ds/recom_match_split_full_test_ls_w_5_features_3_features_label_filterd_train_no_superseries"
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        df.to_csv(f"{folder_path}/{id}.csv")
        total_num -= 1
        print(f"{total_num} recommendation remaining")


