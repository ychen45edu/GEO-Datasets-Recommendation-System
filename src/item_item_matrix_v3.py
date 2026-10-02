import pandas as pd
import numpy as np
from numpy.linalg import norm
import math
import Item_Extraction_Local as ie
import sqlite3
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

#Reduce/stemming and remove stop words
def stop_word_stemming_(sentence):
    """

    :param sentence: sentence
    :return: list of words without stop words

    Execute next two lines if stopwords aren't download.
        import nltk
        nltk.download('stopwords')

    stop words:
    [‘i’, ‘me’, ‘my’, ‘myself’, ‘we’, ‘our’, ‘ours’, ‘ourselves’, ‘you’, “you’re”, “you’ve”, “you’ll”, “you’d”, ‘your’, ‘yours’, ‘yourself’,
    ‘yourselves’, ‘he’, ‘him’, ‘his’, ‘himself’, ‘she’, “she’s”, ‘her’, ‘hers’, ‘herself’, ‘it’, “it’s”, ‘its’, ‘itself’, ‘they’, ‘them’,
    ‘their’, ‘theirs’, ‘themselves’, ‘what’, ‘which’, ‘who’, ‘whom’, ‘this’, ‘that’, “that’ll”, ‘these’, ‘those’, ‘am’, ‘is’, ‘are’, ‘was’,
    ‘were’, ‘be’, ‘been’, ‘being’, ‘have’, ‘has’, ‘had’, ‘having’, ‘do’, ‘does’, ‘did’, ‘doing’, ‘a’, ‘an’, ‘the’, ‘and’, ‘but’, ‘if’, ‘or’,
    ‘because’, ‘as’, ‘until’, ‘while’, ‘of’, ‘at’, ‘by’, ‘for’, ‘with’, ‘about’, ‘against’, ‘between’, ‘into’, ‘through’, ‘during’, ‘before’,
    ‘after’, ‘above’, ‘below’, ‘to’, ‘from’, ‘up’, ‘down’, ‘in’, ‘out’, ‘on’, ‘off’, ‘over’, ‘under’, ‘again’, ‘further’, ‘then’, ‘once’,
    ‘here’, ‘there’, ‘when’, ‘where’, ‘why’, ‘how’, ‘all’, ‘any’, ‘both’, ‘each’, ‘few’, ‘more’, ‘most’, ‘other’, ‘some’, ‘such’, ‘no’,
    ‘nor’, ‘not’, ‘only’, ‘own’, ‘same’, ‘so’, ‘than’, ‘too’, ‘very’, ‘s’, ‘t’, ‘can’, ‘will’, ‘just’, ‘don’, “don’t”, ‘should’, “should’ve”,
    ‘now’, ‘d’, ‘ll’, ‘m’, ‘o’, ‘re’, ‘ve’, ‘y’, ‘ain’, ‘aren’, “aren’t”, ‘couldn’, “couldn’t”, ‘didn’, “didn’t”, ‘doesn’, “doesn’t”, ‘hadn’,
    “hadn’t”, ‘hasn’, “hasn’t”, ‘haven’, “haven’t”, ‘isn’, “isn’t”, ‘ma’, ‘mightn’, “mightn’t”, ‘mustn’, “mustn’t”, ‘needn’, “needn’t”,
    ‘shan’, “shan’t”, ‘shouldn’, “shouldn’t”, ‘wasn’, “wasn’t”, ‘weren’, “weren’t”, ‘won’, “won’t”, ‘wouldn’, “wouldn’t”]
    """




    stop_words = stopwords.words('english')
    # Convert sentence to lower case
    sentence_lc = str(sentence).lower()

    # remove stop words and stemming words
    bagOfWords = sentence_lc.split(' ')

    ps = PorterStemmer()

    filtered_sentence = []

    for w in bagOfWords:
        stem=ps.stem(w)
        if stem not in stop_words:
            filtered_sentence.append(stem)
    return filtered_sentence

