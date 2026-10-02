import pandas as pd
from fuzzywuzzy import fuzz
import requests
from bs4 import BeautifulSoup
import time


"""
Input: series table from https://www.ncbi.nlm.nih.gov/geo/browse/?view=series&display=20&sort=submitter
Output: list where pmid associate with author who are having at least 9 GEO dataset 
"""

def unique_pmid(csv="C:/Users/GC/Desktop/series_test.csv"):
    df=pd.read_csv(csv, dtype=str)
    df = df.dropna(subset=["PubMed ID"])

    df2=df.copy()
    df=df.groupby('Contact').size().reset_index(name='Count')

    rslt_df = df[df['Count'] > 8]
    rslt_ls=rslt_df["Contact"].tolist()

    t_f = df2['Contact'].isin(rslt_ls)
    df2=df2[t_f]

    df2.rename(columns={'PubMed ID': 'PubMed_ID'}, inplace=True)
    pubmed_ls = df2["PubMed_ID"].tolist()

    new=[]
    remove=[]
    for i in pubmed_ls:
        if ";" in i:
            split_ls=i.split(";")
            for id in split_ls:
                new.append(id)
            remove.append(i)

    final=[item for item in pubmed_ls if item not in remove and ".0" not in item]+new
    final=list(set(final))
    return final

# list where gseid associate with author who are having at least 9 GEO dataset
def unique_gse(csv="C:/Users/GC/Desktop/series_test.csv"):
    df=pd.read_csv(csv, dtype=str)
    df = df.dropna(subset=["PubMed ID"])

    df2=df.copy()
    df=df.groupby('Contact').size().reset_index(name='Count')

    rslt_df = df[df['Count'] > 8]
    rslt_ls=rslt_df["Contact"].tolist()

    t_f = df2['Contact'].isin(rslt_ls)
    df2=df2[t_f]

    gse_ls = df2["Accession"].tolist()
    return gse_ls


# Dictionary for GSEID : Contact Author
def g_c_dic(csv="C:/Users/GC/Desktop/series_test.csv"):
    df=pd.read_csv(csv, dtype=str)
    gseid_contact_dict = dict(zip(df.Accession, df.Contact))
    return  gseid_contact_dict


# Export csv file for each contact author

def decomposed_contact(csv="C:/Users/GC/Desktop/series_test.csv"):
    df=pd.read_csv(csv)
    df=df.dropna(subset=["PubMed ID"])

    df2=df.copy()
    df=df.groupby('Contact').size().reset_index(name='Count')

    rslt_df = df[df['Count'] > 8]
    rslt_ls=rslt_df["Contact"].tolist()

    t_f = df2['Contact'].isin(rslt_ls) #return true or false for contact name associate with >9 publication/series
    df2=df2[t_f]

    df2 = df2[~df2['PubMed ID'].str.contains(";")]
    contact_ls = list(set(df2["Contact"].tolist()))

    path="D:/UTH Drive/OneDrive - The University of Texas Health Science Center at Houston/Dr Cao Research/Code/env3/venv/pubmed_classification/contact_author_csv/"

    for i in contact_ls:
        df=df2.loc[df2['Contact'] == i]
        file_name=f'{path}{i}.csv'
        df.to_csv(file_name, index=False)

# Create dictionary for gseid : pmid
def series_ls_w_contact(csv="C:/Users/GC/Desktop/series_test.csv",filter=0):
    df=pd.read_csv(csv, dtype=str)
    df = df.fillna('')

    if filter ==1:
        df = df.dropna(subset=["PubMed ID"])
        df2=df.copy()
        df=df.groupby('Contact').size().reset_index(name='Count')
        rslt_df = df[df['Count'] > 8]
        rslt_ls=rslt_df["Contact"].tolist()
        t_f = df2['Contact'].isin(rslt_ls)
        df2=df2[t_f]
    else:
        df2 = df.copy()

    df2.rename(columns={'PubMed ID': 'PubMed_ID'}, inplace=True)
    gse_pmid_dict = dict(zip(df2.Accession, df2.PubMed_ID))

    # Split PMID into list for those GSEIDs with more than one PMID
    for i in gse_pmid_dict:
        if ";" in str(gse_pmid_dict[i]):
            gse_pmid_dict[i]=gse_pmid_dict[i].split(";")

    for k, v in gse_pmid_dict.items():
        if "." in str(v):
            gse_pmid_dict[k] = v.replace(".0", "")
    return gse_pmid_dict


