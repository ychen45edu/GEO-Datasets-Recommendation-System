import pandas as pd
import numpy as np
from numpy.linalg import norm
import math
import pandas as pd
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

#Reduce/stemming and remove stop words without "other"
def stop_word_stemming_no_other(sentence):
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
    stop_words.remove("other")

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
    """
    Calculate the Term Frequency (TF) for words in a given document/bag of words.

    Parameters:
    ----------
    wordDict : dict
        A dictionary mapping each vocabulary word to its raw occurrence count in the text.
    bagOfWords : list
        The list of stemmed/tokenized words present in the document.

    Returns:
    -------
    dict
        A dictionary mapping each word to its normalized term frequency (count / total_words).
    """
    tfDict = {}
    bagOfWordsCount = len(bagOfWords)
    for word, count in wordDict.items():
        tfDict[word] = count / float(bagOfWordsCount)
    return tfDict


# Cosine similarity of sentence
def similarity(sentence1, sentence2):
    """
    Calculate the cosine similarity between two general text strings using Term Frequency vectors.

    Workflow:
    1. Checks for missing/null string inputs ('nan').
    2. Tokenizes, stems, and filters English stopwords via `stop_word_stemming_`.
    3. Handles empty input edge cases (returns 1 if both empty).
    4. Constructs a shared vocabulary and term-frequency (TF) vectors for both sentences.
    5. Computes and returns the cosine similarity between the two vectors.

    Parameters:
    ----------
    sentence1 : str or float
        The first text string (or NaN).
    sentence2 : str or float
        The second text string (or NaN).

    Returns:
    -------
    float
        Cosine similarity score ranging from 0.0 to 1.0.
    """
    if str(sentence1) == "nan" or str(sentence2) == "nan":
        return 0

    bagOfWordsA = stop_word_stemming_(sentence1)
    bagOfWordsB = stop_word_stemming_(sentence2)

    if len(bagOfWordsA) == 0 and len(bagOfWordsB) == 0:
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


def similarity_organism(organism1, organism2):
    """
    Determine exact match similarity between two organism names.

    Normalizes both organism names to lowercase and tests for exact equality.

    Parameters:
    ----------
    organism1 : str
        Name of the first organism.
    organism2 : str
        Name of the second organism.

    Returns:
    -------
    int
        1 if both organism names match case-insensitively, otherwise 0.
    """
    sentence1_lower = organism1.lower()
    sentence2_lower = organism2.lower()
    if sentence1_lower == sentence2_lower:
        return 1
    return 0


def similarity_exp(exp1, exp2):
    """
    Calculate the cosine similarity between two experiment descriptions with specialized filtering.

    Workflow:
    1. Checks for missing/null string inputs ('nan').
    2. Filters words using `stop_word_stemming_no_other` (retaining the word "other").
    3. Excludes domain-specific boilerplate terms: ['expression', 'profiling', 'by'].
    4. Handles edge cases for empty bags of words (returns 1 if both empty, 0 if only one is empty).
    5. Constructs a shared vocabulary and term-frequency (TF) vectors.
    6. Computes and returns the cosine similarity between the two experiment descriptions.

    Parameters:
    ----------
    exp1 : str or float
        The first experiment description text (or NaN).
    exp2 : str or float
        The second experiment description text (or NaN).

    Returns:
    -------
    float
        Cosine similarity score ranging from 0.0 to 1.0.
    """
    if str(exp1) == "nan" or str(exp2) == "nan":
        return 0

    # Remove addition stop words for experiment type.
    add_stop_ls = ["expression", 'profiling', 'by']

    bagOfWordsA_old = stop_word_stemming_no_other(exp1)
    bagOfWordsA = []

    for i in range(len(bagOfWordsA_old)):
        if bagOfWordsA_old[i] not in add_stop_ls:
            bagOfWordsA.append(bagOfWordsA_old[i])

    bagOfWordsB_old = stop_word_stemming_no_other(exp2)
    bagOfWordsB = []

    for i in range(len(bagOfWordsB_old)):
        if bagOfWordsB_old[i] not in add_stop_ls:
            bagOfWordsB.append(bagOfWordsB_old[i])

    if len(bagOfWordsA) == 0 and len(bagOfWordsB) == 0:
        return 1
    elif len(bagOfWordsA) == 0 or len(bagOfWordsB) == 0:
        return 0
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