# Removed "other" from stopwords and added "expression", 'profiling', 'by'
def stop_word_stemming_no_other_(sentence):
    """
    :param sentence: sentence
    :return: list of words without stop words

    Execute next two lines if stopwords aren't download.
        import nltk
        nltk.download('stopwords')

    stop words:
    [‘i’, ‘me’, ‘my’, ‘myself’, ‘we’, ‘our’, ‘ours’, ‘ourselves’, ‘you’, “you’re”, “you’ve”, “you’ll”, “you’d”, ‘your’, ‘yours’, ‘yourself’,
    ‘yourselves’, ‘he’, ‘him’, ‘his’, ‘himself’, ‘she’, “she’s”, ‘her’, ‘hers’, ‘herself’, ‘it’, “it’s”, ‘its’, ‘itself’, ‘they’, ‘them’,
    ‘their’, ‘theirs’, ‘themselves’, ‘what’, ‘which’, ‘who’, ‘whom’, ‘this’, ‘that’, “that’ll”, ‘these’, ‘those’, ‘am’, ‘is’, ‘are’, ‘was’,
    ‘were’, ‘be’, ‘been’, ‘being’, ‘have’, ‘has’, ‘had’, ‘having’, ‘do’, ‘does’, ‘did’, ‘doing’, ‘a’, ‘an’, ‘the’, ‘and’, ‘but’, ‘if’, ‘or’,
    ‘because’, ‘as’, ‘until’, ‘while’, ‘of’, ‘at’, ‘by’, ‘for’, ‘with’, ‘about’, ‘against’, ‘between’, ‘into’, ‘through’, ‘during’, ‘before’,
    ‘after’, ‘above’, ‘below’, ‘to’, ‘from’, ‘up’, ‘down’, ‘in’, ‘out’, ‘on’, ‘off’, ‘over’, ‘under’, ‘again’, ‘further’, ‘then’, ‘once’,
    ‘here’, ‘there’, ‘when’, ‘where’, ‘why’, ‘how’, ‘all’, ‘any’, ‘both’, ‘each’, ‘few’, ‘more’, ‘most’, ‘other’, ‘some’, ‘such’, ‘no’,
    ‘nor’, ‘not’, ‘only’, ‘own’, ‘same’, ‘so’, ‘than’, ‘too’, ‘very’, ‘s’, ‘t’, ‘can’, ‘will’, ‘just’, ‘don’, “don’t”, ‘should’, “should’ve”,
    ‘now’, ‘d’, ‘ll’, ‘m’, ‘o’, ‘re’, ‘ve’, ‘y’, ‘ain’, ‘aren’, “aren’t”, ‘couldn’, “couldn’t”, ‘didn’, “didn’t”, ‘doesn’, “doesn’t”, ‘hadn’,
    “hadn’t”, ‘hasn’, “hasn’t”, ‘haven’, “haven’t”, ‘isn’, “isn’t”, ‘ma’, ‘mightn’, “mightn’t”, ‘mustn’, “mustn’t”, ‘needn’, “needn’t”,
    ‘shan’, “shan’t”, ‘shouldn’, “shouldn’t”, ‘wasn’, “wasn’t”, ‘weren’, “weren’t”, ‘won’, “won’t”, ‘wouldn’, “wouldn’t”]
    """
    from nltk.corpus import stopwords
    from nltk.stem import PorterStemmer
    from nltk.tokenize import word_tokenize

    stop_words = stopwords.words('english')
    stop_words.remove("other")

    add_stop_ls = ["expression", 'profiling', 'by']
    stop_words=stop_words+add_stop_ls


    # Convert sentence to lower case
    sentence_lc = str(sentence).lower()

    # remove stop words and stemming words
    bagOfWords = sentence_lc.split(' ')

    ps = PorterStemmer()

    filtered_sentence = []

    for w in bagOfWords:
        stem=ps.stem(w)
        if stem not in stop_words:
            filtered_sentence.append(stem)
    return filtered_sentence

def computeTF(wordDict, bagOfWords):
    tfDict = {}
    bagOfWordsCount = len(bagOfWords)
    for word, count in wordDict.items():
        tfDict[word] = count / float(bagOfWordsCount)
    return tfDict


def computeIDF(documents):

    N = len(documents)

    idfDict = dict.fromkeys(documents[0].keys(), 0)
    for document in documents:
        for word, val in document.items():
            if val > 0:
                idfDict[word] += 1

    for word, val in idfDict.items():
        idfDict[word] = math.log(N / float(val))
    return idfDict

def computeTFIDF(tfBagOfWords, idfs):
    tfidf = {}
    for word, val in tfBagOfWords.items():
        tfidf[word] = val * idfs[word]
    return tfidf