# If similarity score between series table contact name and publication author name >0.69, return 1,otherwise 0
def contact_match(p_c_dic,pmid,author_name):
    pmid=int(pmid)
    pmid = str(pmid)
    s_r= fuzz.ratio(p_c_dic[pmid], author_name) / 100
    if s_r>0.69:
        return 1
    return 0


# Return the contact author name bases on highest similarity score among author list
def contact_author_name(author_name,author_list):
    highest_sc=0
    contact_author=''
    for name in author_list:
        s_c= fuzz.ratio(author_name, name) / 100
        if s_c>highest_sc and s_c >0.69:
            highest_sc=s_c
            contact_author=name
    return contact_author

def gse_error_check(gse_id):
    path = "D:/UTH Drive/OneDrive - The University of Texas Health Science Center at Houston/Dr Cao Research/Code/env3/venv/pubmed_classification/gse_html/"
    with open(f"{path}{gse_id}.txt", encoding="utf-8") as fp:
        soup_gse = BeautifulSoup(fp, 'html.parser')
    try:
        title=soup_gse.find_all("title")[0].get_text()
        # Return 1 if Server problem cause download unsuccessful
        if "Gateway" in title or "Error" in title:
            return 1
    except:
        return 1
    return 0

# import os
# directory="D:/UTH Drive/OneDrive - The University of Texas Health Science Center at Houston/Dr Cao Research/Code/env3/venv/pubmed_classification/gse_html/"
# files = os.listdir(directory)
# # length=len(files)
# # count=0
# # print(length)
# # for i in files:
# #
# #     if gse_error_check(i.replace(".txt",""))==1:
# #         print(i)
# #     count+=1
# #     if count % 10000 ==0:
# #         print(f"{count}/{length}")
#
#
# csv="C:/Users/GC/Desktop/series_sep25.csv"
# dic = series_ls_w_contact(csv, 0)
# for i in files:
#     if i.replace(".txt","") not in dic:
#         print(i)




def pmid_error_check(pmid):
    path = "D:/UTH Drive/OneDrive - The University of Texas Health Science Center at Houston/Dr Cao Research/Code/env3/venv/pubmed_classification/pub_html/"
    with open(f"{path}{pmid}.txt", encoding="utf-8") as fp:
        soup_pmid = BeautifulSoup(fp, 'html.parser')
    title=soup_pmid.find_all("title")[0].get_text()
    # Return 1 if Server problem cause download unsuccessful
    if "Error" in str(title) or "error" in str(title):
        return 1
    else:
        return 0



def gse_html_download(gse_id):
    path="D:/UTH Drive/OneDrive - The University of Texas Health Science Center at Houston/Dr Cao Research/Code/env3/venv/pubmed_classification/gse_html/"
    f = open(f"{path}{gse_id}.txt", "w",encoding='utf-8')
    html_txt=requests.get(url=f"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={gse_id}").text
    f.write(html_txt)
    f.close()
    error=gse_error_check(gse_id)
    # if error ==1:
    #     gse_html_download(gse_id)