# TFIDF
# df=pd.read_csv("./evaluation_recommendation_ds/Similariy Matrix/full_similarity_matrix_id_1279618_1_feature.csv")
#
# all_texts = pd.concat([df['all_info_x'], df['all_info_y']]).drop_duplicates()
#
# stop_words = stopwords.words('english')
# stop_words.remove("other")
# add_stop_ls = ["expression", 'profiling', 'by']
# stop_words = stop_words + add_stop_ls
#
# vectorizer = TfidfVectorizer(stop_words=stop_words)
# vectorizer.fit(all_texts)
#
# tfidf_x = vectorizer.transform(df['all_info_x'])  # shape: (num_rows, vocab_size)
# tfidf_y = vectorizer.transform(df['all_info_y'])  # shape: (num_rows, vocab_size)
#
#
# similarities = []
# for i in range(df.shape[0]):
#     sim = cosine_similarity(tfidf_x[i], tfidf_y[i])[0,0]
#     similarities.append(sim)
#
# df['score'] = similarities
# df.to_csv("./evaluation_recommendation_ds/Similariy Matrix/full_similarity_matrix_tfidf_id_1279618_1_feature.csv")

import numpy as np

# Assume 'model' is a pre-trained Word2Vec model
def text_to_vector(text):
    words = text.split()
    word_vectors = [model[word] for word in words if word in model]
    return np.mean(word_vectors, axis=0)


# Cosine similarity of sentence using TF
def similarity(sentence1, sentence2):
    if str(sentence1)=="nan" or str(sentence2)=="nan":
        return 0

    bagOfWordsA = stop_word_stemming_(sentence1)
    bagOfWordsB = stop_word_stemming_(sentence2)

    if len(bagOfWordsA)==0 and len(bagOfWordsB)==0:
        return 1
    else:
        uniqueWords = set(bagOfWordsA).union(set(bagOfWordsB))
        numOfWordsA = dict.fromkeys(uniqueWords, 0)
        for word in bagOfWordsA:
            numOfWordsA[word] += 1

        numOfWordsB = dict.fromkeys(uniqueWords, 0)
        for word in bagOfWordsB:
            numOfWordsB[word] += 1

        tfA = computeTF(numOfWordsA, bagOfWordsA)
        tfB = computeTF(numOfWordsB, bagOfWordsB)

        tfA_ls = []
        for value in tfA.values():
            tfA_ls.append(value)

        tfB_ls = []
        for value in tfB.values():
            tfB_ls.append(value)

        # define two lists or array
        A = np.array(tfA_ls)
        B = np.array(tfB_ls)

        # compute cosine similarity
        cosine = np.dot(A, B) / (norm(A) * norm(B))
        return cosine

# Cosine similarity of sentence uisng TF-iDF
def similarity_tfidf(df):
    if str(sentence1)=="nan" or str(sentence2)=="nan":
        return 0

    bagOfWordsA = stop_word_stemming_(sentence1)
    bagOfWordsB = stop_word_stemming_(sentence2)

    if len(bagOfWordsA)==0 and len(bagOfWordsB)==0:
        return 1
    else:
        uniqueWords = set(bagOfWordsA).union(set(bagOfWordsB))
        numOfWordsA = dict.fromkeys(uniqueWords, 0)
        for word in bagOfWordsA:
            numOfWordsA[word] += 1

        numOfWordsB = dict.fromkeys(uniqueWords, 0)
        for word in bagOfWordsB:
            numOfWordsB[word] += 1

        tfA = computeTF(numOfWordsA, bagOfWordsA)
        tfB = computeTF(numOfWordsB, bagOfWordsB)

        tfA_ls = []
        for value in tfA.values():
            tfA_ls.append(value)

        tfB_ls = []
        for value in tfB.values():
            tfB_ls.append(value)

        # define two lists or array
        A = np.array(tfA_ls)
        B = np.array(tfB_ls)

        # compute cosine similarity
        cosine = np.dot(A, B) / (norm(A) * norm(B))
        return cosine


def calculate_scores(training_df):
    """
    Calculate the scores for each feature defined below.

     features = ['DESIGN_SCORE','EXPERIMENT_SCORE','ORGANISM_SCORE','SUMMARY_SCORE','MATCH']

    :return:
    """
    training_df['DESIGN_SCORE'] = training_df.apply(lambda row: similarity(row['design_x'],row['design_y']), axis=1)
    training_df['EXPERIMENT_SCORE'] = training_df.apply(lambda row: similarity_exp(row['experiment_x'], row['experiment_y']), axis=1)
    training_df['ORGANISM_SCORE'] = training_df.apply(lambda row: similarity_organism(row['organism_x'],row['organism_y']), axis=1)
    training_df['SUMMARY_SCORE'] = training_df.apply(lambda row: similarity(row['summary_x'], row['summary_y']), axis=1)
    training_df['TITLE_SCORE'] = training_df.apply(lambda row: similarity(row['title_x'], row['title_y']), axis=1)
    training_df['OVERALL_SCORE'] = training_df.loc[:, ["DESIGN_SCORE", "EXPERIMENT_SCORE",
                                                       "ORGANISM_SCORE",'SUMMARY_SCORE','TITLE_SCORE']].mean(axis=1)

    training_scores_df = training_df
    return training_scores_df




def score(GSEID1,GSEID2,item_similarity_df):
    try:
        sim_result = item_similarity_df[(item_similarity_df['GSEID_x'] == GSEID1) & (item_similarity_df['GSEID_y'] == GSEID2)]
        return sim_result['OVERALL_SCORE'].values[0]
    except:
        sim_result = item_similarity_df[(item_similarity_df['GSEID_x'] == GSEID2) & (item_similarity_df['GSEID_y'] == GSEID1)]
        return sim_result['OVERALL_SCORE'].values[0]


#Generate item_item Matrix
def item_item(item_similarity_df):
    #Retrieve list of GSEID
    ls1=item_similarity_df['GSEID_x'].tolist()
    ls2=item_similarity_df['GSEID_y'].tolist()
    ls3=ls1+ls2
    GSEID_ls=list(dict.fromkeys(ls3))
    #Generate Item_Item matrix
    gse_dic={"GSEID":GSEID_ls}
    for i in gse_dic['GSEID']:
        gse_dic[i]=""
    matrix=pd.DataFrame(gse_dic)

    nrow=matrix.shape[0]
    ncol=matrix.shape[1]

    for n in range(nrow):
        GSEID1= matrix.loc[n,"GSEID"]
        for i in range(1,ncol):
            GSEID2=matrix.columns[i]
            if GSEID1!=GSEID2:
                matrix.iloc[n,i]=score(GSEID1,GSEID2,item_similarity_df)
            elif GSEID1==GSEID2:
                matrix.iloc[n,i] = 1

    # matrix.to_csv("item_item_matrix_sql.csv")
    return matrix

# Generate a series_similarity table with similariy scores between series
def similarity_tbl_sql(db="recom_sys.db"):
    df=ie.pair_sql(db)
    pd.set_option('display.max_columns', None)
    ts_df=calculate_scores(df)
    ts_df_final=ts_df[["GSEID_x","GSEID_y","DESIGN_SCORE", "EXPERIMENT_SCORE","ORGANISM_SCORE",'SUMMARY_SCORE','TITLE_SCORE','OVERALL_SCORE']]

    conn = sqlite3.connect(db)
    cur=conn.cursor()
    series_similarity = """ CREATE TABLE series_similarity (
                GSEID_x VARCHAR(100) NOT NULL,
                GSEID_y VARCHAR(100) NOT NULL,
                DESIGN_SCORE FLOAT(5,4),
                EXPERIMENT_SCORE FLOAT(5,4),
                ORGANISM_SCORE FLOAT(5,4),
                SUMMARY_SCORE FLOAT(5,4),
                TITLE_SCORE FLOAT(5,4),
                OVERALL_SCORE FLOAT(5,4),
                PRIMARY KEY (GSEID_x, GSEID_y)
            ); """
    cur.execute("DROP TABLE IF EXISTS series_similarity")
    cur.execute(series_similarity)
    conn.commit()
    ts_df_final.to_sql(name="series_similarity", con=conn,if_exists='replace', index=False)

    conn.commit()
    cur.close()
    conn.close()