def pmid_html_download(pmid):
    import requests
    from bs4 import BeautifulSoup
    path="D:/UTH Drive/OneDrive - The University of Texas Health Science Center at Houston/Dr Cao Research/Code/env3/venv/pubmed_classification/pub_html/"
    f = open(f"{path}{pmid}.txt", "w",encoding='utf-8')
    html_txt=requests.get(url=f"https://pubmed.ncbi.nlm.nih.gov/?term={pmid}").text
    f.write(html_txt)
    f.close()
    error = pmid_error_check(pmid)
    # if error==1:
    #     pmid_html_download(pmid)

def check_pmid_file_exist(pmid):
    import os
    file_path=fr"D:\UTH Drive\OneDrive - The University of Texas Health Science Center at Houston\Dr Cao Research\Code\env3\venv\pubmed_classification\pub_html\{pmid}.txt"
    if os.path.exists(file_path):
        return 1
    else:
        return 0

def check_gse_file_exist(gse):
    import os
    file_path=fr"D:\UTH Drive\OneDrive - The University of Texas Health Science Center at Houston\Dr Cao Research\Code\env3\venv\pubmed_classification\gse_html\{gse}.txt"
    if os.path.exists(file_path):
        return 1
    else:
        return 0


def download_gse_pmid(csv="C:/Users/GC/Desktop/series_sep25.csv"):
    dic = series_ls_w_contact(csv, 0)
    length=len(dic)
    count=0
    for i, k in dic.items():
        print(f"{count}/{length}")
        print(i)
        print(check_gse_file_exist(i))
        if check_gse_file_exist(i)==0 or gse_error_check(i)==1:
            try:
                gse_html_download(i)
            except:
                time.sleep(300)
                gse_html_download(i)
        if type(k) == list:
            for j in k:
                if check_pmid_file_exist(j) == 0 or pmid_error_check(j)==1:
                    print(check_pmid_file_exist(j))
                    print(j)
                    try:
                        pmid_html_download(j)
                    except:
                        time.sleep(300)
                        pmid_html_download(j)
        elif k != "" and (check_pmid_file_exist(k) == 0 or pmid_error_check(k)==1):
            print(check_pmid_file_exist(k))
            print(k)
            try:
                pmid_html_download(k)
            except:
                time.sleep(300)
                pmid_html_download(k)
        count+=1
# download_gse_pmid()

# return file list
def file_exist(directory = "D:/UTH Drive/OneDrive - The University of Texas Health Science Center at Houston/Dr Cao Research/Code/env3/venv/pubmed_classification/pub_html"):
    import os
    files = os.listdir(directory)
    ls=[]
    print("Files in directory:")
    for file in files:
        file=file.replace(".txt","")
        ls.append(file)
    return ls



def gse_validation_chk(directory = "D:/UTH Drive/OneDrive - The University of Texas Health Science Center at Houston/Dr Cao Research/Code/env3/venv/pubmed_classification/gse_html/"):
    import os
    from bs4 import BeautifulSoup
    import requests
    import Item_Extraction_Local as iel
    files = os.listdir(directory)
    directory_contents = [os.path.splitext(f)[0] for f in files]
    for i in files:
        with open(f"{directory}{i}", encoding="utf-8") as fp:
            soup_gse = BeautifulSoup(fp, 'html.parser')
        try:
            sum = iel.summary(soup_gse)
            if len(sum) < 2:
                print(i)
        except:
            print(f"{i} has error")
# gse_validation_chk()

def pmid_validation_chk(directory = "D:/UTH Drive/OneDrive - The University of Texas Health Science Center at Houston/Dr Cao Research/Code/env3/venv/pubmed_classification/pub_html/"):
    import os
    from bs4 import BeautifulSoup
    import requests
    import Author_Extraction_Local as ae
    files = os.listdir(directory)
    directory_contents = [os.path.splitext(f)[0] for f in files]
    for i in files:
        with open(f"{directory}{i}", encoding="utf-8") as fp:
            soup_pm = BeautifulSoup(fp, 'html.parser')
        try:
            ae.affiliation(soup_pm,0)
        except:
            print(f"{i} has error")

# pmid_validation_chk()