#Top 5 recommendation for single item
def recommendation_single(GSEID):
    item_sim_matrix=pd.read_csv("item_item_matrix.csv")
    item_sim_matrix = pd.read_csv("item_item_matrix_sql.csv")
    recommendation_set=item_sim_matrix[['GSEID',GSEID]]
    recommendation_set=recommendation_set.sort_values(by=[GSEID], ascending=False)
    top_5=recommendation_set[1:6]
    return top_5


#Top 5 recommendation for multiple item
def recommendation_multiple(GSEID_ls):
    len_ls=len(GSEID_ls)
    item_sim_matrix = pd.read_csv("item_item_matrix.csv")
    recommendation_set = item_sim_matrix[['GSEID']+GSEID_ls]
    recommendation_set_new=recommendation_set.copy()
    recommendation_set_new['MAX_SCORE']=recommendation_set.max(axis=1,numeric_only=True)
    recommendation_set_new=recommendation_set_new.sort_values(by=["MAX_SCORE"], ascending=False)
    top_5=recommendation_set_new[len_ls:len_ls+5]
    return top_5



#Recommendation for multiple item over specific threshold
def recommendation_multiple_w_threshold(GSEID_ls,threshold):
    len_ls=len(GSEID_ls)
    item_sim_matrix = pd.read_csv("item_item_matrix.csv")
    recommendation_set = item_sim_matrix[['GSEID']+GSEID_ls]
    recommendation_set_new=recommendation_set.copy()
    # Add Feature "MAX_SCORE"
    recommendation_set_new['MAX_SCORE']=recommendation_set.max(axis=1,numeric_only=True)
    #Change Index to be GSEID
    recommendation_set_new.set_index("GSEID", inplace=True)
    filtered_rows = recommendation_set_new.drop(index=GSEID_ls)
    filtered_rows = filtered_rows[filtered_rows["MAX_SCORE"]>threshold]
    return filtered_rows


## Import from mySQL
def recommendation_multiple_w_threshold_sql(df,threshold=0.5):

    series_ls=df['series_id']
    series_str=str(tuple(series_ls))
    conn = sqlite3.connect("recom_sys.db")

    #SQL Command
    sql_com = f""" 
        select GSEID_y AS series_id,max(OVERALL_SCORE) 
        FROM series_similarity
        WHERE GSEID_x IN {series_str}
        AND GSEID_y NOT IN {series_str}
        GROUP BY GSEID_y
        HAVING max(OVERALL_SCORE)>{threshold}
        ORDER BY max(OVERALL_SCORE) DESC
        LIMIT 5;"""

    recom_df = pd.read_sql(sql_com, conn)
    conn.close()
    return recom_df



def row_rec(row):
    if row['COUNT']==1:
        for key,value in row.items():
            if value==1:
                z=key
                break
        row_rec=recommendation_single(z)['GSEID']
        row_rec_top1=row_rec.tolist()[0]
        return row_rec_top1

    else:
        row_ls=[]
        for key,value in row.items():
            if value==1:
                row_ls.append(key)
        row_rec=recommendation_multiple(row_ls)['GSEID']
        row_rec_ls=row_rec.tolist()
        row_rec_top1=row_rec_ls[0]
        return row_rec_top1


#Generate prediciton matrix
def predict_user_item_matrix():
    ui = pd.read_csv('user_item_matrix_gseid.csv')
    ui = ui.drop("Unnamed: 0",axis=1)
    ui_pred = ui.copy()

    for column in ui_pred.iloc[:,1:].columns:
        ui_pred[f"pred_{column}"]=0

    ui['COUNT'] = ui.loc[:, ui.columns != "name"].apply(lambda x: x.sum(), axis=1)

    nrow=ui.shape[0]


    rec_dict = {}
    for i in range(nrow):
        row=ui.loc[i, ui.columns != "name"]
        recom=row_rec(row)
        rec_dict[ui.loc[i,'name']]=recom

    ui_pred.set_index("name", inplace=True)
    for key,value in rec_dict.items():
        ui_pred.loc[key,f"pred_{value}"]=1

    ui_pred.to_csv("item_pred.csv")



def main():
    training_df=pd.read_csv('item_info_cross_match.csv')
    item_info_sim_matrix = calculate_scores(training_df)
    item_info_sim_matrix.to_csv("Item_Info_Cross_Match_Similarity.csv")
    item_sim_matrix=item_item(item_info_sim_matrix)
    predict_user_item_matrix()

# main()